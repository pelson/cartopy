from __future__ import division

import matplotlib
import matplotlib.path as mpath
from matplotlib._path import clip_path_to_rect
import numpy as np


def clip_path_mpl(path, bbox):
    """
    Clip the given path to the given bounding box.

    Uses :func:`matplotlib._path.clip_path_to_rect` which has a
    bug before matplotlib v1.2.1 meaning it cannot be used before
    that release.

    """
    resultant_verts = clip_path_to_rect(path, bbox, True)

    if len(resultant_verts) == 0:
        path = mpath.Path([[0, 0]], codes=[mpath.Path.MOVETO])
    else:
        # Closed polygons going in to clip_path_to_rect are returned with
        # their final vertex missing. Add this back in if appropriate.
        if np.all(path.vertices[0, :] == path.vertices[-1, :]):
            for i, verts in enumerate(resultant_verts):
                resultant_verts[i] = np.append(verts, verts[0:1, :], axis=0)

        vertices = np.concatenate(resultant_verts)
        path = mpath.Path(vertices=vertices)

    return path


def clip_path_python(subject, clip, point_inside_clip_path):
    """
    Clip the subject path with the given clip path using the
    Sutherland-Hodgman polygon clipping algorithm.

    Args:

    * subject - The subject path to be clipped. Must be a simple, single
                polygon path with straight line segments only.
    * clip - The clip path to use. Must be a simple, single
             polygon path with straight line segments only.
    * point_inside_clip_path - a point which can be found inside the clip path
                               polygon.

    """
    inside_pt = point_inside_clip_path

    output_verts = subject.vertices

    for i in xrange(clip.vertices.shape[0] - 1):
        clip_edge = clip.vertices[i:i + 2, :]
        input_verts = output_verts
        output_verts = []
        inside = np.cross(clip_edge[1, :] - clip_edge[0, :],
                          inside_pt - clip_edge[0, :])

        s = input_verts[-1]

        for e in input_verts:
            e_clip_cross = np.cross(clip_edge[1, :] - clip_edge[0, :],
                                    e - clip_edge[0, :])
            s_clip_cross = np.cross(clip_edge[1, :] - clip_edge[0, :],
                                    s - clip_edge[0, :])

            if np.sign(e_clip_cross) == np.sign(inside):
                if np.sign(s_clip_cross) != np.sign(inside):
                    p = intersection_point(clip_edge[0, :], clip_edge[1, :],
                                           e, s)
                    output_verts.append(p)
                output_verts.append(e)
            elif np.sign(s_clip_cross) == np.sign(inside):
                p = intersection_point(clip_edge[0, :], clip_edge[1, :],
                                       e, s)
                output_verts.append(p)
            s = e

    if output_verts == []:
        path = mpath.Path([[0, 0]], codes=[mpath.Path.MOVETO])
    else:
        # If the subject polygon was closed, then the return should be too.
        if np.all(subject.vertices[0, :] == subject.vertices[-1, :]):
            output_verts.append(output_verts[0])
        path = mpath.Path(np.array(output_verts))
    return path


def intersection_point(p0, p1, p2, p3):
    """
    Return the intersection point of the two infinite lines that pass through
    point p0->p1 and p2->p3 respectively.

    """
    x_1, y_1 = p0
    x_2, y_2 = p1
    x_3, y_3 = p2
    x_4, y_4 = p3

    div = (x_1 - x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 - x_4)

    if div == 0:
        raise ValueError('Lines are parallel and cannot '
                         'intersect at any one point.')

    x = ((x_1 * y_2 - y_1 * x_2) * (x_3 - x_4) - (x_1 - x_2) * (x_3 *
         y_4 - y_3 * x_4)) / div
    y = ((x_1 * y_2 - y_1 * x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 *
         y_4 - y_3 * x_4)) / div

    return x, y

# Provide a clip_path function which follows the documentation of
# clip_path_mpl. Because of a bug before v1.2.1, we need to conditionally
# wrap clip_path_python with a shim.
clip_path = clip_path_mpl
if matplotlib.__version__ <= '1.2.1':
    try:
        import matplotlib.transforms as mtrans
        # Try calculating the clip path. If it runtime errors then
        # we have the still broken version.
        _ = clip_path_mpl(mpath.Path([[0, 0]]),
                          mtrans.Bbox([[0, 0], [1, 1]]))

    except RuntimeError:
        def clip_path(subject, clip_bbox):
            """A shim on clip_path_python to support Bbox path clipping."""
            bbox_patch = bbox_to_path(clip_bbox)
            bbox_center = ((clip_bbox.x0 + clip_bbox.x1) / 2,
                           (clip_bbox.y0 + clip_bbox.y1) / 2)
            return clip_path_python(subject, bbox_patch, bbox_center)


def lines_intersect(p0, p1, p2, p3):
    """
    Return whether the two lines defined by p0->p1 and p2->p3 intersect.
    """
    cp1 = np.cross(p1 - p0, p2 - p0)
    cp2 = np.cross(p1 - p0, p3 - p0)
    return np.sign(cp1) == np.sign(cp2) and cp1 != 0


def bbox_to_path(bbox):
    """
    Turn the given :class:`matplotlib.transforms.Bbox` instance into
    a :class:`matplotlib.path.Path` instance.

    """
    verts = np.array([[bbox.x0, bbox.y0], [bbox.x1, bbox.y0],
                      [bbox.x1, bbox.y1], [bbox.x0, bbox.y1],
                      [bbox.x0, bbox.y0]])
    return mpath.Path(verts)
