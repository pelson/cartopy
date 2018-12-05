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

import pytest
import cartopy.crs as ccrs


from cartopy.mpl.scalebar import (ScaleBarArtist, determine_target_length as determine_target_length, 
    center_align_line_generator, forward, pick_best_scale_length)

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

def test_integration_of_components():
    center = [-6484360.33870819, 2878445.5153896]
    w0 = 829330.2064098883
    w1 = 2073325.51602472
    line_gen = center_align_line_generator(center[0], center[1], w0, w1, ccrs.Mercator())

    shortest = next(line_gen)
    longest = next(line_gen)
    line_gen = center_align_line_generator(center[0], center[1], w0, w1, ccrs.Mercator())
    r = pick_best_scale_length(line_gen)

def test_forward_pc():
    start = 0, 0
    v = forward(ccrs.PlateCarree(), [-4, 50], [0, 50], 3000)
    assert v[1] == 50
    assert v[0] == pytest.approx(-3.9581565)


def test_forward_mercator():
    v = forward(ccrs.Mercator(), [0, 0], [1e6, 0], 30000, tol=0.0000001)
    assert v[0] == pytest.approx(30000)

