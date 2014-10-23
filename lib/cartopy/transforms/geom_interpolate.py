# -*- coding: utf-8 -*-
import interpolate
import numpy as np
import matplotlib.path as mpath


def to_cartesian(spherical_p):
    # Convert lats and lons to cartesian xyz. Only use this function for fast approximation. For anything else, just use the Geocentric coordinate system.
    lam, phi = np.deg2rad(spherical_p)
    cos_phi = np.cos(phi)
    return cos_phi * np.cos(lam), cos_phi * np.sin(lam), np.sin(phi)


def perp_distance_squared(p0, p1, p_mid):
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = p_mid

    dx = x1 - x0
    dy = y1 - y0
    d2 = dx * dx + dy * dy

    dx2 = x2 - x0
    dy2 = y2 - y0
    dz = dy * dx2 - dx * dy2
    if d2 == 0:
        return 0
    else:
        return dz * dz / d2


def distance_squared_2d(p0, p1):
    return (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2

def distance_squared_3d(p0, p1):
    return (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2 + (p0[2] - p1[2]) ** 2

def _segment_split(coords, interpolator, project_fn, t, p0, p1,
                   cart_p0, cart_p1, depth, precision):
    """
    Interpolate between the given coordinates until the given precision
    is attained.

    """
    # TODO: Consider angular distance (as per d3) as well?

    if depth > 16:
        return
#        print 'Max depth.', depth, t, p0, p1
#        return

    t_delta = 0.5 ** (depth + 1)

    sp_mid = interpolator(t)
    p_mid = project_fn(sp_mid[0], sp_mid[1])
    cart_mid = to_cartesian(sp_mid)

    perp_projected_distance = perp_distance_squared(p0, p1, p_mid)
    # Distance in projected coords squared.
    projected_distance = distance_squared_2d(p0, p_mid)
    # Distance in 3d Cartesian squared.
    angular_distance = distance_squared_3d(cart_p0, cart_mid)

#    print perp_projected_distance, angular_distance, precision.angular_distance_squared

    if (projected_distance > precision.distance_squared or
            angular_distance > precision.angular_distance_squared): 
        _segment_split(coords, interpolator, project_fn,
                       t - t_delta, p0, p_mid, cart_p0, cart_mid,
                       depth=depth+1, precision=precision)

    coords.append(p_mid)

    projected_distance = distance_squared_2d(p_mid, p1)
    angular_distance = distance_squared_3d(cart_mid, cart_p1)
    if (projected_distance > precision.distance_squared or
            angular_distance > precision.angular_distance_squared):
        _segment_split(coords, interpolator, project_fn,
                       t + t_delta, p_mid, p1, cart_mid, cart_p1,
                       depth=depth+1, precision=precision)


import itertools

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


class Precision(object):
    def __init__(self, min_distance, min_angular_distance):
        # The minimum distance distance in projected space.
        self.distance_squared = min_distance ** 2
        # The minimum distance projected onto the unit sphere.
        self.angular_distance_squared = np.cos(np.deg2rad(min_angular_distance))



def cartesian_interp_fn(p0, p1):
    dx = p0[0] - p1[0]
    dy = p0[1] - p1[1]
    def interpolator(t):
        return p1[0] + t * dx, p1[1] + t * dy
    return interpolator


def interpolate_and_project_path(path, project_fn, interpolator_creation_fn, precision):
    # NOTE: This algorithm is pretty dumb and may well lead to some cases of un-preserved geometry
    # when a poor precision is used.
    verts = []
    codes = []

    for seg0, seg1 in pairwise(path.iter_segments()):
        sp0, code0 = seg0
        sp1, code1 = seg1

        p0 = project_fn(sp0[0], sp0[1])
        p1 = project_fn(sp1[0], sp1[1])

        verts.append(p0)
        codes.append(code0)
        if code1 == mpath.Path.LINETO:
            interpolator = interpolator_creation_fn(sp0, sp1)
            result = []
            cart_p0, cart_p1 = to_cartesian(sp0), to_cartesian(sp1)
            _segment_split(result, interpolator, project_fn, t=0.5, p0=p0, p1=p1,
                           cart_p0=cart_p0, cart_p1=cart_p1, depth=1, precision=precision)
            verts.extend(result)
            codes.extend([mpath.Path.LINETO] * len(result))
    else:
        # XXX NOTE: Might want to interpolate this bit too!!!!
        verts.append(p1)
        codes.append(code1)
    return mpath.Path(np.array(verts), codes)



# =================  THE INTERFACE? ==========================
import collections
PolygonType = collections.namedtuple('PolygonType', 'ring, holes')


class TargetGeometry(object):
    def __init__(self, geometry, crs, vertex_interp_fn):
        # XXX crs - could just be a function which takes xy -> target xy.
        self.geometry = geometry
        self.crs = crs
        self.vertex_interp_fn = vertex_interp_fn

    # XXX REMOVE
    def show(self, precision):
        result = self.geometry.interpolate(self.vertex_interp_fn, precision)
        # do it.
# ============================================================


if __name__ == '__main__':
    
    import cartopy.crs as ccrs
    from functools import partial


    proj = ccrs.Robinson()
    precision = 4e6

#    proj = ccrs.Mollweide()
#    precision = 4e6

    path = mpath.Path([[-50, 50], [30, 50], [50, -60], [-50, 50],
                       [-20, 30], [30, -20], [20, 40], [-20, 30]],
                      codes=[1, 2, 2, 2,
                             1, 2, 2, 2])

#     path = mpath.Path([[-50, 50], [50, 50], [50, -50], [-50, 50],
#                        [-30, 30], [30, -30], [30, 30], [-30, 30]],
#                       codes=[1, 2, 2, 2,
#                              1, 2, 2, 2])



    print 'Prec {}; XLim: {}'.format(precision, proj.x_limits)
    transform_point = proj.transform_point

    project_fn = partial(transform_point, src_crs=ccrs.Geodetic())
    result = []

    new_path = interpolate_and_project_path(path, project_fn, interpolate.great_circle_interpolation, precision=Precision(precision, 30))

    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch

    plt.figure(figsize=(18, 8))
    ax = plt.subplot(1, 2, 1)
    ax.add_patch(PathPatch(path, facecolor='yellow', edgecolor='red'))
    ax.autoscale_view()

    print path.vertices.shape, new_path.vertices.shape

    ax = plt.subplot(1, 2, 2)
    ax.add_patch(PathPatch(new_path, facecolor='yellow', edgecolor='red'))
    ax.autoscale_view()
    plt.show()
