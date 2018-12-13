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

import math
import sys

import cartopy.geodesic
import cartopy.crs as ccrs
import numpy as np

import matplotlib.lines as mlines
import matplotlib.text as mtext
import matplotlib.patheffects as path_effects


class _Unit(object):
    #: The number of meters in the given unit.
    SCALEFACTORS = {'mi': 1609.34,
                    'm': 1,
                    'km': 1000,}
    _UNITS_TO_ALIASES = {'km': ['killometers'],
               'm': ['meters'],
               'mi': ['miles']}

    #: A mapping of unit_alias to canonical_unit_name.
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


def round_sig_fig(number, sig_figs=7):
    y = abs(number)

    # If it is nearly zero, return zero.
    if y <= sys.float_info.min:
        result = 0.0
    else:
        result = round(number, int(sig_figs - math.ceil(math.log10(y)) ) )
    return result


class _GenericScaleBarArtist(matplotlib.artist.Artist):
    def __init__(self, location=(0.5, 0.075), max_width=0.3,
                 line_kwargs=None, border_kwargs=None, text_kwargs=None, units='km',
                 tick_text_y_offset=-6, alignment='center'):

        #: The position of the scalebar in Axes coordinates.
        self.location = np.array(location)

        #: The maximum width, in Axes coordinate, of the scalebar.
        self.max_width = max_width

        self.line_kwargs = line_kwargs or dict()
        self.border_kwargs = border_kwargs or dict(color='black', path_effects=[path_effects.withStroke(linewidth=3, foreground='black')])
        self.text_kwargs = text_kwargs or dict(color='white', path_effects=[path_effects.withStroke(linewidth=3, foreground='black')])
        self.zorder = 50

        #: The offset of the tick text. If None, no tick text to be drawn.
        #: If negative, text is below the ticks. If positive, above.
        self.tick_text_y_offset = tick_text_y_offset
        self.alignment = alignment

        self.units = _Unit(units)

        #: The matplotlib locator responsible for finding the scalebar ticks.
        self.tick_locator = matplotlib.ticker.MaxNLocator(5)

        #: The ticks that are used for the scalebar (computed)
        #: in the desired units.
        self._ticks = tuple()

        #: The x and y locations of the ticks (computed)
        #: in the projected coordinate system.
        self._marker_locations = tuple()

        #: The total of this scalebar (computed) in
        #: the desired units.
        self._scalebar_length = 0.0

        super(_GenericScaleBarArtist, self).__init__()
    
    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return
        for artist in self.scalebar_artists():
            artist.draw(renderer)

    def update_scalebar_properties(self):
        """
        Compute and update the properties that will be required to
        subsequently construct scalebar artists.

        """
        ax = self.axes
        ax_to_data = ax.transAxes - ax.transData

        if self.alignment == 'center':
            center = ax_to_data.transform_point(self.location)
            p0 = self.location - [self.max_width / 2, 0]
            p1 = self.location + [self.max_width / 2, 0]
        elif self.alignment in 'left':
            p0 = self.location
            p1 = p0 + [self.max_width, 0]
        elif self.alignment == 'right':
            p1 = self.location
            p0 = p1 - [self.max_width, 0]
        else:
            raise ValueError('Unknown alignment {}'.format(self.alignment))
        p0 = ax_to_data.transform_point(p0)
        p1 = ax_to_data.transform_point(p1)

        # Calculate maximum line length in meters on the ground (MOG).
        max_line_length_m = segment_length(ax.projection, p0, p1)
        max_line_length = self.units.from_meters(max_line_length_m) 

        # Compute the tick marks.
        ticks = self.tick_locator.tick_values(0, max_line_length)

        # Only allow ticks that are within the allowed range.
        ticks = ticks[np.logical_and(ticks >= 0, ticks <= max_line_length)]
        self._ticks = ticks

        ticks_m = self.units.to_meters(ticks)

        # The scalebar length is now the maximum tick value.
        scalebar_len = ticks.max()
        self._scalebar_length = scalebar_len

        scalebar_len_m = ticks_m.max()

        # We now know what ticks we are going to draw, but we need to figure
        # out where these locations are in projected space. For center alignment
        # things get tricky because we can't guarantee that the length-scale on
        # the RHS of a center point is the same as the length-scale on the LHS, so we iterate a little.

        if self.alignment == 'center':
            # Iterate the center point until we get a good approximation for a balanced start point

            # Start by assuming that the start of the colorbar should be placed at p0.
            # Compute the center location based on that assumption. Now iteratively move the start
            # location closer to the desired center based on whether the projected end is 
            min_start = p0
            max_start = forward(self.axes.projection, p1, p0, distance=scalebar_len_m)

            # Compute the start value.
            start = (min_start[0] + max_start[0]) / 2, (min_start[1] + max_start[1]) / 2

            start_range = max([segment_length(ax.projection, start, min_start),
                               segment_length(ax.projection, start, max_start)])

            def center_dist(start):
                end = forward(ax.projection, start, p1, distance=scalebar_len_m)
                new_center = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
                return segment_length(ax.projection, new_center, center)

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

        elif self.alignment == 'left':
            start = p0
        elif self.alignment == 'right':
            start = p1
            p1 = p0

        line_start = start
        marker_locs = [line_start]
        for i, distance in enumerate(np.diff(self._ticks)):
            distance_m = self.units.to_meters(distance)
            line_end = forward(self.axes.projection, line_start, p1, distance_m)
            marker_locs.append(line_end)
            line_start = line_end

        self._marker_locations = tuple(marker_locs)

    def scalebar_artists(self, linewidth=3, units='km'):
        self.update_scalebar_properties()

        artists = []

        ticks_m = self.units.to_meters(self._ticks)
        start = self._marker_locations[0]
        p1 = self._marker_locations[1]

        outline = self.bar_outline()
        if outline:
            artists.append(outline)

        artists.extend(self.scale_lines() or [])
        artists.extend(self.tick_texts() or [])

        text = self.scale_text() 
        if text:
            artists.append(text)

        return artists

    def scale_lines(self, steps, start, extreme_end):
        return None

    def tick_texts(self):
        return None

    def bar_outline(self):
        xs, ys = zip(*self._marker_locations)
        # Put a nice border around the scalebar.
        border = mlines.Line2D(
                xs, ys, transform=self.axes.transData, **self.border_kwargs)
        border.axes = self.axes
        return border

    def scale_text(self):
        xs, ys = zip(*self._marker_locations)
        bar_length = self._scalebar_length
        length = bar_length
        units = self.units.orig

        xs, ys = zip(*self._marker_locations)
        xs = np.array(xs)
        ys = np.array(ys)

        # 7 significant figures is enough precision for everything.
        length = round_sig_fig(length, 7)

        if length.is_integer():
            length = int(length)

        # shift the object down 6 points
        offset = self.tick_text_y_offset

        if offset is None:
            return
        if offset > 0:
            verticalalignment = 'bottom'
        else:
            verticalalignment = 'top'
        dx, dy = 0, offset / 72.

        import matplotlib.transforms as transforms
        offset = transforms.ScaledTranslation(dx, dy,
                                              self.figure.dpi_scale_trans)
        shadow_transform = self.axes.transData + offset

        t = mtext.Text(xs.mean(), ys.mean(),
                       '{0} {1}'.format(length, units), transform=self.axes.transData + offset,
                       horizontalalignment='center', verticalalignment=verticalalignment, **self.text_kwargs)
        t.axes = self.axes
        t.figure = self.figure
        return t

    def tick_texts(self):
        xs, ys = zip(*self._marker_locations)
        ticks = self._ticks
        ticks = self.units.to_meters(ticks)

        units = self.units.orig
        texts = []
        for x, y, tick in zip(xs, ys, ticks):
            length = tick

            length = self.units.from_meters(length)

            # 7 significant figures is enough precision for everything.
            length = round_sig_fig(length, 7)

            if length.is_integer():
                length = int(length)

#            if length == 0:
#                continue
            import matplotlib.transforms as transforms
            # shift the object down 6 points
            offset = self.tick_text_y_offset

            if offset is None:
                return
            if offset > 0:
                verticalalignment = 'bottom'
            else:
                verticalalignment = 'top'
            dx, dy = 0, offset / 72.
            offset = transforms.ScaledTranslation(dx, dy,
                                                  self.figure.dpi_scale_trans)
            shadow_transform = self.axes.transData + offset
            t = mtext.Text(x, y,
                           '{0}'.format(length, units), transform=self.axes.transData + offset,
                           horizontalalignment='center', verticalalignment=verticalalignment, **self.text_kwargs)
            t.axes = self.axes
            t.figure = self.figure
            texts.append(t)

        # Only show the units on the last text and ensure the number is center
        # aligned by padding it with spaces on the RHS.
        units_padding = ' ' * (len(str(units)) + 2)
        t.set_text('{pad}{length} {units}'.format(
            pad=units_padding, length=length, units=units))

        return texts


class ScaleBarArtist(_GenericScaleBarArtist):
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

    def scale_lines(self):
        lines = []
        steps = self.units.to_meters(self._ticks)
        start = self._marker_locations[0]
        extreme_end = self._marker_locations[-1]

        line_start = start
        for i, distance in enumerate(np.diff(steps)):
            line_style = self.line_stylization(i, steps)
            #import cartopy.mpl.style as cms
            #style = cms.merge(line_style, self.line_kwargs)
            # Don't use cms.merge here because that assumed PathCollections, not lines.
            line_style.update(self.line_kwargs)
            style = line_style

            line = [self._marker_locations[i], self._marker_locations[i+1]]
            xs, ys = zip(*line)
            line = mlines.Line2D(
                xs, ys,
                transform=self.axes.transData, **style)
            line.axes = self.axes
            lines.append(line)
        return lines

    def tick_texts(self):
        return None


class ScaleLineArtist(_GenericScaleBarArtist):
    def scale_lines(self):
        lines = []
        start = self._marker_locations[0]
        line_start = start

        x = [start[0]]
        y = [start[1]]
        marker_locs = [start]
        style = self.line_kwargs
        style = {'marker': '|', 'markersize': abs(self.tick_text_y_offset or 5) - 2, 'markeredgewidth': 1, 'color': 'black', 'linestyle': 'solid'}

        style.update(dict(solid_capstyle='butt'))

        offset = self.tick_text_y_offset

        if offset is None:
            return
        import matplotlib.markers
        if offset > 0:
            verticalalignment = 'bottom'
            style['marker'] = matplotlib.markers.TICKUP
        else:
            verticalalignment = 'top'
            style['marker'] = matplotlib.markers.TICKDOWN
        dx, dy = 0, offset / 72.

        xs, ys = zip(*self._marker_locations)
        line = mlines.Line2D(xs, ys, transform=self.axes.transData, **style)
        lines = [line]

        return lines

    def line_stylization(self, step_index, steps):
        return {'color': 'black'}

    def bar_outline(self, *args, **kwargs):
        return None

    def scale_text(self):
        return None


def segment_length(projection, start_point, end_point, npts=50):
    """
    Determine the physical length of the given line segment.

    Parameters
    ----------
    projection : cartopy.crs.Projection
        The projection of the line to measure.
    start_point : coordinate pair
        The location of the begining of the projected line in projected
        coordinates.
    end_point : coordinate pair
        The location of the end of the projected line in projected
        coordinates.
    npts : integer
        The number of samples to take along the line to approximate
        the length in projected space.

    Returns
    -------
    length : float
        The length of the line formed by the given vertices in physical meters
        on the ground.

    Examples
    --------
    >>> import cartopy.crs as ccrs
    >>> round(segment_length(ccrs.PlateCarree(), [0, 1], [50, 100])
    156900.0

    """
    xs = np.linspace(start_point[0], end_point[0], npts)
    ys = np.linspace(start_point[1], end_point[1], npts)
    points_ll = ccrs.PlateCarree().transform_points(projection, xs, ys)[:, :2]
    geod = cartopy.geodesic.Geodesic()
    return geod.geometry_length(points_ll)


def forward(projection, start_point, extreme_end_point, distance,
            tol=0.000001, npts=20, maxiter=100):
    """
    Return the end point of a straight line of the given length in the
    given projection.

    Parameters
    ----------
    projection : cartopy.crs.Projection
        The projection in which to find the point ``distance`` away
        from ``p1`` in the ``p1`` direction.
    p0 : coordinate pair
        The projected coordinate of the starting point of the desired line.
    p1_direction: coordinate pair
        A point, in projected coordinates, that should be used to determine
        the direction of the desired line. ``p1_direction`` must be at least
        ``distance`` away from ``p0``.
    distance : number
        The distance, in physical meters, of the desired line.
    tol : float
        The convergence condition of this binary search algorithm, where
        iteration breaks once
        ``(abs(len_of_solution - target_length) / target_length) < tol``
        is satisfied.
    npts : int
        The number of samples to take when projecting the line into geodetic
        coordinates (passed through to ``segment_length``).
    maxiter : int, optional
        The maximum number of iterations allowed. If the number of iterations
        exceeds this value, a ValueError will be raised.

    Returns
    -------
    p1 : coordinate pair
        The location, in projected coordinates which is approximately
        ``distance`` from ``p0`` in the direction of ``p1_direction``.

    """
    start = start_point
    end = extreme_end_point

    max_len = segment_length(projection, start, end, npts=npts)
    if distance < 0:
        raise ValueError('Cannot project a line backwards (distance < 0).')
    if max_len < distance:
        raise ValueError(
            'The distance between p0 and p1 is less than the '
            'distance of the desired location from p0.')
    # Binary search of this line to get to the desired tolerance.
    current_length = max_len
    end_min = start
    end_max = end

    count = 0
    while np.abs(current_length - distance) / distance > tol:
        midpoint = [(end_min[0] + end_max[0]) * 0.5,
                    (end_min[1] + end_max[1]) * 0.5]
        current_length = segment_length(projection, start, midpoint)
        if current_length < distance:
            end_min = midpoint
        else:
            end_max = midpoint
        if count < maxcount:
            count += 1
        else:
            raise ValueError('Unable to iterate to sufficient accuracy.')
    return midpoint
