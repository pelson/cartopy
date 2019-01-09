import shapely.geometry as sgeom
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import cartopy.trace
import numpy as np



rp_proj = ccrs.RotatedPole(pole_latitude=40, pole_longitude=60)

class ReallyPoorRP(ccrs.RotatedPole):
    @property
    def threshold(self):
        return rp_proj.threshold * 10000000.

class CoarsePC(ccrs.PlateCarree):
    @property
    def threshold(self):
        return 1000

proj = ReallyPoorRP(pole_latitude=0, pole_longitude=40)
rp = proj
proj_gl = proj #ccrs.Robinson(0)
proj = CoarsePC() #ccrs.PlateCarree(central_longitude=0)
coarse = CoarsePC()
fine_coarse = ccrs.PlateCarree()


ax = plt.axes(projection=proj)
import cartopy.feature
ax.add_feature(cartopy.feature.LAND)
ax.gridlines(crs=rp)

target_len = 1
# 100x less than the width of the projection (nb. this could be based on axes width...)
target_len = np.ptp(ax.projection.x_limits) / 100

src = ccrs.Geodetic()
target = ax.projection
target = proj_gl

# A pertinent straight-line segment that needs cutting if you interpolate far enough.
verts = np.array([[-179, 15], [-179, -8]])
rp_verts = np.concatenate([[rp.transform_point(*pt, ccrs.Geodetic())] for pt in verts])


geom = sgeom.LineString(rp_verts)

coarse_proj = coarse.project_geometry(geom, rp)
fine_proj = fine_coarse.project_geometry(geom, rp)

# There should be fewer geometries when we have a coarse projection.
assert len(coarse_proj.geoms) < len(fine_proj.geoms)

# In fact, in this case, we want just one.
assert len(coarse_proj.geoms) == 1

# The simplest reprojection of this line does not require cutting, but if you go finer, you will need to cut it.
line_verts = np.concatenate([[ax.projection.transform_point(*pt, ccrs.Geodetic())] for pt in verts])

import shapely.geometry as sgeom
l = mpath.Path(line_verts)

if True:
    print(l)
    # The resolution in length of target projection units.
    l = cartopy.trace.interp_path(l, max_length=target_len, source=rp, dest=coarse)

    p = mpatches.PathPatch(l, facecolor='none', edgecolor='red', lw=10, transform=ax.transData)
    ax.add_patch(p)
#    ax.plot(line_verts[:, 0], line_verts[:, 1], transform=ax.transData, color='yellow', lw=1)
    ax.plot(rp_verts[:, 0], rp_verts[:, 1], transform=rp, color='blue', lw=4)

#ax.set_global()
ax.coastlines()
#ax.margins(5)
#ax.set_xlim(-180, -170)

plt.show()
