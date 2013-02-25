from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatch
import matplotlib.path as mpath
import matplotlib.transforms as mtrans

from positioner import where_on_line, where_on_path


import cartopy.crs as ccrs


def case1():
    ax = plt.axes(projection=ccrs.Robinson())
    
    line = mlines.Line2D([90, 90], [-90, 90], transform=ccrs.PlateCarree())
    
    ax.add_line(line)
    ax.set_global()
    ax.coastlines()
    
    # Rectangle is in a sorry state of affairs...
    bg = mpatch.Rectangle([-1e6, -7.4e6], 7.8e6, 2 * 7.4e6, transform=ax.transData, 
                          color='coral', alpha=0.5, clip_on=False)
    x0, x1 = -1e6, -1e6 + 7.8e6
    y0, y1 = -9e6, 7.4e6
    bg = mpatch.PathPatch(mpath.Path([[x0, y0], [x0, y1], 
                                      [x1, y1], [x1, y0], 
                                      [x0, y0], ],
                                     closed=True),
                          transform=ax.transData, 
                          color='coral', alpha=0.5, clip_on=False
                          )
    
    ax.add_patch(bg)
    
    # patch.contains_point is in a bad way too.
    #print bg.get_path().contains_point([0, 0])
    #print bg.get_path()
    
    path = (line.get_transform() - ax.transData).transform_path(line.get_path())
    
    snapped = mpatch.PathPatch(path, transform=ax.transData, 
                               facecolor='none', edgecolor='yellow',
                               lw=4)
    ax.add_patch(snapped)
    
    import line_snap
    new = line_snap.horiz_snap_path_to_patch_if_outside(path, bg)
    new = mpath.Path(new)
    new = (ax.transData - line.get_transform()).transform_path(new)
    
    snapped = mpatch.PathPatch(new,
                               transform=line.get_transform(), 
                               facecolor='none', edgecolor='green',
                               lw=4)
    ax.add_patch(snapped)
    
    
    tick_locs = [-90, -45, 0, 45, 90]
    tick_locs = range(-90, 90, 2)
    
    for tick_loc in tick_locs:
        try:
            r = where_on_path(new, y=tick_loc)
            plt.plot(r[0], r[1], 'ob', transform=ccrs.PlateCarree())
        except ValueError:
            print 'not crossed:', tick_loc
    
    plt.show()


def case2():
    target_label_cs = ccrs.PlateCarree()
    proj = ccrs.Mollweide()
    ax = plt.axes(projection=proj)
    
    line = mlines.Line2D([0.9, 0.9], [0, 1], transform=ax.transAxes)
    
    ax.add_line(line)
    ax.set_global()
    ax.coastlines()
    ax.gridlines()
    
    x0, x1 = -1e6, 1.36e7
    y0, y1 = -9e6, 7.4e6
    bg = mpatch.PathPatch(mpath.Path([[x0, y0], [x0, y1], 
                                      [x1, y1], [x1, y0], 
                                      [x0, y0], ],
                                     closed=True),
                          transform=ax.transData, 
                          color='coral', alpha=0.5, clip_on=False
                          )
    
    # interpolate, as we only have a few sample points otherwise.
    path = line.get_path().interpolated(1000)
    bg = ax.background_patch
    bg_path = bg.get_path()
    bg_path = bg_path.clip_to_bbox(mtrans.Bbox([[x0, y0], [x1, y1]]))
    bg_path = (bg.get_transform() - ax.transAxes).transform_path(bg_path)
    clipped_bg = mpatch.PathPatch(bg_path,
                          transform=ax.transAxes, 
                          color='red', alpha=0.5, clip_on=False
                          )
    ax.add_patch(clipped_bg)
        
    
    import line_snap
    new = line_snap.horiz_snap_path_to_patch_if_outside(path, clipped_bg)
    new = mpath.Path(new)
    new = (ax.transAxes - target_label_cs._as_mpl_transform(ax)).transform_path(new)
#    print new
    print clipped_bg
    snapped = mpatch.PathPatch(new,
                               transform=target_label_cs, 
                               facecolor='none', edgecolor='green',
                               lw=4)
    ax.add_patch(snapped)
    
    tick_locs = [-90, -45, 0, 45, 90]
    tick_locs = range(-90, 90, 2)
    
    for tick_loc in tick_locs:
        try:
            r = where_on_path(new, y=tick_loc)
            plt.plot(r[0], r[1], 'ob', transform=target_label_cs)
        except ValueError:
#            print 'not crossed:', tick_loc
            pass
    
    plt.show()


def case3():
    target_label_cs = ccrs.PlateCarree()
    proj = ccrs.NorthPolarStereo()
    ax = plt.axes(projection=proj)
    
    line = mlines.Line2D([-180, 180], [0, 0], transform=target_label_cs)
    
    ax.add_line(line)
    ax.set_global()
    ax.coastlines()
    ax.gridlines()
    
    x0, x1 = 0, 0.58
    y0, y1 = 0, 1# XXX bug? 0.5

    path = (target_label_cs._as_mpl_transform(ax) - ax.transAxes).transform_path(line.get_path())
    
    bg = ax.background_patch
    bg_path = bg.get_path()
    bg_path = (bg.get_transform() - ax.transAxes).transform_path(bg_path)
    bg_path = bg_path.clip_to_bbox(mtrans.Bbox([[x0, y0], [x1, y1]]))
    clipped_bg = mpatch.PathPatch(bg_path,
                          transform=ax.transAxes, 
                          color='red', alpha=0.5, clip_on=False
                          )
    ax.add_patch(clipped_bg)
        
    
    import line_snap
    new = line_snap.horiz_snap_path_to_patch_if_outside(path, clipped_bg)
    print new
    new = mpath.Path(new)
    new = (ax.transAxes - target_label_cs._as_mpl_transform(ax)).transform_path(new)
#    print new
    print clipped_bg
    snapped = mpatch.PathPatch(new,
                               transform=target_label_cs, 
                               facecolor='none', edgecolor='green',
                               lw=4)
    ax.add_patch(snapped)
    
    tick_locs = [-90, -45, 0, 45, 90]
    tick_locs = range(-1800, 180, 2)
    
    for tick_loc in tick_locs:
        try:
            r = where_on_path(new, x=tick_loc)
#            print len(r[0])
            # XXX Sort by furthest from center
#            plt.plot(r[0][0], r[1][0], 'ob', transform=target_label_cs)
        except ValueError:
#            print 'not crossed:', tick_loc
            pass
    
    plt.show()



def case4():
    target_label_cs = ccrs.PlateCarree()
    proj = ccrs.NorthPolarStereo()
    ax = plt.axes(projection=proj)
    

    ax.set_global()
    ax.coastlines()
    ax.gridlines()
    
    x0, x1 = 0, 0.58
    y0, y1 = 0, 0.4
    ax_bbox = mtrans.Bbox([[x0, y0], [x1, y1]])

    bg = ax.background_patch
    bg_path = bg.get_path()
    bg_path = (bg.get_transform() - ax.transAxes).transform_path(bg_path)
    bg_path = bg_path.clip_to_bbox(mtrans.Bbox([[x0, y0], [x1, y1]]))
    clipped_bg = mpatch.PathPatch(bg_path,
                          transform=ax.transAxes, 
                          color='red', alpha=0.5, clip_on=False
                          )
    ax.add_patch(clipped_bg)
    
    cmap = plt.get_cmap('hot')
    
    path_lengths = []
    paths = []
    angles = []
    for i in np.linspace(0., np.pi * 2, 360):
        x = np.sin(i) * proj.x_limits[1]
        y = np.cos(i) * proj.y_limits[1]
        p = mpath.Path([[0, 0], [x, y]]).interpolated(20)
        p = (proj._as_mpl_transform(ax) - ax.transAxes).transform_path(p)
        
        try:
            p = p.clip_to_bbox(ax_bbox)
        except ValueError:
            continue
#        print p.vertices.max()
#        print np.rad2deg(i), len(p.vertices), p.vertices.max() - p.vertices.min()
        size = (p.vertices[-2, 0] - p.vertices[0, 0]) ** 2 + \
                (p.vertices[-2, 1] - p.vertices[0, 1]) ** 2

        path_lengths.append(size)
        paths.append(p)
        angles.append(np.rad2deg(i))
        
#        ax.add_patch(mpatch.PathPatch(p, facecolor='none', 
#                                         edgecolor=cmap(size / 1.0),
#                                         transform=ax.transAxes, clip_on=False,
#                                         )
#                      )
#        plt.text(p.vertices[-2, 0], p.vertices[-2, 1], 
#                 '{:g} {:g}'.format(size, np.rad2deg(i)), 
#                 transform=ax.transAxes)
    
#    plt.close()
#    plt.plot(path_lengths)
#    plt.show()

    # XXX add a heuristic to pick the most desirable angle
    longest = max(path_lengths)
    import itertools
    longest = sorted(itertools.izip(*[paths, path_lengths, angles]), 
                          key=lambda (path, size, angle): ((longest - size) > 0.1))[0]
    
    new = (ax.transAxes - target_label_cs._as_mpl_transform(ax)).transform_path(longest[0])

    ax.add_patch(mpatch.PathPatch(new, facecolor='none', 
                                         edgecolor=cmap(size / 1.0),
                                         transform=target_label_cs, clip_on=False,
                                         )
                      )
    
    tick_locs = range(-90, 90, 2)
    
    for tick_loc in tick_locs:
        try:
            r = where_on_path(new, y=tick_loc)
            plt.plot(r[0][0], r[1][0], 'ob', transform=target_label_cs)
        except ValueError:
#            print 'not crossed:', tick_loc
            pass

    plt.show()




if __name__ == '__main__':
#    case1()
#    case2()
#    case3()
    
    case4()
