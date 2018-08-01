from __future__ import division
import matplotlib.artist


import pytest
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.lines as mlines
import matplotlib.text as mtext

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
        line = mlines.Line2D(xs, ys, color='black', transform=self.axes.transData)
        line.axes = self.axes

        length = r[0]
        units = 'm'
        if length > 1000 and units == 'm':
            length /= 1000
            units = 'km'
        t = mtext.Text(xs.sum() / 2, ys.sum() / 2,
                       '\n{0} {1}'.format(length, units), transform=self.axes.transData,
                       horizontalalignment='center', verticalalignment='center')
        t.axes = self.axes
        t.figure = self.figure

        return [line, t]



def test_simple_range():
    r = determine_target_length(7, 9)
    assert r == [9, [0, 3, 6, 9]]

def test_float_range():
    r = determine_target_length(7, 8.9)
    # TODO: Could be a better result?
    assert r == [8.8, [0.0, 2.2, 4.4, 6.6, 8.8]]

def test_small_domain():
    r = determine_target_length(8.1, 8.8)
    assert r == [8.8, [0, 2.2, 4.4, 6.6, 8.8]]

def test_tiny_domain():
    r = determine_target_length(8.874, 8.876)
    # TODO: Could be a better result?
    assert r == [8.8758, [0.0, 2.9586, 5.9172, 8.8758]]

def test_high_domain():
    r = determine_target_length(101, 151)
    assert r == [150, [0, 50, 100, 150]]

def test_huge_domain():
    r = determine_target_length(1490005, 1500005)
    assert r == [1500000.0, [0.0, 500000.0, 1000000.0, 1500000.0]]

def test_large_range():
    r = determine_target_length(1.1, 151)
    assert r == [150, [0, 50, 100, 150]]

def test_invalid_range():
    with pytest.raises(ValueError):
        determine_target_length(10, 2)

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
    distances, azi_0, azi_1 = np.array(
        geod.inverse(line[:, 2], line[:, 1:]).T)
    print('distances:', distances, azi_1)
    return np.sum(np.abs(distances))


def test_line_len():
    line = np.array(
        [[-111.6 + 360, -105.3 + 360, -97.8 + 360],
         [  16.0,   18.7, 21.9]])
    assert 100000 < line_len(line) < 1000000


def pick_best_scale_length(line_gen):
    """
    Given the possible Axes coordinates that could be used to represent a scalebar,
    return the best choice and its length (rounded to a nice form)
    """
    # Get the extreme lengths (first 2 lines)
    # This will give us the range of lines that are available to us.
    # Pick the line that we will ultimately go for.
    # Iterate until we get close to that line.

    _, shortest_line = next(line_gen)
    _, longest_line = next(line_gen)

    print(repr(longest_line))
    if np.isnan(line_len(longest_line)) or np.isnan(line_len(shortest_line)):
        return None
    target_length, step = determine_target_length(
        line_len(shortest_line), line_len(longest_line)
    )

    DEBUG('Target: {}; lhs: {}; rhs: {};'.format(target_length, line_len(shortest_line), line_len(longest_line)))
    for iteration, r in enumerate(line_gen):
        # Avoid infinite loops
        if iteration > 20:
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
    return target_length, step, line_start_stop, line

def test_integration_of_components():
    center = [-6484360.33870819, 2878445.5153896]
    w0 = 829330.2064098883
    w1 = 2073325.51602472
    line_gen = center_align_line_generator(center[0], center[1], w0, w1, ccrs.Mercator())

    shortest = next(line_gen)
    longest = next(line_gen)
    print(shortest, line_len(shortest[1]))
    print(longest, line_len(longest[1]))
    print(next(line_gen))
    line_gen = center_align_line_generator(center[0], center[1], w0, w1, ccrs.Mercator())
    r = pick_best_scale_length(line_gen)

if __name__ == '__main__':
    ax = plt.axes(projection=ccrs.NorthPolarStereo())
    ax.set_extent([-21, -95.5, 14, 76], ccrs.Geodetic())
    ax.stock_img()
    ax.coastlines(resolution='110m')
    a = ScaleBarArtist()
    a.set_zorder(100)
    ax.add_artist(a)

    a = ScaleBarArtist(location=(0.5, 0.95))
    a.set_zorder(100)
    ax.add_artist(a)
    #    scale_bar(ax, ccrs.Mercator(), 1000)  # 100 km scale bar

    # or to use m instead of km
    # scale_bar(ax, ccrs.Mercator(), 100000, m_per_unit=1, units='m')
    # or to use miles instead of km
    # scale_bar(ax, ccrs.Mercator(), 60, m_per_unit=1609.34, units='miles')

    plt.show()
