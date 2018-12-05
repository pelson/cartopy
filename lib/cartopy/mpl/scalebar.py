# (C) British Crown Copyright 2018, Met Office
#
# This file is part of cartopy.
#
# cartopy is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cartopy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cartopy.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)

import matplotlib.artist


import pytest
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.lines as mlines
import matplotlib.text as mtext
import matplotlib.patheffects as path_effects


def DEBUG(msg):
    #print(msg)
    pass


class ScaleBarArtist(matplotlib.artist.Artist):
    def __init__(self, location=(0.5, 0.075), width_range=(0.15, 0.3)):

        #: The position of the scalebar in Axes coordinates.
        self.location = np.array(location)

        #: The valid range of widths, in Axes coordinates, of the
        #: scalebar.
        self.width_range = width_range

        super(ScaleBarArtist, self).__init__()

    @matplotlib.artist.allow_rasterization
    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return
        for artist in self.scale_bar_artists():
            artist.draw(renderer)

    def scale_bar_artists(self, linewidth=3, units='km'):
        ax = self.axes
        ax_to_data = ax.transAxes - ax.transData
        center = ax_to_data.transform_point(self.location)
        p0 = self.location + [self.width_range[0] / 2, 0]
        p1 = self.location + [self.width_range[1] / 2, 0]
        w0 = (ax_to_data.transform_point(p0)[0] - center[0]) * 2
        w1 = (ax_to_data.transform_point(p1)[0] - center[0]) * 2
        line_gen = center_align_line_generator(center[0], center[1], w0, w1, self.axes.projection)
        r = pick_best_scale_length(line_gen)
        if r is None:
            return []
        line_start_stop = r[2]
        xs = np.array([line_start_stop[0][0], line_start_stop[1][0]])
        ys = np.array([line_start_stop[0][1], line_start_stop[1][1]])

        steps = r[1]
        start, extreme_end = line_start_stop[0], [line_start_stop[1][0] + 0.1 * (self.axes.projection.x_limits[1] - self.axes.projection.x_limits[0]), line_start_stop[1][1]]
        lines = []
        line_start = start
        for i, distance in enumerate(np.diff(steps)):
            line_end = forward(self.axes.projection, line_start, extreme_end, distance)

            xs = np.array([line_start_stop[0][0], line_start_stop[1][0]])
            ys = np.array([line_start_stop[0][1], line_start_stop[1][1]])
            line = mlines.Line2D(
                [line_start[0], line_end[0]], [line_start[1], line_end[1]],
                color='black' if i % 2 == 0 else 'white',
                transform=self.axes.transData)
            line.axes = self.axes
            lines.append(line)

            line_start = line_end

        line = mlines.Line2D(
            xs, ys,
            color='black',
            transform=self.axes.transData, path_effects=[path_effects.withStroke(linewidth=3, foreground='black')])
        line.axes = self.axes
        lines.insert(0, line)

        length = r[0]
        units = 'm'
        if length > 1000 and units == 'm':
            length /= 1000
            units = 'km'

        import matplotlib.transforms as transforms
        # shift the object down 4 points
        dx, dy = 0 / 72., -4 / 72.
        offset = transforms.ScaledTranslation(dx, dy,
                                              self.figure.dpi_scale_trans)
        shadow_transform = ax.transData + offset

        t = mtext.Text(xs.sum() / 2, ys.sum() / 2,
                       '{0} {1}'.format(length, units), transform=self.axes.transData + offset,
                       horizontalalignment='center', verticalalignment='top', color='white')
        t.set_path_effects([path_effects.withStroke(linewidth=3, foreground='black')])
        t.axes = self.axes
        t.figure = self.figure

        return lines + [t]


def determine_target_length(shortest, longest, allowed_n_ticks=(3, 4, 5)):
    """
    Given a range of lengths, choose a nice length to aim for and the ticks that we would choose.

    >>> determine_target_length(7, 9)
    [9.0, [0.0, 3.0, 6.0, 9.0]]
    >>> determine_target_length(7, 8.9)
    [8.8, [0.0, 2.2, 4.4, 6.6, 8.8]]
    >>> determine_target_length(8.1, 8.8)
    [8.8, [0.0, 2.2, 4.4, 6.6, 8.8]]
    >>> determine_target_length(101, 151)
    [150.0, [0.0, 50.0, 100.0, 150.0]]

    """
    if longest <= shortest:
        raise ValueError('shortest length must be shorter than longest.')

    n_digits = np.floor(np.log10(longest - shortest))

    # The scale needed to bring the range down to [1-10) range.
    range_scale = 10 ** (n_digits - 1)

    # Scale the input values.
    longest = longest / range_scale
    shortest = shortest / range_scale

    candidates = []
    for n_ticks_target in allowed_n_ticks:
        step = (longest / 10) // n_ticks_target * 10
        step = longest // n_ticks_target
        scale_step = step * range_scale
        resulting_length = step * n_ticks_target
        if resulting_length > shortest:
            # Round to the 5 dp after the appropriate scale factor.
            candidates.append(
                [resulting_length * range_scale,
                 list(np.around(np.arange(0, resulting_length * range_scale + scale_step/2, scale_step), decimals=-int(n_digits) + 5)),
                 longest - resulting_length])
    if not candidates:
        raise ValueError(
            'Cannot select a sensible step size. Please raise an '
            'issue with details of the range (shortest={}, longest={}).'
            ''.format(shortest, longest))
    distance = lambda candidate: candidate[2]
    best = min(candidates, key=distance)

    return best[:2]


def center_align_line_generator(x_center, y, min_x_width, max_x_width, projection):
    """
    This implementation's strategy is to align the line center, taking equal parts off the line on both sides.

#    >>> import cartopy.crs as ccrs
#    >>> gen = center_align_line_generator(0, 0, 30000, 40000, ccrs.Mercator())
##    >>> next(gen)
#    >>> next(gen)
#    >>> next(gen)

    """
    # Infinite generator of lines, doing a binary search for some external
    # criteria (e.g. as done in pick_best_scale_length)

    lon_lat = ccrs.Geodetic()
    steps = 4

    ys = np.full(steps, y)
    min_xs = np.linspace(-0.5, 0.5, steps) * min_x_width + x_center
    line_lon_lat = lon_lat.transform_points(projection, min_xs, ys).T[:2]
    yield [[min_xs.min(), y], [min_xs.max(), y]], line_lon_lat

    max_xs = np.linspace(-0.5, 0.5, steps) * max_x_width + x_center
    line_lon_lat = lon_lat.transform_points(projection, max_xs, ys).T[:2]
    yield [[max_xs.min(), y], [max_xs.max(), y]], line_lon_lat

    search_space = [min_x_width, max_x_width]

    while True:
        DEBUG('Search space: {}'.format(search_space))
        # Split the search space in half.
        next_split = (search_space[1] - search_space[0]) / 2 + search_space[0]

        xs = np.linspace(-0.5, 0.5, steps) * next_split + x_center
        line_lon_lat = lon_lat.transform_points(projection, xs, ys).T[:2]
        left_is_good = yield ([[xs.min(), y], [xs.max(), y]], line_lon_lat)

        if left_is_good:
            DEBUG('Bring in the rhs')
            yield 'OK'
            search_space[1] = next_split
        else:
            DEBUG('Bring in the lhs')
            yield 'OK'
            search_space[0] = next_split


def line_len(line):
    """
    Determine the physical line length. The units are determined by this function.

    Line is in lons/lats
    """
    import cartopy.geodesic
    geod = cartopy.geodesic.Geodesic()
    return geod.geometry_length(line.T)



def pick_best_scale_length(line_gen):
    """
    Given the possible Axes coordinates that could be used to represent a scalebar,
    return the best choice and its length (rounded to a nice form).

    Can return None if there is no possible scale for the given line. This occurs when
    the line would be out of range of projection.

    """
    # Get the extreme lengths (first 2 lines)
    # This will give us the range of lines that are available to us.
    # Pick the line that we will ultimately go for.
    # Iterate until we get close to that line.

    _, shortest_line = next(line_gen)
    _, longest_line = next(line_gen)

    if np.isnan(line_len(longest_line)) or np.isnan(line_len(shortest_line)):
        return None
    target_length, step = determine_target_length(
        line_len(shortest_line), line_len(longest_line)
    )

    DEBUG('Target: {}; lhs: {}; rhs: {};'.format(target_length, line_len(shortest_line), line_len(longest_line)))
    for iteration, r in enumerate(line_gen):
        # Avoid infinite loops
        if iteration > 50:
            raise RuntimeError('Unable to determine a sensible length. Target: {}; now: {};'.format(target_length, length))
        line_start_stop, line = r
        length = line_len(line)
        DEBUG('Target: {}; now: {};'.format(target_length, length))
        if length < target_length:
            line_gen.send(False)
            lh_len = length
        else:
            line_gen.send(True)
            rh_len = length
        # Iterate until we have an accuracy of 6 significant figures.
        if np.abs(length - target_length) / target_length < 0.000001:
            break

    # TODO: Remove the line itself?
    return target_length, step, line_start_stop, line


def forward(projection, start_point, extreme_end_point, distance, tol=0.000001, npts=20, maxcount=100):
    """
    Return the end point of a straight line in the given projection, starting from
    start_point and extending in the x direction until the line has the given distance.

    This is an iterative solution which will terminate once the length reaches ``(abs(len - target) / target) < tol``.
    """
    start = start_point
    end = extreme_end_point

    def line_length(start_point, end_point):
        xs = np.linspace(start_point[0], end_point[0], npts)
        ys = np.linspace(start_point[1], end_point[1], npts)
        points_ll = ccrs.PlateCarree().transform_points(projection, xs, ys)[:, :2].T
        return line_len(points_ll)
    max_len = line_length(start, end)
    if max_len < distance:
        raise ValueError(
            'It is not possible to construct a straight line '
            'of length {} from {} in the x direction of this projection.'
            ''.format(distance, start_point))
    # Binary search of this line to get to the desired tolerance.
    current_length = max_len
    end_min = start
    end_max = end

    count = 0
    while np.abs(current_length - distance) / distance > tol:
        midpoint = (end_min[0] + end_max[0]) * 0.5, (end_min[1] + end_max[1]) * 0.5
        current_length = line_length(start, midpoint)
        if current_length < distance:
            end_min = midpoint
        else:
            end_max = midpoint
        if count < maxcount:
            count += 1
        else:
            raise ValueError('Unable to iterate to sufficient accuracy.')
    return midpoint



