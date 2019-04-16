import matplotlib.path as mpath
from cartopy.transforms.geom_interpolate import interpolate_and_project_path, Precision

from cartopy.transforms.interpolate import great_circle_interpolation


if __name__ == '__main__':
    
    import cartopy.crs as ccrs
    from functools import partial


    proj = ccrs.PlateCarree()
    coarse_precision = 60
    fine_precision = 10

    path = mpath.Path([[-50, 50], [30, 50], [50, -60], [-50, 50],
                       [-20, 30], [30, -20], [20, 40], [-20, 30]],
                      codes=[1, 2, 2, 2,
                             1, 2, 2, 2])

    transform_point = proj.transform_point

    project_fn = partial(transform_point, src_crs=ccrs.Geodetic())
    result = []

    coarse_path = interpolate_and_project_path(path, project_fn,
                                            great_circle_interpolation,
                                            precision=Precision(coarse_precision, 30))
    
    fine_path = interpolate_and_project_path(path, project_fn,
                                            great_circle_interpolation,
                                            precision=Precision(fine_precision, 30))

    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch

    fig = plt.figure(figsize=(7, 4))
    ax = plt.subplot(2, 2, 1, projection=ccrs.PlateCarree())
    ax.add_patch(PathPatch(path, facecolor='gray', edgecolor='black',
                           alpha=0.5, transform=ax.transData))
#     ax.coastlines()
    ax.set_global()
    ax.set_title('No interpolation')

    ax = plt.subplot(2, 2, 2, projection=ccrs.PlateCarree())
    ax.add_patch(PathPatch(coarse_path, facecolor='gray', edgecolor='black',
                           alpha=0.5, transform=ax.transData))
#     ax.coastlines()
    ax.set_global()
    ax.set_title('Coarse interpolation')
    
    ax = plt.subplot(2, 1, 2, projection=ccrs.PlateCarree())
    ax.add_patch(PathPatch(fine_path, facecolor='gray', edgecolor='black',
                           alpha=0.5, transform=ax.transData))
#     ax.coastlines()
    ax.set_global()
    ax.set_title('Fine interpolation')
    
    fig.subplots_adjust(left=0.05, right=0.95)
    
    plt.show()
