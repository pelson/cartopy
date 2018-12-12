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


def scale_for_units(units, value):
    if units == 'miles':
        value = value * 1609.34
    elif units == 'meters':
        value = value
    else:
        raise RuntimeError('unknown units')
    return value

#: The number of meters in the given unit.
_UNIT_SCALEFACTOR = {'miles': 1609.34,
                     'meters': 1,
                     'killometers': 1000,
                     'km': 1000,
                     }
_UNIT_ALIASES = {'miles': ['mi'],
                 'meters': ['m'],
                 'killometers': ['km']}

_UNIT_SYMBOLS = {'miles': 'mi',
                 'killometers': 'km',
                 'meters': 'm'}

class _Unit(object):
    #: The number of meters in the given unit.
    SCALEFACTORS = {'mi': 1609.34,
                    'm': 1,
                    'km': 1000,}
    _UNITS_TO_ALIASES = {'km': ['killometers'],
               'm': ['meters'],
               'mi': ['miles']}
    ALIASES = {alias: unit
               for unit, aliases in _UNITS_TO_ALIASES.items()
               for alias in aliases
               }

    # A really light-weight immutable unit interface.
    def __init__(self, unit):
        self.orig = unit
        unit = self.ALIASES.get(unit, unit)
        if unit not in self.SCALEFACTORS:
            raise ValueError('Unknown unit {}'.format(unit))

        self.unit = unit
        self.scale_factor = self.SCALEFACTORS[unit]

    def to_meters(self, values):
        return values * self.scale_factor

    def from_meters(self, values):
        return values / self.scale_factor
        
    @property
    def full_name(self):
        return self._UNITS_TO_ALIASES.get(self.unit, [self.unit])[0]


class ScaleBarArtist(matplotlib.artist.Artist):
    def __init__(self, location=(0.5, 0.075), max_width=0.3,
                 line_kwargs=None, border_kwargs=None, text_kwargs=None, units='km'):

        #: The position of the scalebar in Axes coordinates.
        self.location = np.array(location)

        #: The maximum width, in Axes coordinate, of the scalebar.
        self.max_width = max_width

        self.line_kwargs = line_kwargs or dict()
        self.border_kwargs = border_kwargs or dict(color='black', path_effects=[path_effects.withStroke(linewidth=3, foreground='black')])
        self.text_kwargs = text_kwargs or dict(color='white', path_effects=[path_effects.withStroke(linewidth=3, foreground='black')])
        self.zorder = 50

        self.units = _Unit(units)

        super(ScaleBarArtist, self).__init__()

    def line_stylization(self, step_index, steps):
        """
        Given the step we are to draw, and a list of all
        other steps that are going to be drawn, return a
        style dictionary that can be merged with self.line_kwargs.
        """
        if step_index % 2:
            return {'color': 'white'}
        else:
            return {'color': 'black'}

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return
        for artist in self.scalebar_artists():
            artist.draw(renderer)

    def scalebar_artists(self, linewidth=3, units='km'):
        ax = self.axes
        ax_to_data = ax.transAxes - ax.transData

        alignment = 'center'

        # if alignment == 'center':
        center = ax_to_data.transform_point(self.location)
        p0 = self.location - [self.max_width / 2, 0]
        p1 = self.location + [self.max_width / 2, 0]
        # elif alignment ...

        p0 = ax_to_data.transform_point(p0)
        p1 = ax_to_data.transform_point(p1)

        # Calculate maximum line length in meters on the ground (MOG).
        npts = 40
        def line_length(start_point, end_point):
            xs = np.linspace(start_point[0], end_point[0], npts)
            ys = np.linspace(start_point[1], end_point[1], npts)
            points_ll = ccrs.Geodetic().transform_points(self.axes.projection, xs, ys)[:, :2].T
            return line_len(points_ll)

        max_line_length_m = line_length(p0, p1)
        max_line_length = self.units.from_meters(max_line_length_m) 

        self.locator = matplotlib.ticker.MaxNLocator(4)

        # Compute the tick marks.
        ticks = self.locator.tick_values(0, max_line_length)

        # Only allow ticks that are within the allowed range.
        ticks = ticks[np.logical_and(ticks >= 0, ticks <= max_line_length)]

        ticks_m = self.units.to_meters(ticks)

        # The scalebar length is now the maximum tick value.
        scalebar_len = ticks.max()

        scalebar_len_m = ticks_m.max()

        # We now know what ticks we are going to draw, but we need to figure
        # out where these locations are in projected space. For center alignment
        # things get tricky because we can't guarantee that the length-scale on
        # the RHS of a center point is the same as the length-scale on the LHS, so we iterate a little.

        if alignment == 'center':
            # Iterate the center point until we get a good approximation for a balanced start point

            # Start by assuming that the start of the colorbar should be placed at p0.
            # Compute the center location based on that assumption. Now iteratively move the start
            # location closer to the desired center based on whether the projected end is 
            min_start = p0
            max_start = forward(self.axes.projection, p1, p0, distance=scalebar_len_m)

            # Compute the start value.
            start = (min_start[0] + max_start[0]) / 2, (min_start[1] + max_start[1]) / 2

            start_range = max([line_length(start, min_start), line_length(start, max_start)])
            # line_length(max_start, min_start)

            def center_dist(start):
                end = forward(self.axes.projection, start, p1, distance=scalebar_len_m)
                new_center = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
                return line_length(new_center, center)

            target = scalebar_len_m / 1e6

            for i in range(50):
                distance_adjustment = start_range / 2**(i)

                distance_adjustment = center_dist(start)

                if distance_adjustment < target:
                    break

                # Move the start by the given distance adjustment. Choose the direction that reduces the distance from the desired center.
                choice0 = forward(self.axes.projection, start, p0, distance=distance_adjustment)
                choice1 = forward(self.axes.projection, start, p1, distance=distance_adjustment)

                if center_dist(choice0) < center_dist(choice1):
                    start = choice0
                else:
                    start = choice1

            lines, outline = self.scale_lines(ticks_m, start, p1)
            xs, ys = outline
            xs = np.array(xs)
            ys = np.array(ys)

        elif alignment == 'start':
            start = p0
            lines, outline = self.scale_lines(ticks_m, p0, p1)
            xs, ys = outline
            xs = np.array(xs)
            ys = np.array(ys)

        outline = self.bar_outline(xs, ys)
        if outline:
            lines.insert(0, outline)

        t = self.scale_text(xs, ys, scalebar_len)
        if t:
            lines.append(t)

        return lines

    def scale_lines(self, steps, start, extreme_end):
        lines = []
        line_start = start

        x = [start[0]]
        y = [start[1]]
        for i, distance in enumerate(np.diff(steps)):
            line_end = forward(self.axes.projection, line_start, extreme_end, distance)

            x.append(line_end[0])
            y.append(line_end[1])
            line_style = self.line_stylization(i, steps)
            #import cartopy.mpl.style as cms
            #style = cms.merge(line_style, self.line_kwargs)
            # Don't use cms.merge here because that assumed PathCollections, not lines.
            line_style.update(self.line_kwargs)
            style = line_style

            xs = np.array([start[0], extreme_end[0]])
            ys = np.array([start[1], extreme_end[1]])
            line = mlines.Line2D(
                [line_start[0], line_end[0]], [line_start[1], line_end[1]],
                transform=self.axes.transData, **style)
            line.axes = self.axes
            lines.append(line)

            line_start = line_end
        return lines, [x, y]

    def bar_outline(self, xs, ys):
        # Put a nice border around the scalebar.
        border = mlines.Line2D(
                xs, ys, transform=self.axes.transData, **self.border_kwargs)
        border.axes = self.axes
        return border

    def scale_text(self, xs, ys, bar_length):
        length = bar_length
        units = self.units.orig

        if length.is_integer():
            length = int(length)

        import matplotlib.transforms as transforms
        # shift the object down 4 points
        dx, dy = 0 / 72., -4 / 72.
        offset = transforms.ScaledTranslation(dx, dy,
                                              self.figure.dpi_scale_trans)
        shadow_transform = self.axes.transData + offset

        t = mtext.Text(xs.mean(), ys.mean(),
                       '{0} {1}'.format(length, units), transform=self.axes.transData + offset,
                       horizontalalignment='center', verticalalignment='top', **self.text_kwargs)
        t.axes = self.axes
        t.figure = self.figure
        return t



class ScaleLineArtist(ScaleBarArtist):
    def scale_lines(self, steps, start, extreme_end):
        lines = []
        line_start = start

        x = [start[0]]
        y = [start[1]]
        marker_locs = [start]

        for i, distance in enumerate(np.diff(steps)):
            line_end = forward(self.axes.projection, line_start, extreme_end, distance)

            marker_locs.append(line_end)

            x.append(line_end[0])
            y.append(line_end[1])
            line_style = self.line_stylization(i, steps)
            #import cartopy.mpl.style as cms
            #style = cms.merge(line_style, self.line_kwargs)
            # Don't use cms.merge here because that assumed PathCollections, not lines.
            line_style.update(self.line_kwargs)
            style = line_style

            xs = np.array([start[0], extreme_end[0]])
            ys = np.array([start[1], extreme_end[1]])
            height = 1000
            style = {'marker': '|', 'markersize': 10, 'markeredgewidth': 1, 'color': 'black', 'linestyle': 'solid'}
            line = mlines.Line2D(
                [line_end[0], line_end[0]], [line_end[1] - height, line_end[1] + height],
                transform=self.axes.transData, **style)
            line.axes = self.axes

            lines.append(line)

            line_start = line_end

        xs, ys = zip(*marker_locs)
        line = mlines.Line2D(xs, ys, transform=self.axes.transData, **style)
        lines = [line]

        return lines, [x, y]

    def line_stylization(self, step_index, steps):
        return {'color': 'black'}

    def bar_outline(self, *args, **kwargs):
        return None


def line_len(line):
    """
    Determine the physical line length. The units are determined by this function.

    Line is in lons/lats


    >>> line_len(np.array([[0, 1], [1, 0]))
    123

    """
    import cartopy.geodesic
    geod = cartopy.geodesic.Geodesic()
    return geod.geometry_length(line.T)


def forward(projection, start_point, extreme_end_point, distance, tol=0.000001, npts=20, maxcount=100):
    """
    Return the end point of a straight line in the given projection, starting from
    start_point and extending in the extreme_end_point direction until the line has the given distance.

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
            'of length {} from {} in the extreme_end_point direction of this projection.'
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



