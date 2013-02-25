from __future__ import division

import numpy as np

import matplotlib.lines as mlines
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import cartopy.crs as ccrs

from cartopy.mpl.clip_path import *


def main():
    ax = plt.axes()
    ax.set_xlim([5, 15])
    ax.set_ylim([-15, -5])
    p = mpatches.CirclePolygon([10, -10], 3, resolution=150, alpha=0.5, facecolor='coral')
    ax.add_patch(p)
    
    patch_path = p.get_path()
    patch_path = (p.get_transform() - ax.transData).transform_path(patch_path)
    
    bbox = mtrans.Bbox([[10, -15], [15, -5]])
    
    r = clip_path(patch_path, bbox)
    
    patch_line = mlines.Line2D([0], [0], transform=None)
    patch_line.set_xdata(r.vertices[:, 0])
    patch_line.set_ydata(r.vertices[:, 1])
    
    ax.add_line(patch_line)
    plt.show()


def main3():
    import matplotlib.patches as mpatches
    import matplotlib.path as mpath
    import matplotlib.transforms as mtrans
    import matplotlib.pyplot as plt
    
    from cartopy.mpl.clip_path import clip_path_mpl
    
    ax = plt.axes()
    ax.set_xlim([-20, 10])
    ax.set_ylim([-150, 100])
    
    path = mpath.Path.unit_regular_star(8)
    path.vertices *= [10, 100]
    path.vertices -= [5, 25]
    
    patch = mpatches.PathPatch(path, alpha=0.5, facecolor='coral', edgecolor='none')
    ax.add_patch(patch)
    
    bbox = mtrans.Bbox([[-12, -77.5], [-2, 50]])
    result_path = clip_path_mpl(path, bbox)
    result_patch = mpatches.PathPatch(result_path, alpha=0.5, facecolor='green', lw=4, edgecolor='black')
    
    ax.add_patch(result_patch)
    plt.show()


def main2():
    ax = plt.axes()
#    ax.set_xlim([5, 15])
#    ax.set_ylim([-15, -5])
#    p = mpatches.CirclePolygon([10, -10], 3, resolution=150, alpha=0.5, facecolor='coral')
#    ax.add_patch(p)
    
    ax.set_xlim([-0.2, 12.2])
    ax.set_ylim([-0.2, 12.2])
    
    patch_path = mpath.Path(np.array([[0, 1, 1, 0.5, 0, 0], [0, 0, 1, 1.5, 1, 0]]).T, closed=True)
    
    patch_path = mpath.Path(np.array([[0, 1, 1, 2, 2, 3, 3, 0.5, 0], [0, 0, 1, 1, 0, 0, 1, 2, 1]]).T)
    

    codes = np.empty(10, dtype=mpath.Path.code_type)
    codes[0] = mpath.Path.MOVETO
    codes[1:4] = mpath.Path.LINETO
    codes[4] = mpath.Path.CLOSEPOLY
    codes[5] = mpath.Path.MOVETO
    codes[6:-1] = mpath.Path.LINETO
    codes[-1] = mpath.Path.CLOSEPOLY
    
    patch_path = mpath.Path(np.array([[0, 1, 1, 0.5, 0, 10, 11, 11, 10.5, 10] , 
                                      [0, 0, 1, 1.5, 1, 10, 10, 11, 11.5, 11]]).T, 
                            codes = codes)
   
#    patch_path = (p.get_transform() - ax.transData).transform_path(patch_path)
    
    
    bbox = mtrans.Bbox.unit() #([[10, -15], [15, -5]])
    bbox = mtrans.Bbox([[0.25, 0.25], [10.75, 10.75]])
    bbox = mtrans.Bbox([[0.25, 0.25], [10.75, 0.75]])
    
    

    bbox = mtrans.Bbox([[0.2, 0.2], [0.8, 1.3]])
    
    
#    prj = ccrs.NorthPolarStereo()
#    p = prj.boundary
#    from cartopy.mpl.patch import geos_to_path
#    patch_path, = geos_to_path(prj.boundary)
#    
#    print patch_path.vertices[0, :] == patch_path.vertices[-1, :]
#    
#    ax.set_xlim([patch_path.vertices[:, 0].min(), patch_path.vertices[:, 0].max()])
#    ax.set_ylim([patch_path.vertices[:, 1].min(), patch_path.vertices[:, 1].max()])
#    bbox = mtrans.Bbox([[patch_path.vertices[:, 0].min() + 1e7, patch_path.vertices[:, 1].min() + 1e7],
#                        [patch_path.vertices[:, 0].max() - 1e7, patch_path.vertices[:, 1].max() - 1e7]])
#    
#    
#    bbox_path = mpath.Path(np.array([[0.2, 0.8, 0.8, 0.2, 0.2], [0.2, 0.2, 1.3, 1.3, 0.2]]).T)

    bbox_path = bbox_to_path(bbox)
    
    r = clip_path(patch_path, bbox)
    r2 = clip_path2(patch_path, 
                    bbox_path,
                    point_inside_clip_path=(0.5, 0.5))
    
    print patch_path.codes
    print patch_path.vertices[0, :] == patch_path.vertices[-1, :]
    print r2.vertices[0, :] == r2.vertices[-1, :]
    
#    print patch_path.vertices[0, :] == patch_path.vertices[-1, :]
#    print r2.vertices[0, :] == r2.vertices[-1, :]
#    print ':R:', r2
    
    
#    patch_line = mlines.Line2D([0], [0], transform=None)
#    patch_line.set_xdata(r.vertices[:, 0])
#    patch_line.set_ydata(r.vertices[:, 1])
#    
#    ax.add_line(patch_line)
    
    ax.add_patch(mpatches.PathPatch(patch_path, alpha=0.5))
    
#    ax.add_patch(mpatches.PathPatch(r, alpha=0.5, facecolor='red', lw=5, edgecolor='green'))
    
    ax.add_patch(mpatches.PathPatch(r2, alpha=0.5, facecolor='yellow', lw=5, edgecolor='black'))
    
    plt.show()


if __name__ == '__main__':
#    main3()

#    print lines_intersect(np.array([0, 0]), np.array([1, 1]),
#                          np.array([-1, -1]), np.array([0, -1]))
    

#    main2()

    ax = plt.axes(projection=ccrs.NorthPolarStereo())
    
    ax = plt.axes(projection=ccrs.InterruptedGoodeHomolosine())
    ax.cla()
#    ax.set_extent([-15, 10, 50, 60])
    
    ax.coastlines()
    plt.show()