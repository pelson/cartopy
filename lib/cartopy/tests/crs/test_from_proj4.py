# (C) British Crown Copyright 2011 - 2012, Met Office
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
from nose.tools import assert_raises_regexp, assert_true

import cartopy.crs as ccrs


@mock.patch('cartopy._proj4.LOGGER')
def test_unhandled_units(logger):
    # The unit isn't handled by LambertConformal, so we use that to check our
    # error handling and logging.
    msg = ("No projection can currently handle this combination "
           "of proj4 parameters.\nRequired parameters: secant_latitudes, "
           "units, central_longitude, central_latitude for the projection "
           "lcc")
    with assert_raises_regexp(ValueError, msg):
        ccrs.from_proj4('+proj=lcc +lat_1=-14 +lat_0=-14 '
                        '+lon_0=170 +k_0=1 +units=us-ft +no_defs')

    calls = [mock.call("Starting with parameters:\n\t[['central_latitude', "
                       "-14], ['secant_latitudes', (-14, None)], "
                       "['central_longitude', 170], ['scale_factor', 1], "
                       "['units', 'us-ft']]"),
             mock.call(" Value (us-ft) of units not aligned with "
                       "unparameterised m. Could not remove it as a default "
                       "value.")]
    logger.info.assert_has_calls(calls)


@mock.patch('cartopy._proj4.LOGGER')
def test_unhandled_projection(logger):
    msg = ("No cartopy Projection class can currently "
           "handle the proj4 'doesntexist' projection.")
    with assert_raises_regexp(ValueError, msg):
        ccrs.from_proj4('+proj=doesntexist +no_defs')

    call = mock.call("Found 0 potential class(es): []")
    logger.info.assert_has_calls([call])


@mock.patch('cartopy._proj4.LOGGER')
def test_no_proj(logger):
    msg = ("No projection found in the Proj4 string.")
    with assert_raises_regexp(ValueError, msg):
        ccrs.from_proj4('+no_defs')

    # No log messages needed - the error should suffice.    
    assert_true(not logger.info.called)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-s', '--with-doctest'], exit=False)
