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
"""
Provides shapely geometry <-> matplotlib path support.


See also `Shapely Geometric Objects <see_also_shapely>`_
and `Matplotlib Path API <http://matplotlib.org/api/path_api.html>`_.

.. see_also_shapely:
   http://toblerity.github.com/shapely/manual.html#geometric-objects

"""
import numpy as np
import matplotlib.path
from matplotlib.path import Path
import shapely
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.linestring import LineString
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.multipoint import MultiPoint
from shapely.geometry.multipolygon import MultiPolygon


def geos_to_path(shape):
    """
    Creates a list of :class:`matplotlib.path.Path` objects that describe
    a shape.

    Args:

    * shape
        A list, tuple or single instance of any of the following
        types: :class:`shapely.geometry.point.Point`,
        :class:`shapely.geometry.linestring.LineString`,
        :class:`shapely.geometry.polygon.Polygon`,
        :class:`shapely.geometry.multipoint.MultiPoint`,
        :class:`shapely.geometry.multipolygon.MultiPolygon`,
        :class:`shapely.geometry.multilinestring.MultiLineString`,
        :class:`shapely.geometry.collection.GeometryCollection`,
        or any type with a _as_mpl_path() method.

    Returns:
        A list of :class:`matplotlib.path.Path` objects.

    """
    if isinstance(shape, (list, tuple)):
        paths = []
        for shp in shape:
            paths.extend(geos_to_path(shp))
        return paths

    if isinstance(shape, (LineString, Point)):
        return [Path(np.vstack(shape.xy).T)]
    elif isinstance(shape, Polygon):
        def poly_codes(poly):
            codes = np.ones(len(poly.xy[0])) * Path.LINETO
            codes[0] = Path.MOVETO
            return codes

        vertices = np.concatenate([np.array(shape.exterior.xy)] +
                                  [np.array(ring.xy) for ring in
                                   shape.interiors], 1).T
        codes = np.concatenate([poly_codes(shape.exterior)] +
                               [poly_codes(ring) for ring in shape.interiors])
        return [Path(vertices, codes)]
    elif isinstance(shape, (MultiPolygon, GeometryCollection, MultiLineString,
                            MultiPoint)):
        paths = []
        for geom in shape.geoms:
            paths.extend(geos_to_path(geom))
        return paths
    elif hasattr(shape, '_as_mpl_path'):
        vertices, codes = shape._as_mpl_path()
        return [Path(vertices, codes)]
    else:
        raise ValueError('Unsupported shape type {}.'.format(type(shape)))


def path_segments(path, transform=None, remove_nans=False, clip=None,
                  quantize=False, simplify=False, curves=False,
                  stroke_width=1.0, snap=False, sketch=None):
    """
    Creates an array of vertices and a corresponding array of codes from a
    :class:`matplotlib.path.Path`.

    Args:

    * path
        A :class:`matplotlib.path.Path` instance.

    Kwargs:
        See :func:`matplotlib.path.iter_segments` for details of the keyword
        arguments.

    Returns:
        A (vertices, codes) tuple, where vertices is a numpy array of
        coordinates, and codes is a numpy array of matplotlib path codes.
        See :class:`matplotlib.path.Path` for information on the types of
        codes and their meanings.

    """
    # XXX assigned to avoid a ValueError inside the mpl C code...
    a = transform, remove_nans, clip, quantize, simplify, curves

    # Series of cleanups and conversions to the path e.g. it
    # can convert curved segments to line segments.
    vertices, codes = matplotlib.path.cleanup_path(path, transform,
                                                   remove_nans, clip,
                                                   snap, stroke_width,
                                                   simplify, curves)

    # Remove the final vertex (with code 0)
    return vertices[:-1, :], codes[:-1]


# Matplotlib v1.3+ deprecates the use of matplotlib.path.cleanup_path. Instead
# there is a method on a Path instance to simplify this.
if hasattr(matplotlib.path.Path, 'cleaned'):
    _path_segments_doc = path_segments.__doc__

    def path_segments(path, **kwargs):
        pth = path.cleaned(**kwargs)
        return pth.vertices[:-1, :], pth.codes[:-1]

    path_segments.__doc__ = _path_segments_doc


def path_to_geos(path, force_ccw=False):
    """
    Creates a list of Shapely geometric objects from a
    :class:`matplotlib.path.Path`.

    Args:

    * path
        A :class:`matplotlib.path.Path` instance.

    Kwargs:

    * force_ccw
        Boolean flag determining whether the path can be inverted to enforce
        ccw.

    Returns:
        A list of :class:`shapely.geometry.polygon.Polygon`,
        :class:`shapely.geometry.linestring.LineString` and/or
        :class:`shapely.geometry.multilinestring.MultiLineString` instances.

    """
    # Convert path into numpy array of vertices (and associated codes)
    path_verts, path_codes = path_segments(path, curves=False)

    # Split into subarrays such that each subarray consists of connected
    # line segments based on the start of each one being marked by a
    # matplotlib MOVETO code.
    verts_split_inds = np.where(path_codes == Path.MOVETO)[0]
    verts_split = np.split(path_verts, verts_split_inds)
    codes_split = np.split(path_codes, verts_split_inds)

    # Iterate through the vertices generating a list of
    # (external_geom, [internal_polygons]) tuples.
    collection = []
    for path_verts, path_codes in zip(verts_split, codes_split):
        if len(path_verts) == 0:
            continue

        # XXX A path can be given which does not end with close poly, in that
        # situation, we have to guess?
        # XXX Implement a point
        if (path_verts.shape[0] > 2 and
                (path_codes[-1] == Path.CLOSEPOLY or
                 all(path_verts[0, :] == path_verts[-1, :]))):
            if path_codes[-1] == Path.CLOSEPOLY:
                geom = Polygon(path_verts[:-1, :])
            else:
                geom = Polygon(path_verts)
        else:
            geom = LineString(path_verts)

        # If geom is a Polygon and is contained within the last geom in
        # collection, add it to its list of internal polygons, otherwise
        # simple append it as a  new external geom.
        if (len(collection) > 0 and
                isinstance(collection[-1][0], Polygon) and
                isinstance(geom, Polygon) and
                collection[-1][0].contains(geom.exterior)):
            collection[-1][1].append(geom.exterior)
        elif geom.is_empty:
            pass
        else:
            collection.append((geom, []))

    # Convert each (external_geom, [internal_polygons]) pair into a
    # a shapely Polygon that encapsulates the internal polygons, if the
    # external geom is a LineSting leave it alone.
    geom_collection = []
    for external_geom, internal_polys in collection:
        if internal_polys:
            # XXX worry about islands within lakes
            geom = Polygon(external_geom.exterior, internal_polys)
        else:
            geom = external_geom

        # Correctly orientate the polygon (ccw)
        if force_ccw and not geom.exterior.is_ccw:
            geom = shapely.geometry.polygon.orient(geom)

        geom_collection.append(geom)

    # If the geom_collection only contains LineStrings combine them
    # into a single MultiLinestring.
    if geom_collection and all(isinstance(geom, LineString) for
                               geom in geom_collection):
        geom_collection = [MultiLineString(geom_collection)]

    # Remove any zero area Polygons
    not_zero_poly = lambda geom: ((isinstance(geom, Polygon) and
                                   not geom._is_empty and geom.area != 0) or
                                  not isinstance(geom, Polygon))
    result = list(filter(not_zero_poly, geom_collection))

    return result


def remove_bad_ends(verts, codes):
    """
    Designed to remove empty sections from a polygon.
    If this routine is used on lines, valid line components may be
    removed incorrectly.

    """
    quiet = True
    size = codes.size
    remove = []
    new_i = 0
    minx_i = miny_i = 0
    # We don't need to test the last vertex.
    while new_i < (size - 1):
        i = new_i
        j = new_i = i + 1
        x0, y0 = verts[i, :]
        xj, yj = verts[j, :]
        code = codes[j]

        if x0 == xj and y0 == yj:
            # A static point. Do we want to strip this?
            continue
        elif x0 == xj and i >= minx_i:
            ind = 1
            while x0 == xj and code != 1:
#                print 'L:', j, code, x0, xj
                # Update xj, yj and code for this j.
                j += 1
                if j >= size:
                    break
                xj, yj = verts[j, :]
                code = codes[j]
            j -= 1
            minx_i = j + 1
        elif y0 == yj and i >= miny_i:
            ind = 0
            while True:
                if not quiet: print 'L:', j, code, y0, yj
                # Update xj, yj and code for this j.
                j += 1
                if j >= size:
                    if not quiet: print 'Breaking for j', j
                    j -= 1
                    break
                oldxj, oldyj = xj, yj
                xj, yj = verts[j, :]
                code = codes[j]
                if y0 != yj or code == 1:
                    j -= 1
                    break
            miny_i = j + 1
        else:
            continue

        # We've now determined that we have a streak of values with a
        # constant x or y (and we know whether it is the x or the y).
        # Now look at the upper and lower values of that range, identifying
        # the direction (increasing or decreasing) the numbers are going.
        # Any value which does not follow that direction should be removed.
        if not quiet: print 'Lower: {}; Upper: {}'.format(i, j)
        xj, yj = verts[j, :]
        if not quiet: print x0, xj, y0, yj
        if ind == 0:
#            direction = xj - x0
            v0 = x0
            vj = xj
        else:
#            direction = np.sign(yj - y0)
            v0 = y0
            vj = yj
        v0, vj = sorted([v0, vj])
        # We don't exclude the first value, nor the last, hence adding 1
        for ni in range(i + 1, j):
#            this_direction = np.sign(verts[ni, ind] - v0)
            if not quiet: print 'D:', ni, v0, verts[ni, ind], vj
#            if direction != this_direction:
            if not (v0 < verts[ni, ind] <= vj):
                remove.append(ni)
            else:
                # Update v0, making the range that the next value can lie
                # within smaller.
                new_v = verts[ni, ind]
                v0, vj = sorted([new_v, vj])
    return remove


def remove_inds_from_path(path, indices):
    """
    Remove the given indices from the :class:`matplotlib.path.Path` instance.

    Note: This algorithm is updating the vertices and codes *in-place*.

    """
    good = np.ones([path.codes.size, 2], dtype=np.bool)
    good[indices, :] = False
    path.vertices = path.vertices[good].reshape([-1, 2])
    path.codes = path.codes[good[:, 0]]


if __name__ == '__main__':
    r_verts = [1, 3, 2, 2]
    c_verts = [2] * 3 + [1]
    codes = np.array([1, 2, 2, 2])
    r_verts = [2, 3, 4, 2, 3, 4]
    c_verts = [2, 2, 2, 2, 2, 2]
    codes = np.array([1, 2, 2, 1, 2, 2])
    verts = np.vstack([c_verts, r_verts]).T
#    verts = np.vstack([r_verts, c_verts]).T

    print verts
    print remove_bad_ends(verts, codes)
