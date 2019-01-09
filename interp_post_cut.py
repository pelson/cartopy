import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import cartopy.trace
import numpy as np


ax = plt.axes(projection=ccrs.PlateCarree())
ax = plt.axes(projection=ccrs.InterruptedGoodeHomolosine())
#ax = plt.axes(projection=ccrs.Stereographic())


target_len = 1
# 100x less than the width of the projection (nb. this could be based on axes width...)
target_len = np.ptp(ax.projection.x_limits) / 100

verts = np.array([[-50, 50],  [50, 50]])
import shapely.geometry as sgeom
l = mpath.Path(verts)


ls = sgeom.LineString(verts)
import cartopy.mpl.patch
paths = cartopy.mpl.patch.geos_to_path(ax.projection.project_geometry(ls, ccrs.Geodetic()))

for l in paths:
    print(l)
    # The resolution in length of target projection units.
    l = cartopy.trace.interp_path(l, max_length=target_len, source=ccrs.Geodetic(), dest=ax.projection)

    p = mpatches.PathPatch(l, facecolor='none', edgecolor='black', transform=ax.transData)
    ax.add_patch(p)
ax.coastlines()
ax.margins(1)

plt.show()
