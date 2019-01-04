# (C) British Crown Copyright 2019, Met Office
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

import numpy as np
from numpy.testing import assert_array_almost_equal
import pytest
import shapely.geometry as sgeom

import cartopy.crs as ccrs


def verts_to_points(verts):
    return [{'x': v[0], 'y': v[1]} for v in verts]

def points_to_verts(points):
    return np.array([[pt['x'], pt['y']] for pt in points])


def test_project_segment():
    # IGH cuts this geodetic geometry into multiple. Assert it produces the same thing no matter the order
    verts = np.array([[-20, 45], [-60, 60]])
    ls = sgeom.LineString(verts[:2])
    ls = sgeom.LineString(verts[::-1])
    from cartopy.trace import _Testing
    
    r1 = _Testing._call_project_segment(ls, ccrs.Geodetic(), ccrs.InterruptedGoodeHomolosine())
    r2 = _Testing._call_project_segment(ls, ccrs.Geodetic(), ccrs.InterruptedGoodeHomolosine(), [verts_to_points(verts[1:])])
    print(r1)
    print(r2)
    assert len(r1) == len(r2)
    for line1, line2 in zip(r1, r2):
        print(np.round(points_to_verts(line1)))
        print(np.round(points_to_verts(line2)))
        print()
    assert r1 == r2
    assert 1 == 2

