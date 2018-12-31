"""
Sometimes proj4 doesn't have what we want. We can fall back to python level implementations (but performance suffers).

"""
import numpy as np
import shapely.geometry as sgeom


import cartopy.crs as ccrs

ll = ccrs.PlateCarree(globe=ccrs.Globe(semimajor_axis=1, ellipse='sphere', datum=None))
gn0 = ccrs.Gnomonic(central_longitude=-90)
gn1 = ccrs.Gnomonic(central_longitude=90)


def project(λ, ϕ):
    #    print('Projecting: ', λ, ϕ)
#    x, y = np.rad2deg(λ), np.rad2deg(ϕ)

    if λ < 0:
        x, y = gn0.transform_point(λ-np.pi/4, ϕ, ll)
        x += -6378137.0
    else:
        x, y = gn1.transform_point(λ+np.pi/4, ϕ, ll)
        x_off, _ = gn1.transform_point(np.pi/4, ϕ, ll)
        print('fff:', x_off)
        x -= x_off

    return x, y


#class Custom(ccrs.CRS):
class Custom(ccrs.Projection):
    def __init__(self, forward_prj_fn, *args, **kwargs):
        # TODO: Determine whether forward is really inverse...
        self._prj_fn = forward_prj_fn

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


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    ax = plt.axes(projection=Custom(project))
#    ax = plt.axes(projection=ccrs.Gnomonic())
    ax.coastlines()
    ax.set_global()
    ax.stock_img()
    ax.gridlines()
    plt.show()
