from __future__ import division

import numpy as np

import matplotlib.lines as mlines
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

import cartopy.crs as ccrs

def snap_line_to_patch(line, patch):
    """
    Return a line which is a version of the given line snapped to the nearest 
    horizontal (TODO vertical) point on the given patch.
    
    NOTE: Transforms currently should be the same for line and patch.
    Does not support complex lines with curves or breaks.
    
    The resulting line may jump around the patch, particularly for patches which
    have repeating x or y coordinates (such as a circle).
    
    No interpolation is done - the resulting line has the same resolution as the given line.
    
    """
    from positioner import where_on_line
    
    
    patch_line = mlines.Line2D([0], [0], transform=patch.get_transform())
    patch_path = (patch.get_transform() - line.get_transform()).transform_path(patch.get_path())
    patch_line.set_xdata(patch_path.vertices[:, 0])
    patch_line.set_ydata(patch_path.vertices[:, 1])
    
    coords = []
    for x, y in line.get_path().vertices:
        try:
            xs, ys = where_on_line(patch_line, y=y)
            ind = np.abs(xs - x).argmin()
            xy = [xs[ind], ys[ind]]
        except ValueError:
            continue
        coords.append(xy)
    
    return coords
    


def horiz_snap_path_to_patch_if_outside(path, patch):
    """
    Return a path.
    
    Path and patch must be on same CS.
    
    """
    from positioner import where_on_line
    
    patch_line = mlines.Line2D([0], [0], transform=patch.get_transform())
    patch_path = patch.get_path()
    patch_line.set_xdata(patch_path.vertices[:, 0])
    patch_line.set_ydata(patch_path.vertices[:, 1])
    
    from collections import namedtuple
    event_mock = namedtuple('event_mock', 'x, y')
    coords = []
    for x, y in path.vertices:
        if patch.get_path().contains_point([x, y]):
            xy = [x, y]
        else:
            
#            print 'does not contain', tx, ty, patch.get_path()
            try:
                xs, ys = where_on_line(patch_line, y=y)
                ind = np.abs(xs - x).argmin()
                xy = [xs[ind], ys[ind]]
            except ValueError:
                # TODO if this is  the first non-snappable point, interpolate to the end of hte line segment
                continue
        coords.append(xy)
    
    return coords



def snap_line_to_patch_if_necessary(line, patch, outline_patch):
    from positioner import where_on_line
    
    patch_line = mlines.Line2D([0], [0], transform=patch.get_transform())
    patch_path = (patch.get_transform() - line.get_transform()).transform_path(patch.get_path())
    patch_line.set_xdata(patch_path.vertices[:, 0])
    patch_line.set_ydata(patch_path.vertices[:, 1])
    
    from collections import namedtuple
    event_mock = namedtuple('event_mock', 'x, y')
    coords = []
    for x, y in line.get_path().vertices:
        tx, ty = line.get_transform().transform_point([x, y])
        p_event = event_mock(tx, ty)
        print p_event, outline_patch.contains(p_event)
        
        if outline_patch.contains(p_event)[0]:
            print 'outline contains:', p_event, outline_patch
            xy = [x, y]
        else:
            try:
                xs, ys = where_on_line(patch_line, y=y)
                ind = np.abs(xs - x).argmin()
                xy = [xs[ind], ys[ind]]
            except ValueError:
                continue
        coords.append(xy)
    
    return coords


def main():
    ax = plt.axes()
    ax.set_xlim([5, 12])
    ax.set_ylim([-15, -5])
    p = mpatches.CirclePolygon([10, -10], 3, resolution=15, alpha=0.5, facecolor='coral')
    ax.add_patch(p)
    
    
    xs = np.array([7, 6, 8, 8, 8]) + 6
    ys = [-8, -9, -10, -12, -14]
    line = mlines.Line2D(xs, ys)
    ax.add_line(line)
    
    r = snap_line_to_patch_if_necessary(line, p, ax.patch)
    print r
    plt.plot(*zip(*r), lw=10, color='red', alpha=0.25)
    
    
    #patch_line = mlines.Line2D([0], [0], transform=p.get_transform())
    #patch_path = p.get_path()
    #condition = patch_path.vertices[:, 0] < 0
    #patch_line.set_xdata(patch_path.vertices[condition, 0])
    #patch_line.set_ydata(patch_path.vertices[condition, 1])
    #
    #ax.add_line(patch_line)
    #
    #r = snap_line_to_patch(line, patch_line)
    #plt.plot(*zip(*r), lw=10, color='red', alpha=0.25)
    
    plt.show()
    
def main2():
    ax = plt.axes()
    ax.set_xlim([5, 15])
    ax.set_ylim([-15, -5])
    p = mpatches.CirclePolygon([10, -10], 3, resolution=15, alpha=0.5, facecolor='coral')
    ax.add_patch(p)
    
    
    xs = np.array([7, 6, 8, 8, 8]) + 3
    ys = [-8, -9, -10, -12, -14]
    line = mlines.Line2D(xs, ys)
    ax.add_line(line)
    
    r = snap_line_to_patch(line, p)
    print r
    plt.plot(*zip(*r), lw=10, color='red', alpha=0.25)
    plt.show()


if __name__ == '__main__':
    ax = plt.axes(projection=ccrs.Robinson())
    ax.coastlines()
    ax.gridlines()
    
    def on_move(event):
#        print event
        print bool(ax.outline_patch.contains(event)[0])
    
    ax.figure.canvas.mpl_connect('motion_notify_event', on_move)
    
    plt.show()
#    main()