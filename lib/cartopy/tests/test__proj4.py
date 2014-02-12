# (C) British Crown Copyright 2014, Met Office
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
# along with cartopy.  If not, see <http://www.gnu.org/licenses/>.

import mock
from nose.tools import assert_equal, assert_raises_regexp, assert_false

import cartopy.crs as ccrs
import cartopy._proj4 as p4


def test__proj4_str_to_params():
    fake_proj4_str = (' +a_string=hello-world +a-float=1.23 +an-int=-23 '
                      '+no_defs')
    result = p4._proj4_str_to_params(fake_proj4_str)
    assert_equal(result, [['a_string', 'hello-world'], ['a-float', 1.23],
                          ['an-int', -23]])
    
    # Now check that a single valued parameter which hasn't been explicitly
    # handled raises an error.
    msg = "Unhandled single value proj4 parameter 'unhandled_single_param'."
    with assert_raises_regexp(ValueError, msg):
        p4._proj4_str_to_params('+proj=latlon +unhandled_single_param')


class Test_remove_unparameterised(object):
    class SimpleProjection(ccrs.Projection):
        _proj4_unparameterised = ccrs.Projection._proj4_unparameterised.copy()
        _proj4_unparameterised.update({'a_float': 1/3.,
                                       'an_int': -43,
                                       'a string': 'the result'})
    
    def test_float_exact(self):
        params, _ = p4._remove_unparameterised(self.SimpleProjection,
                                               [['a_float', 1/3.]], [False])
        assert_equal(params, [])

    def test_float_close(self):
        params, _ = p4._remove_unparameterised(self.SimpleProjection,
                                               [['a_float', 0.3333333]],
                                               [False])
        assert_equal(params, [])
    
    @mock.patch('cartopy._proj4.LOGGER')
    def test_float_not_close_enough(self, logger):
        orig_params = [['a_float', 0.333333]]
        params, processeds = p4._remove_unparameterised(self.SimpleProjection,
                                                        orig_params, [False])
        assert_equal(params, [['a_float', 0.333333]])
        assert_equal(processeds, [False])
        logger.info.assert_called_once_with(' Value (0.333333) of a_float not '
            'aligned with unparameterised 0.333333333333. Could not remove '
            'it as a default value.')

    def test_int(self):
        # Check an int which is exactly the same as the default is removed,
        # but one that isn't, isn't.
        params, _ = p4._remove_unparameterised(self.SimpleProjection,
                                               [['an_int', -43]],
                                               [False])
        assert_equal(params, [])
        with mock.patch('cartopy._proj4.LOGGER') as logger:
            params, _ = p4._remove_unparameterised(self.SimpleProjection,
                                                   [['an_int', 43]],
                                                   [False])
        assert_equal(params, [['an_int', 43]])
        info_log_msg = (' Value (43) of an_int not aligned with '
                        'unparameterised -43. Could not remove it as a '
                        'default value.')
        logger.info.assert_called_once_with(info_log_msg)
    
    def test_str(self):
        params, _ = p4._remove_unparameterised(self.SimpleProjection,
                                               [['a string', 'the result']],
                                               [False])
        assert_equal(params, [])
        
        with mock.patch('cartopy._proj4.LOGGER') as logger:
            params, _ = p4._remove_unparameterised(self.SimpleProjection,
                                                   [['a string',
                                                     'not the result']],
                                                   [False])
        assert_equal(params, [['a string', 'not the result']])
        info_log_msg = (' Value (not the result) of a string not aligned '
                        'with unparameterised the result. Could not remove '
                        'it as a default value.')
        logger.info.assert_called_once_with(info_log_msg)


def test__remove_default_params():
    class FakeProjection(ccrs.Projection):
        def __init__(self, wibble=10):
            pass

    params = [['wibble', 10], ['another', 'wibble']]
    p4._remove_default_params(FakeProjection, params)
    assert_equal(params, [['another', 'wibble']])

    params = [['wibble', 10.1]]
    p4._remove_default_params(FakeProjection, params)
    assert_equal(params, [['wibble', 10.1]])


def test__compute_unparam():
    class GenericProjection(ccrs.Projection):
        def __init__(self, foo=10, bar='another'):
            pass
    
    class SpecificProjection(GenericProjection):
        def __init__(self, foo=20):
            pass
    
    result = p4._compute_unparam(GenericProjection, {'foo': 20}, ['bar'])
    expected = {'foo': 20, 'scale_factor': 1.0, 'units': 'm'}
    assert_equal(result, expected)

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-s', '--with-doctest'], exit=False)
