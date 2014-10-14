# -*- coding: utf-8 -*-
import interpolate
import numpy as np







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


def interpolate_and_project_path(path, interpolator_creation_fn, precision):
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



if __name__ == '__main__':
    import matplotlib.path as mpath
    import cartopy.crs as ccrs
    from functools import partial

    do_africa = True

    proj = ccrs.Robinson()
    precision = 2e6

    proj = ccrs.Mollweide()
    precision = 4e6

    path = mpath.Path([[-50, 50], [30, 50], [50, -60], [-50, 50],
                       [-20, 30], [30, -20], [20, 40], [-20, 30]],
                      codes=[1, 2, 2, 2,
                             1, 2, 2, 2])

    path = mpath.Path([[-50, 50], [50, 50], [50, -50], [-50, 50],
                       [-30, 30], [30, -30], [30, 30], [-30, 30]],
                      codes=[1, 2, 2, 2,
                             1, 2, 2, 2])

    path = mpath.Path([[-180, 90], [0, 90], [180, 90], [180, 0], [180, -90],
                       [0, -90], [-180, -90], [-180, 0], [-180, 90]])

    # NPS
    path = mpath.Path([[180, -90], [-90, -90], [0, -90], [90, -90], [180, -90]])
    proj = ccrs.NorthPolarStereo()
    precision = 5e21

    # XXX DOESN'T WORK
#    proj = ccrs.LambertConformal(central_longitude=0, central_latitude=80, secant_latitudes=(-14, 13))
#    precision = 4e4
#    w = 100
#    path = mpath.Path([[-w, 90], [0, 90], [w, 90]] + [[w, i] for i in np.linspace(90, -40, 3)] + 
#                      [[i, -40] for i in np.linspace(w, -w, 3)] +
#                      [[-w, i] for i in np.linspace(-40, 90, 3)] + [[-w, 90]])

#    proj = ccrs.Orthographic()
#    precision = 8e5
#    path = mpath.Path([[-90, 90], [0, 90], [90, 90], [90, 0], [90, -90],
#                       [0, -90], [-90, -90], [-90, 0], [-90, 90]])

#    # XXX Doesn't work.
#    proj = ccrs.TransverseMercator()
#    precision = 8e6
#    path = mpath.Path([[-179, 90], [0, 90], [180, 90], [180, 0.0001], [180, 0], [180, -90],
#                       [0, -90], [-180, -90], [-180, 0], [-180, 0.0001], [-180, 90]])


#    # XXX Doesn't work.
#    proj = ccrs.Gnomonic()
#    precision = 8e6
#    path = mpath.Path([[-180, -90], [-90, -90], [0, -90], [90, -90], [180, -90], [-180, -90]])


#    # Equ conic
#    from pyproj import Proj
#    proj = Proj(proj='eqc')
#    proj.transform_point = proj.__call__
#    proj.x_limits = 'Unknown'
#    precision = 4e6
#    print proj.transform_point(path.vertices[:, 0], path.vertices[:, 1])

#    # IGH
#    eps = 1e-13
#    path = mpath.Path([[-180, 90],
#                       [-40 - eps, 90], [-40 - eps, 0], [-40 + eps, 0], [-40 + eps, 90],
#                       [0, 90], [180, 90], [180, 0], [180, -90],
#                       [80+eps, -90], [80+eps, 0], [80-eps, 0], [80-eps, -90],
#                       [0, -90],
#                       [-20+eps, -90], [-20+eps, 0], [-20-eps, 0], [-20-eps, -90],
#                       [-100+eps, -90], [-100+eps, 0], [-100-eps, 0], [-100-eps, -90],
#                       [-180, -90], [-180, 0], [-180, 90]])
#    proj = ccrs.InterruptedGoodeHomolosine()
#    precision = 5e4



    print 'Prec {}; XLim: {}'.format(precision, proj.x_limits)
    transform_point = proj.transform_point

    project_fn = partial(transform_point, src_crs=ccrs.Geodetic())
    result = []

    new_path = interpolate_and_project_path(path, interpolate.great_circle_interpolation, precision=Precision(precision, 30))

    if do_africa:
        # Africa
        import cartopy.io.shapereader as shpreader
        shpfilename = shpreader.natural_earth(resolution='110m',
                                          category='cultural',
                                          name='admin_0_countries')
        reader = shpreader.Reader(shpfilename)
        countries = reader.records()
        shapes = []
        for country in countries:
            if country.attributes['continent'] == 'Africa':
                shapes.append(country.geometry)
        import cartopy.mpl.patch as cpatch
        from shapely.ops import cascaded_union
        africa = cpatch.geos_to_path(cascaded_union(shapes))
        africa = mpath.Path.make_compound_path(*africa)

        africa_interp = interpolate_and_project_path(africa, interpolate.great_circle_interpolation, precision=Precision(precision, 30))


    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch

    plt.figure(figsize=(18, 8))
    ax = plt.subplot(1, 2, 1)
    ax.add_patch(PathPatch(path, facecolor='yellow', edgecolor='red'))
    if do_africa:
        ax.add_patch(PathPatch(africa, facecolor='green', edgecolor='black'))
    ax.autoscale_view()

    print path.vertices.shape, new_path.vertices.shape

    ax = plt.subplot(1, 2, 2)
    ax.add_patch(PathPatch(new_path, facecolor='yellow', edgecolor='red'))
    if do_africa:
        ax.add_patch(PathPatch(africa_interp, facecolor='green', edgecolor='black', zorder=2))
    ax.autoscale_view()
    plt.show()
