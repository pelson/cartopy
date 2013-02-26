from __future__ import division

import numpy as np


class Positioner(object):
    pass



def where_on_line(line, x=None, y=None, xy_trans=None):
    if xy_trans is None or xy_trans == line.get_transform():
        path_in_xy_trans = line.get_path()
    else:
        path_in_xy_trans = (line.get_transform() - xy_trans).transform_path(line.get_path()) 

    return where_on_path(path_in_xy_trans, x=x, y=y)


def where_on_path(path_in_xy_trans, x=None, y=None):
    """
    Returns the coordinates (in xy_trans coordinates) of a point which intersects the 
    given x or y coordinate on the given line.
    
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
