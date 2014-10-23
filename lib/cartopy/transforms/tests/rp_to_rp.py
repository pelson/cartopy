import matplotlib.pyplot as plt
import cartopy.crs as ccrs


ax1 = plt.subplot(1, 1, 1, projection=ccrs.RotatedPole(pole_longitude=-180, pole_latitude=60))
ax1.gridlines(lw=3)
ax1.coastlines()


from cartopy.transforms.euler_angles import UM_rotated_pole_inverse, UM_rotated_pole
rot_to_ll = UM_rotated_pole_inverse(-180, 60)
ll_to_rot = UM_rotated_pole(-180, 60)


am_in_ll = [[-180, -90], [-180, 0], [-180, 90]]
nearly_polar = 179.999999, 89.999999
nearly_polar = 180, 89.999999999
eps = 1e-13
nearly_polar = 180 - eps, 90 - eps
am_in_ll = [[-nearly_polar[0], -nearly_polar[1]], [-nearly_polar[0], 0], [-nearly_polar[0], nearly_polar[1]]]
#am_in_ll = [[nearly_polar[0], -nearly_polar[1]], [nearly_polar[0], 0], nearly_polar]
am_in_rot = [ll_to_rot(*vert) for vert in am_in_ll]
#am_in_ll_again = [rot_to_ll(*vert) for vert in am_in_rot]
#print am_in_ll_again


from cartopy.transforms.cut import Antimeridian

segments = Antimeridian().cut_spherical(am_in_rot, 0)
print segments

from cartopy.transforms.geom_interpolate import interpolate_and_project_path, Precision, cartesian_interp_fn
from cartopy.transforms.interpolate import great_circle_interpolation
import matplotlib.path as mpath
import matplotlib.patches as mpatches
for seg in segments:
    path = mpath.Path([rot_to_ll(*vert) for vert in seg])
#    path = mpath.Path([vert for vert in seg])
    
    path = interpolate_and_project_path(path, ll_to_rot, great_circle_interpolation, Precision(10, 30))
    
    seg = path
    print seg.vertices
    patch = mpatches.PathPatch(seg, facecolor='none', edgecolor='red', lw=2, transform=ax1.transData)
    ax1.add_patch(patch)

ax1.set_global()

plt.show()