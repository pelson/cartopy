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

"""
Handles matplotlib styling in a single consistent place.

"""
import warnings

import six

import matplotlib.artist
import matplotlib.patches
import matplotlib.lines


# Define the matplotlib style aliases that cartopy can expand.
# Note: This should not contain the plural aliases
# (e.g. linewidths -> linewidth).
# This is an intended duplication of
# https://github.com/matplotlib/matplotlib/blob/\
#   2d2dab511d22b6cc9c812cfbcca6df3f9bf3094a/lib/matplotlib/patches.py#L20-L26
# Duplication intended to simplify readability, given the small number of
# aliases.
_ALIASES = {
    'lw': 'linewidth',
    'ls': 'linestyle',
    'fc': 'facecolor',
    'ec': 'edgecolor',
}


class StyleProxy(object):
    def __init__(self, style=None, callbacks=None):
        self._style = style or {}
        self._callbacks = callbacks or []

    def update_style(self, other_style):
        # Note this is not using merge() as we are only managing a
        # single style dictionary. merge() is exclusively for when we
        # need to blend multiple levels of style definition.
        # HOWEVER: It would be good to get aliases... e.g. self.style['lw'] = 1; self.style['linewidth'] == 1
        self._style.update(other_style)

    def apply(self, artist, context=None):
        if self.style:
            matplotlib.artist.setp(artist, **self.style)
        for callback in self._callbacks:
            callback(artist, context=context)

    # TODO: Choose which one.
    update = update_style
    @property
    def style(self):
        # NOTE: users still need to call finalize.
        return self._style.copy()

    def __getitem__(self, key):
        return self._style[key]

    def __setitem__(self, key, value):
        return self._style.__setitem__(key, value)

    def get(self, key, default=None):
        return self._style.get(key, default)

    def __iter__(self):
        return iter(self._style)
    
    @staticmethod
    def _attach_artist_methods(klass, proxying_klass):
        """
        Put setters and getters that one would expect from a matplotlib
        artist on the given class.

        Parameters
        ----------
        klass : type
            The class on which to add the matplotlib-like methods.
        proxying_klass : klass
            The matplotlib artist type that is being proxied.

        """
        # Define a function that can produce our getters and setters.
        # This has the added advantage of being a closure over the prop
        # which will simplify our subsequent for-loop.
        def _attach_setters_and_getters(klass, prop):
            getter_name = 'get_{}'.format(prop)
            # Attach a getter for the prop.
            def getter_meth(self):
                return self._style.get(prop)
            setattr(klass, getter_name, getter_meth)

            setter_name = 'set_{}'.format(prop)
            def setter_meth(self, v):
                return self._style.__setitem__(prop, v)
            setattr(klass, setter_name, setter_meth)

        # Use the standard matplotlib machinery to find out what we should be setting
        # for a PathCollection.
        _inspector = matplotlib.artist.ArtistInspector(
            proxying_klass)

        # Attach the actual set_* and get_* methods.
        for _prop in _inspector.get_setters():
            _attach_setters_and_getters(klass, _prop)


class PatchProxy(StyleProxy):
    pass


class Line2DProxy(StyleProxy):
    pass


StyleProxy._attach_artist_methods(PatchProxy, matplotlib.patches.Patch)
StyleProxy._attach_artist_methods(Line2DProxy, matplotlib.lines.Line2D)


def merge(*style_dicts):
    """
    Merge together multiple matplotlib style dictionaries in a predictable way

    The approach taken is:

        For each style:
            * Expand aliases, such as "lw" -> "linewidth", but always prefer
              the full form if over-specified (i.e. lw AND linewidth
              are both set)
            * "color" overwrites "facecolor" and "edgecolor" (as per
              matplotlib), UNLESS facecolor == "never", which will be expanded
              at finalization to 'none'

    >>> style = merge({"lw": 1, "edgecolor": "black", "facecolor": "never"},
    ...               {"linewidth": 2, "color": "gray"})
    >>> sorted(style.items())
    [('edgecolor', 'gray'), ('facecolor', 'never'), ('linewidth', 2)]

    """
    style = {}
    facecolor = None

    for orig_style in style_dicts:
        this_style = orig_style.copy()

        for alias_from, alias_to in _ALIASES.items():
            alias = this_style.pop(alias_from, None)
            if alias_from in orig_style:
                # n.b. alias_from doesn't trump alias_to
                # (e.g. 'lw' doesn't trump 'linewidth').
                this_style.setdefault(alias_to, alias)

        color = this_style.pop('color', None)
        if 'color' in orig_style:
            this_style['edgecolor'] = color
            this_style['facecolor'] = color

        if isinstance(facecolor, six.string_types) and facecolor == 'never':
            requested_color = this_style.pop('facecolor', None)
            setting_color = not (isinstance(requested_color, six.string_types)
                                 and requested_color.lower() == 'none')
            if (('fc' in orig_style or 'facecolor' in orig_style) and
                    setting_color):
                warnings.warn('facecolor will have no effect as it has been '
                              'defined as "never".')
        else:
            facecolor = this_style.get('facecolor', facecolor)

        # Push the remainder of the style into the merged style.
        style.update(this_style)

    return style


def finalize(style):
    """
    Update the given matplotlib style according to cartopy's style rules.

    Rules:

        1. A facecolor of 'never' is replaced with 'none'.

    """
    # Expand 'never' to 'none' if we have it.
    facecolor = style.get('facecolor', None)
    if facecolor == 'never':
        style['facecolor'] = 'none'
    return style



