from __future__ import division

import numpy as np

#import matplotlib.lines as mlines
#import matplotlib.path as mpath
#import matplotlib.pyplot as plt

#ax = plt.axes()
#
#l = mlines.Line2D([0, 0, 2, 3, 3, 2], [10, 20, 30, 40, 50, 20], transform=ax.transData)
#
#ax.add_line(l)
#ax.set_ylim([0, 70])
#ax.set_xlim([-1, 4])
#
#
#p = l.get_path()


def where_on_line(line, x=None, y=None, xy_trans=None):
    if xy_trans is None or xy_trans == line.get_transform():
        path_in_xy_trans = line.get_path()
    else:
        path_in_xy_trans = (line.get_transform() - xy_trans).transform_path(line.get_path()) 

    return where_on_path(path_in_xy_trans, x=x, y=y)


def where_on_path(path_in_xy_trans, x=None, y=None):
    """
    Returns the coordinates (in xy_trans coordinates) of a point which intersects the 
    given x or y coordinate.
    
    Args:
    
     * line - the line to find a point on
     
    Kwargs
    
     * x or y - the x or y coordinate desired of the returned point
     * xy_trans - the transform of the given x or y coordinate, and the
                  coordinate system to return the point in. If none, the
                  transform from the line is used.

    .. note::
    
        Does not currently handle lines with curves or breaks.
        
        There may be repeated values (if the line is closed or self intersecting)
        
    """
    if x is not None != y is not None:
        raise ValueError('X xor Y must be set.')
    
    if x is not None:
        x = float(x)
        intersections = np.where(np.diff(np.sign(path_in_xy_trans.vertices[:, 0] - x)) != 0)[0]
        if intersections.size > 0:
            intersection = intersections[0]
            c0, c1 = path_in_xy_trans.vertices[intersections, :], path_in_xy_trans.vertices[intersections + 1, :]
            # Figure out the equation of the line in the form ``y = mx + c``.
            m = (c1[:, 1] - c0[:, 1]) / (c1[:, 0] - c0[:, 0])
            c = c0[:, 1] - m * c0[:, 0]
            
            y = m * x + c
            y = np.unique(y)
            return [np.repeat(x, y.size), y]
        else:
            raise ValueError('The x value {} was not crossed by the given line.'.format(x))

    else:
        y = float(y)
        intersections = np.where(np.diff(np.sign(path_in_xy_trans.vertices[:, 1] - y)) != 0)[0]#
        if intersections.size > 0:
            intersection = intersections[0]
            # c0 represents [x0s, y0s] c1: [x1s, y1s]
            c0, c1 = path_in_xy_trans.vertices[intersections, :], path_in_xy_trans.vertices[intersections + 1, :]
            
            # Any vertical lines for which it is not possible to calculate a gradient,
            # add an arbitrary value to the x coordinates to avoid a numpy warning - the
            # final value itself will be substituted in from the c0 x array.
            vert_line = c1[:, 0] == c0[:, 0]
            if np.any(vert_line):
                c1[vert_line, 0] += 1

            # Figure out the equation of the line in the form ``y = mx + c``.
            m = (c1[:, 1] - c0[:, 1]) / (c1[:, 0] - c0[:, 0])
            c = c0[:, 1] - m * c0[:, 0]
            
            x = (y - c) / m
            x[vert_line] = c0[vert_line, 0]
            x = np.unique(x)
            return [x, np.repeat(y, x.size)]
        else:
            raise ValueError('The y value {} was not crossed by the given line.'.format(y))
    
        

#xy = where_on_line(l, x=0.75, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, x=0.25, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, x=0.5, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, y=0.5, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, y=0.25, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)


#print where_on_line(l, x=1, xy_trans=ax.transData)
#print where_on_line(l, x=0, xy_trans=ax.transData)
#print where_on_line(l, x=3, xy_trans=ax.transData)
#print where_on_line(l, x=5, xy_trans=ax.transData)
#print where_on_line(l, x=2.5, xy_trans=ax.transData)
#
#
#print where_on_line(l, y=0, xy_trans=ax.transData)
#print where_on_line(l, y=10, xy_trans=ax.transData)
#print where_on_line(l, y=25, xy_trans=ax.transData)
#print where_on_line(l, y=50, xy_trans=ax.transData)
#print where_on_line(l, y=55, xy_trans=ax.transData)


#
#import matplotlib.patches as mpatches
#import matplotlib.path as mpaths
#import matplotlib.lines as mlines
#import matplotlib.pyplot as plt
##
##ax = plt.axes()
##ax.set_xlim([5, 15])
##ax.set_ylim([-15, -5])
##p = mpatches.CirclePolygon([10, -10], 3, resolution=15, alpha=0.5, facecolor='coral')
##ax.add_patch(p)
##
##patch_line = mlines.Line2D([0], [0], transform=ax.transData)
##patch_path = p.get_path()
##patch_path = (p.get_transform() - ax.transData).transform_path(patch_path)
##condition = patch_path.vertices[:, 0] != np.nan
##patch_line.set_xdata(patch_path.vertices[condition, 0])
##patch_line.set_ydata(patch_path.vertices[condition, 1])
##ax.add_line(patch_line)
##
##
##print where_on_line(patch_line, x=10)
##
##print where_on_line(patch_line, y=-10)
##print where_on_line(patch_line, y=-7)
##
##
##
##line = mlines.Line2D([-12, -11, -10, -10, -10, -14], 
##                     [7, 8, 8, 7, 6, 9],
##                     transform=ax.transData)
##ax.add_line(line)
##
##
##print where_on_line(line, x=-10)
##
##
##
##line = mlines.Line2D([7, 8, 8, 6, 9], 
##                     [-12, -11, -10, -10, -14],
##                     transform=ax.transData)
##ax.add_line(line)
##
##
##print where_on_line(line, y=-10)
###plt.show()
##
##
#
#ax = plt.axes()
## make sensible limits for the axes
#ax.set_ylim([0, 70])
#ax.set_xlim([-1, 4])
#
#line = mlines.Line2D([0, 0, 2, 3, 3, 2], 
#                          [10, 20, 30, 40, 50, 20],
#                          transform=ax.transData) 
#ax.add_line(line)
#xy = where_on_line(line, y=0.25, xy_trans=ax.transAxes)
#print xy
#plt.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
##
#plt.show()
