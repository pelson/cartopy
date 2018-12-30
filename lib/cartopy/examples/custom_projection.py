"""
Sometimes proj4 doesn't have what we want. We can fall back to python level implementations (but performance suffers).

"""
import numpy as np
import shapely.geometry as sgeom

def project(λ, ϕ):
    print('Projecting: ', λ, ϕ)
    x, y = np.rad2deg(λ+2), np.rad2deg(ϕ)

    if x > 0:
        pass
        #x = x * 2
#        y = y + (x % 4 - 2)

    return (x + 180) % 360 - 180, y


import cartopy.crs as ccrs


#class Custom(ccrs.CRS):
class Custom(ccrs.Projection):
    def __init__(self, forward_prj_fn, *args, **kwargs):
        # TODO: Determine whether forward is really inverse...
        self._prj_fn = forward_prj_fn

        # TODO: Shouldn't need to jump through proj4 hoops.
        super().__init__([('proj', 'lonlat')])

    @property
    def x_limits(self):
        return -360, 360

    @property
    def y_limits(self):
        return -90, 90

    @property
    def threshold(self):
        return 360 / 1

    @property
    def boundary(self):
        return sgeom.box(
            self.x_limits[0], self.y_limits[0],
            self.x_limits[1], self.y_limits[1])




if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    ax = plt.axes(projection=Custom(project))
    ax.coastlines()
    ax.set_global()
    ax.stock_img()
    plt.show()
