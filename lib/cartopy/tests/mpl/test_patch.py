# (C) British Crown Copyright 2015, Met Office
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cartopy. If not, see <http://www.gnu.org/licenses/>.
from unittest import TestCase

import matplotlib.path as mpath
import numpy as np

import cartopy.crs as ccrs
import cartopy.mpl.patch as cpatch


class Test_remove_zero_area_branch(TestCase):
    def _call_remove_bad_ends(self, x_verts, y_verts, codes):
        verts = np.vstack([x_verts, y_verts]).T
        codes = np.array(codes)
        r1 = cpatch.remove_bad_ends(verts, codes)

        verts = np.vstack([y_verts, x_verts]).T
        r2 = cpatch.remove_bad_ends(verts, codes)
        self.assertEqual(r1, r2)
        return r1

    def test_simple_case_1(self):
        r_verts = [1, 3, 2]
        c_verts = [2, 2, 2]
        codes = [1, 2, 2]
        bad_inds = self._call_remove_bad_ends(r_verts, c_verts, codes)
        self.assertEqual(bad_inds, [1])

    def test_simple_case_2(self):
        r_verts = [2, 3, 1]
        c_verts = [2] * 3
        codes = [1, 2, 2]
        bad_inds = self._call_remove_bad_ends(r_verts, c_verts, codes)
        self.assertEqual(bad_inds, [1])

    def test_simple_case_79_code(self):
        r_verts = [1, 2, 3, 1]
        c_verts = [3, 2, 2, 2]
        codes = [1, 2, 2, 79]
        r = self._call_remove_bad_ends(r_verts, c_verts, codes)
        self.assertEqual(r, [2])

    def test_simple_case_double_ended(self):
        r_verts = [3, 4, 2.5, 1, 2]
        c_verts = [2] * 5
        codes = [1, 2, 2, 2, 2]
        bad_inds = self._call_remove_bad_ends(r_verts, c_verts, codes)
        self.assertEqual(bad_inds, [1, 3])

    def test_simple_case_multiple_paths(self):
        # As before, but with an extra path.
        r_verts = [2, 3, 1, 4, 2, 2, 2, 2, 2]
        c_verts = [2, 2, 2, 3, 2, 3, 1.5, 0.5, 1]
        codes = [1, 2, 2, 2, 1, 2, 2, 2, 79]
        bad_inds = self._call_remove_bad_ends(r_verts, c_verts, codes)
        self.assertEqual(bad_inds, [1, 5, 7])

    def test_simple_case_multiple_paths_2(self):
        # As before, but with an extra path.
        r_verts = [2, 3, 4, 2, 3, 4]
        c_verts = [2, 2, 2, 2, 2, 2]
        codes = [1, 2, 2, 1, 2, 2]
        bad_inds = self._call_remove_bad_ends(r_verts, c_verts, codes)
        self.assertEqual(bad_inds, [])

    def test_simple_case_static_points(self):
        # As before, but with an extra path.
        r_verts = [2, 2, 3, 1, 1]
        c_verts = [2, 2, 2, 2, 2]
        codes = [1, 2, 2, 2, 2]
        bad_inds = self._call_remove_bad_ends(r_verts, c_verts, codes)
        self.assertEqual(bad_inds, [2, 3])

    def test_edge_and_interior_complex_case(self):
        # An "integration" type test for a real geometry which led to
        # the development of the remove_zero_area_branch code.
        # A Path which has a zero area branch sticking out. e.g.
        #   x_ _x_ _x
        #   |   |
        #   x_ _x
        # Which also has a single point separating interior from exterior:
        #   e_ _e_ _ _ _ _e
        #   | i- -i- - -i |
        #   | |        /  |
        #   | i&e - i /   |
        #   e / \ e _ _ _ e

        arr = np.array
        codes = arr(
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2,
             2, 2, 2, 2],
            dtype=np.uint8)
        verts_t = arr([
            [345.72000122, 345.76000977, 345.77799988, 345.77067057,
             345.76000977, 345.73524257, 345.72923396, 345.72000122,
             345.69999695, 345.6909041, 345.68841553, 345.72000122,
             345.72125149, 345.72625256, 345.72000122, 345.71750069,
             345.69555155, 345.68713706, 345.67999268, 345.64667765,
             345.64001465, 345.63601379, 345.64001465, 345.67706745,
             345.67999268, 345.68666077, 345.70749855, 345.7152002,
             345.70249748, 345.67999268, 345.66769174, 345.65500641,
             345.66222466, 345.67332967, 345.67999268, 345.72000122,
             345.67999268, 345.64001465, 345.6000061, 345.55999756,
             345.51998901, 345.50074033, 345.49750137, 345.50843981,
             345.50843981, 345.50893126, 345.51998901, 345.52841187,
             345.52841187, 345.51998901, 345.51739304, 345.48688221,
             345.48001099, 345.46028846, 345.48001099, 345.51998901,
             345.55999756, 345.55999756, 345.55999756, 345.51998901,
             345.48001099, 345.4711202, 345.45578046, 345.48001099,
             345.48188496, 345.51323948, 345.51763737, 345.51702768,
             345.50212649, 345.5013326, 345.5013326, 345.48750687,
             345.48889499, 345.51199341, 345.51998901, 345.55999756,
             345.57473755, 345.6000061, 345.64001465, 345.67999268,
             345.68570818, 345.69332886, 345.72000122, 345.72000122,
             345.71111043, 345.70857021, 345.72000122, 345.76000977,
             345.76000977, 345.77000427, 345.76000977, 345.72000122],
            [20.11333402, 20.11000061, 20.1400013, 20.1799984,
             20.19523684, 20.21999931, 20.26000023, 20.27714348,
             20.30000114, 20.34000206, 20.37999916, 20.41750002,
             20.42000008, 20.46000099, 20.48857307, 20.50000191,
             20.53999901, 20.57999992, 20.58666674, 20.62000084,
             20.62000084, 20.62000084, 20.61707394, 20.57999992,
             20.56666629, 20.53999901, 20.50000191, 20.46000099,
             20.42000008, 20.39230713, 20.37999916, 20.34000206,
             20.30000114, 20.26000023, 20.25200005, 20.21999931,
             20.20857048, 20.21058733, 20.21199913, 20.18285561,
             20.18533185, 20.21999931, 20.26000023, 20.30000114,
             20.34000206, 20.37999916, 20.4105881, 20.42000008,
             20.46000099, 20.47777918, 20.50000191, 20.53999901,
             20.54956444, 20.57999992, 20.62000084, 20.62000084,
             20.62000084, 20.62000084, 20.62000084, 20.62000084,
             20.62000084, 20.62000084, 20.57999992, 20.54260776,
             20.53999901, 20.50000191, 20.46000099, 20.42000008,
             20.37999916, 20.34000206, 20.30000114, 20.26000023,
             20.21999931, 20.1799984, 20.17225702, 20.17124903,
             20.1799984, 20.19919884, 20.19176337, 20.18571281,
             20.1799984, 20.1400013, 20.11333402, 20.1311122,
             20.1400013, 20.1799984, 20.21999931, 20.1799984,
             20.1799984, 20.1400013, 20.12333425, 20.1311122]])
        bad_path = mpath.Path(verts_t.T, codes)

        crs = ccrs.RotatedPole(193.0, 41.0)
        # Figure out the bad indices for this path.
        bad_inds = cpatch.remove_bad_ends(bad_path.vertices, bad_path.codes)
        # Remove them from the path.
        fixed_path = cpatch.remove_inds_from_path(bad_path, bad_inds)

        # Convert the path to a single geometry
        geom_bad, = cpatch.path_to_geos(bad_path)
        geom_good, = cpatch.path_to_geos(fixed_path)

        # The areas should be the same (~0.018) after the removal.
        self.assertEqual(geom_bad.area, geom_good.area)

        # Projecting the two geometries triggers the transformation algorithm
        # to treat the geometries differently - the non-tweaked path results
        # in a geometry which fills the globe, but our new path doesn't.
        result_bad = crs.project_geometry(geom_bad, crs)
        result_good = crs.project_geometry(geom_good, crs)

        self.assertGreater(result_bad.area, 64800)
        self.assertLess(result_good.area, 0.02)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-s', '--with-doctest'], exit=False)
