import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import shapely.geometry as sgeom


LHS, RHS = ccrs.NorthPolarStereo(), ccrs.PlateCarree()
geom = sgeom.Point(0, 0)


fig = plt.figure(figsize=(7, 2))

ax1 = plt.subplot(1, 2, 1, projection=LHS)
ax2 = plt.subplot(1, 2, 2, projection=RHS)

ax1.coastlines(color='gray', alpha=0.4)
ax2.coastlines(color='gray', alpha=0.4)

ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
ax2.add_geometries([geom], LHS, color='blue', alpha=0.8, linewidth=50)

plt.show()