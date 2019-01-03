"""
Sometimes proj4 doesn't have what we want. We can fall back to python level implementations (but performance suffers).

"""
import numpy as np
import shapely.geometry as sgeom


import cartopy.crs as ccrs

ll = ccrs.PlateCarree(globe=ccrs.Globe(semimajor_axis=1, ellipse='sphere', datum=None))
ll = ccrs.Geodetic()
gn0 = ccrs.Gnomonic(central_longitude=-90)
gn1 = ccrs.Gnomonic(central_longitude=90)
t0 = gn0.transformer(ll)
t1 = gn1.transformer(ll)
print(t0)
print(t1)

def project(coords):
    λ, ϕ = coords
#    λ, ϕ = np.rad2deg(λ), np.rad2deg(ϕ)

    #x_off, _ = gn1.transform_point(np.pi/4, ϕ, ll)
    x_off = 6378137.0
    foo = np.rad2deg
    if λ < 0:
        x, y = t0.coords(foo(np.array([λ-np.pi/4, ϕ])))
        x -= x_off
    else:
        x, y = t1.coords(foo(np.array([λ+np.pi/4, ϕ])))
        x += x_off
    return np.array([x, y])
print('\n'*20)


def inverse(coords):
    orig = coords.copy()
    x, y = coords
    x_off = 6378137.0
    if x < 0:
        coords[0] += x_off
        λ, ϕ = ll.transformer(gn0).coords(coords)
        λ = λ+np.pi/4
    else:
        coords[0] -= x_off
        λ, ϕ = ll.transformer(gn1).coords(coords)
    λ, ϕ = np.deg2rad([λ, ϕ])
    if x < 0:
        λ = λ+np.pi/4
    else:
        λ = λ - np.pi/4
    
    # λ, ϕ = coords
    #print('INVERTING:', orig, '->', [λ, ϕ], '({} deg)'.format(np.rad2deg([λ, ϕ])))
    return np.array([λ, ϕ], dtype=float)


#class Custom(ccrs.CRS):
class Custom(ccrs.Projection):
    def __init__(self, forward_prj_fn, inverse_prj_fn, *args, **kwargs):
        # TODO: Determine whether forward is really inverse...
        self._prj_function = forward_prj_fn
        self._prj_function_inverse = inverse_prj_fn

        # TODO: Shouldn't need to jump through proj4 hoops.
        super().__init__([('proj', 'lonlat')])

    @property
    def x_limits(self):
        return gn0.x_limits
        return -360, 360

    @property
    def y_limits(self):
        return gn0.y_limits
        return -90, 90

    @property
    def threshold(self):
        return gn0.threshold
        return 360 / 1

    @property
    def boundary(self):
       #return gn0.boundary
        return sgeom.box(
            self.x_limits[0], self.y_limits[0],
            self.x_limits[1], self.y_limits[1])


from numpy.testing import assert_array_equal, assert_array_almost_equal
def test_pc_to_pc():
    pc = ccrs.PlateCarree()
    t = pc.transformer(pc)
    assert_array_almost_equal(t.coords(np.array([115, -45.])), np.array([115, -45.0]))

def test_pc_to_prj():
    pc = ccrs.PlateCarree()
    t = ccrs.Mercator().transformer(pc)
    expected = np.array([12801741.44, -5591295.92])
    assert_array_almost_equal(t.coords(np.array([115, -45.])), expected, decimal=0)

def test_prj_to_pc():
    # In partnership with test_pc_to_prj, assert that the thing round-trips.
    pc = ccrs.PlateCarree()
    fwd = ccrs.Mercator().transformer(pc).coords(np.array([115, -45.]))
    fwd = np.array(fwd)
    t = pc.transformer(ccrs.Mercator())
    assert_array_almost_equal(t.coords(fwd), np.array([115, -45]))

def test_prj_to_geod():
    ll = ccrs.Geodetic()
    t = ccrs.Mercator().transformer(ll)
    expected = np.array([12801741.44, -5591295.92])
    assert_array_almost_equal(t.coords(np.array([115, -45.])), expected, decimal=0)

def test_geod_to_prj():
    ll = ccrs.Geodetic()
    t = ll.transformer(ccrs.Mercator())
    input = np.array([12801741.44, -5591295.92])
    assert_array_almost_equal(t.coords(input), np.array([115, -45]), decimal=0)

def test_custom_to_geod():
    crs = Custom(project, inverse)
    t = crs.transformer(ccrs.Geodetic())
    r = t.coords(np.array([115, -45.]))
    expected = np.array([9108923.64, -11119942.51])
    expected = np.array([2974174.13, -7037495.53])

    # NOTE: These numbers have been derived cyclically - I still need to verify they are correct.
    expected = np.array([23901924.385688, -18648425.025443])
    #expected = np.array([9459443.812346, -7083437.249145])
    assert_array_almost_equal(r, expected)

def test_geod_to_custom():
    crs = Custom(project, inverse)
    t = ccrs.Geodetic().transformer(crs)
    # Numbers taken from test_custom_to_geod.
    input = np.array([23901924.385688, -18648425.025443])
    #input = np.array([9459443.812346, -7083437.249145])
    r = t.coords(input)
    expected = np.array([115, -45])
    assert_array_almost_equal(r, expected)

def test_proj_is_inverse():
    v = np.array([np.pi/4, np.pi/8])
    expected = np.array([6378137, 2641910.848074])
    p = project(v)
    assert_array_almost_equal(p, expected)
    i = inverse(p)
    assert_array_almost_equal(v, i)

def test_pc_to_custom():
    crs = Custom(project, inverse)
    t = ccrs.PlateCarree().transformer(crs)
    # Numbers taken from test_custom_to_geod.
    input = np.array([23901924.385688, -18648425.025443])
    #input = np.array([9459443.812346, -7083437.249145])
    r = t.coords(input)
    expected = np.array([115, -45])
    assert_array_almost_equal(r, expected)

if __name__ == '__main__':

    from cartopy._crs import Proj4Transformer, RadiansOutProj4Transformer, RadiansInProj4Transformer

    print(ll.proj4_init)
    t = RadiansInProj4Transformer(ll.proj4_init, ll.as_geodetic().proj4_init)
    b = t.coords(np.array([5, 52.]))
    print('FOO:', b)

    print('----')
    b = t1.coords((np.array([5+60, 52.])))
    print(b)


    input = np.array([5813605.77312359, -788732.30988801])
    print('------')
    t = Custom(project, inverse).transformer(ll)
    b = t.coords(np.array([5, 52.]))
    print('FWD:', b)
    t = ll.transformer(Custom(project, inverse))
    t.coords(input)
   
    import sys
#    sys.exit(1)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    ax = plt.axes(projection=Custom(project, inverse))
    #ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.set_global()
    #ax.stock_img()
    ax.gridlines()
    print('PLOT:------')
    def project_err(coords):
        raise RuntimeError()
    ax.plot([-4e7, 0], [0, 2e7], transform=Custom(project, inverse))
    ax.plot([0, 0], [0, 45], 'b', transform=ccrs.PlateCarree())
    ax.plot(45, 0, 'or', transform=ccrs.Geodetic())
    plt.show()
