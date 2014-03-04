# (C) British Crown Copyright 2011 - 2014, Met Office
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

import inspect
import logging


# Setup the logging to the "cartopy._proj4" logger. Create a handler for
# the logger if there hasn't already been one defined (perhaps in by the
# cartopy config) for example. 
LOGGER = logging.getLogger(__name__)
if LOGGER.level == logging.NOTSET:
    LOGGER.setLevel(logging.WARN)
if not LOGGER.handlers:
    LOGGER.addHandler(logging.StreamHandler())


def from_proj4(proj4_str):
    from cartopy._crs import CRS, Globe
    import inspect

    def all_subclasses(cls):
        return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                       for g in all_subclasses(s)]

    params = _proj4_str_to_params(proj4_str)
    for param in params[:]:
        if param[0] == 'proj':
            proj = param[1]
            params.remove(param)
            break
    else:
        raise ValueError('No projection found in the Proj4 string.')

    potentials = []
    for cls in all_subclasses(CRS):
        if getattr(cls, '_proj4_proj', None) == proj:
            potentials.append(cls)
    
    LOGGER.info('Found {} potential class(es): {}'.format(len(potentials),
                                                          potentials))
    
    if not potentials:
        raise ValueError('No cartopy Projection class can currently '
                         'handle the proj4 {!r} projection.'.format(proj))
    
    globe_params = Globe.from_proj4_params(params)
    for projection in potentials[::-1]:
        prj_kwargs = inspect.getargspec(projection.__init__).args[1:]

        LOGGER.info('Trying class {}'.format(projection))

        these_params, processeds = projection._proj4_params_to_cartopy(params[:])

        LOGGER.info('Starting with parameters:\n\t{}'.format(these_params))

        _remove_unparameterised(projection, these_params, processeds)

        LOGGER.info('After removing unparameterised values which correspond '
                    'to the existing default:\n\t{}'.format(these_params))

        unprocesseds = set([param[0] for param, processed in
                            zip(params, processeds) if not processed])

        # If it isn't the default value, but it is allowed, then consider the value processed.
        if unprocesseds - set(prj_kwargs):
            LOGGER.info('Class {} was rejected as there remain unprocessed '
                        'parameters: {}'.format(projection,
                                                ', '.join(unprocesseds)))
            continue

        # Tidy up by removing the arguments which aren't doing
        # anything (because they are already the default).
        _remove_default_params(projection, these_params)
        if projection._default_globe_repr != Globe.compute_repr(globe_params):
            LOGGER.info('Adding globe {}'.format(Globe.compute_repr(globe_params)))
            these_params.append(['globe', eval(Globe.compute_repr(globe_params))])
            processeds.append(True)

        unacceptable_kwargs = set(dict(these_params).keys()) - set(prj_kwargs)
        if unacceptable_kwargs:
            LOGGER.info('Class {} was rejected as there are keywords which '
                        'are not acceptable: {}'.format(projection,
                                                        ', '.join(unacceptable_kwargs)))
            continue
        else:
            crs = projection(**dict(these_params))

        actual = sorted(_proj4_str_to_params(crs.proj4_init))
        expected = sorted(_proj4_str_to_params(proj4_str))
        
        # Turn any non string values into floats for both: 
        actual = [[k, v if isinstance(v, basestring) else float(v)] for k, v in actual]
        expected = [[k, v if isinstance(v, basestring) else float(v)] for k, v in actual]
        if actual == expected:
            break
        else:
            LOGGER.info("Class {} was constructed but the underlying proj4 "
                        "string wasn't identical:\nExpected:\t{}"
                        "\nActual:\t{}".format(projection, expected, actual))
    else:
        raise ValueError('No projection can currently handle this combination of proj4 parameters.\n' 
                         'Required parameters: {} for the projection {}. Original proj4 string:\n{}'
                         ''.format(', '.join(dict(these_params).keys()), proj, proj4_str))
    return crs


def _proj4_str_to_params(proj4_string):
    """
    Turns a string into a list of key value pairs (unless it
    is a single value such as +no_defs).

    """
    params = []
    for param in proj4_string.split('+'):
        param = param.strip().split('=')
        
        if not param[0] or param[0] in ['no_defs', 'wktext', 'over']:
            continue
        elif len(param) == 1:
            raise ValueError('Unhandled single value proj4 parameter '
                             '{!r}.'.format(param[0]))

        name, value = param
        cast_value = value

        # Try to maintain the type of the value provided in the proj4 string,
        # so attempt to cast to an int first to see if that was how it was given to us.
        # TODO: This needs to consider epsilons for floats.
        cast_attempts = [int, float]
        for caster in cast_attempts:
            try:
                if str(caster(value)) == value: 
                    cast_value = caster(value)
                    break
            except (ValueError, TypeError):
                continue

        param[1] = cast_value

        params.append(param)
    return params


def _remove_unparameterised(cls, params, processeds):
    for param in params[:]:
        if param[0] in cls._proj4_unparameterised:
            fixed_value = cls._proj4_unparameterised[param[0]]
            # a value of None means that it isn't handled.
            if fixed_value is None:
                continue
            
            # Floats may have done a rountrip from float(str(float))
            # conversion, so be generous when comparing them.
            if isinstance(param[1], float):
                abs_tol = abs(fixed_value - param[1])
                is_equal = abs_tol < 1e-7
            else:
                is_equal = fixed_value == param[1]

            if is_equal:
                index = params.index(param)
                processeds.pop(index)
                params.pop(index)
            else:
                LOGGER.info(' Value ({}) of {} not aligned with '
                            'unparameterised {}. Could not remove it as a '
                            'default value.'.format(param[1], param[0],
                                                    fixed_value))
    return params, processeds


def _remove_default_params(cls, params):
    """
    Given a list of parameter-value pairs, remove any parameters which are
    provided as a default value as computed by inspecting the `__init__` method
    of the given class.

    """
    argspec = inspect.getargspec(cls.__init__)
    defaults = dict(zip(argspec.args[1:],
                        argspec.defaults or []))

    for name, value in params[:]:
        if defaults.get(name) == value:
            params.remove([name, value])
        elif name == 'globe' and value == cls._default_globe_repr:
            params.remove([name, value])


def _compute_unparam(parent_cls, init_defaults, kwargs_passed_to_super):
    parent = parent_cls
    try:
        inherited_unparam = parent._proj4_unparameterised.copy()
    except AttributeError:
        inherited_unparam = {}
    _proj4_unparameterised = inherited_unparam

    # Get the defaults from the parent class' init:
    try:
        defaults = parent._defaults()
    except AttributeError:
        defaults = {}
    
    for kwarg in kwargs_passed_to_super:
        del defaults[kwarg]

    _proj4_unparameterised.update(defaults)
    _proj4_unparameterised.update(init_defaults)
    return _proj4_unparameterised
