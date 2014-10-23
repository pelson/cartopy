"""
Algorithm for arbitrary geometry/path transformation from CRS to CRS.

 - Identify topology of source data to spherical
 - Identify topology of target CRS from spherical
 - Convert source geometry to pseudo-spherical
 - Convert pseudo-spherical geometry to pseudo-target geometry (preserving the undefined edges)
 - Apply interpolation to the pseudo-target geometry to form real geometries at arbitrary precision.

"""
import shapely.geometry as sgeom


class TopologyTransformation(object):
    def forward(self, p0, p1):
        """
        Takes the segment to the manifold that this
        transformation represents.
        
        """
        return None
    
    def inverse(self, p0, p1):
        """
        Takes the segment back from the manifold that
        this transformation represents.

        XXX We can't do this on a segment basis - we need to have more than one segment to re-join it!!!

        """
        return None

class PointToLine(TopologyTransformation):
    def __init__(self, p0, line):
        self.p0 = p0
        self.line = line

    def forward(self, p0, p1):
        # TODO: Use a spherical (i.e. great circle) intersection algorithm.
        import numpy as np
        c = np.array([p0, p1], dtype=float)
        ls = sgeom.LineString(c)
        if ls.intersects(sgeom.Point(self.p0)):
            return [[p0, self.p0],#, 'PLACEHOLDER'],
#                    ['PLACEHOLDER', 
                     [self.p0, p1]]
        else:
            return None# [[p0, p1]]

    def inverse(self, p0, p1):
        # TODO: Use a spherical (i.e. great circle) intersection algorithm.
        import numpy as np
        # dtype to deal with a shapely bug.
        c = np.array([p0, p1], dtype=float)
        ls = sgeom.LineString(c)
        cline = sgeom.LineString(self.line)
        if cline.contains(ls):
            return [self.p0]
        else:
            return None


class PointToPoint(TopologyTransformation):
    # Needed?
    pass

class LineToLine(TopologyTransformation):
    def __init__(self, cut_line, replacement_line):
        self.cut_line = cut_line
        self.replacement_line = replacement_line

    def forward(self, p0, p1):
        # TODO: Use a spherical (i.e. great circle) intersection algorithm.
        import numpy as np
        # dtype to deal with a shapely bug.
        c = np.array([p0, p1], dtype=float)
        ls = sgeom.LineString(c)
        cline = sgeom.LineString(self.cut_line)
        if ls.intersects(cline):
            intersection = ls.intersection(cline)
            if isinstance(intersection, sgeom.Point):
                r = [intersection.x, intersection.y]
                return [[p0, r,],
                        # 'PLACEHOLDER'],
#                        ['PLACEHOLDER', 
                         [r, p1]]
            else:
                # Verfiy this is just the exterior???
                return [[p0, p1]]
        else:
            return None
    
    def inverse(self, p0, p1):
        # TODO: Use a spherical (i.e. great circle) intersection algorithm.
        import numpy as np
        # dtype to deal with a shapely bug.
        c = np.array([p0, p1], dtype=float)
        ls = sgeom.LineString(c)
        rline = sgeom.LineString(self.replacement_line)
        if rline.intersects(ls):
            intersection = ls.intersection(rline)
            if isinstance(intersection, sgeom.Point):
                raise NotImplementedError()
            elif isinstance(intersection, sgeom.LineString):
                # XXX TODO: verify that the segment is a subset of the cut line.
                return ['PLACEHOLDER']
        else:
            return None

class CutLine(LineToLine):
    def __init__(self, line):
        LineToLine.__init__(self, line, line)


class PointToInfiniteExterior(TopologyTransformation):
    def __init__(self, p0):
        self.p0 = p0


class PlateCarree():
    def __init__(self):
        self.topology = [
                         # NOTE: The line depends on the projection parameters...
                         PointToLine([0, 90], [[-180, 90], [180, 90]]),
                         PointToLine([0, -90], [[-180, -90], [180, -90]]),
                         # Note: Line in Spherical coords.
                         CutLine([[180, -90], [180, 90]])
                         ]

class Robinson():
    def __init__(self):
        self.topology = [
                         # Note: Line in Spherical coords.
                         LineToLine([[180, -90], [180, 90]])
                         ]



class NPStereographic():
    def __init__(self):
        self.topology = [
                         PointToInfiniteExterior([0, 90])
                         ]


def handle_segment(p0, p1, topology):
    # Assume that topologies do not interfere with one another.
    # If they do, then we could just define a topology which
    # does a chained action anyway.
    for topo in topology:
        result = topo.forward(p0, p1)
        if result is not None:
            return result
    return None


def handle_inverse_segment(p0, p1, topology):
    # Assume that topologies do not interfere with one another.
    # If they do, then we could just define a topology which
    # does a chained action anyway.
    for topo in topology:
        result = topo.inverse(p0, p1)
        if result is not None:
            return result
    return None


def simple_cases():
#     # Single point intersection.
#     print handle_segment([0, 80], [0, 100],
#                          [PointToLine([0, 90], [[-180, 90], [180, 90]])])
# 
    # Single point intersection.
    print handle_segment([-190, 80], [-170, 70],
                         [CutLine([[-180, -90], [-180, 90]])])

#    # Single point intersection.
#    print handle_segment([170, 20], [190, 10],
#                         [CutLine([[180, -90], [180, 90]])])
#
#    # Along cut line.
#    print handle_segment([-180, 60], [-180, 80],
#                         [CutLine([[-180, -90], [-180, 90]])])
#
#    # No impact.
#    print handle_segment([-160, 60], [-150, 80],
#                         [CutLine([[-180, -90], [-180, 90]])])

    # Single point intersection.
    print handle_inverse_segment([10, 90], [40, 90],
                                 [PointToLine([0, 90], [[-180, 90], [180, 90]])])

    print handle_inverse_segment([-180, 40], [-180, 55],
                                 [CutLine([[-180, -90], [-180, 90]])])


import numpy as np


def crosses_antipodal_line(p0, p1, xy_to_spherical):
    x0, x1 = p0[0], p1[0]

    x0_gt_x1 = x0 > x1

    if x0 == x1:
        return False
    else:
        orig_direction = (x1 - x0) / 2

    sp0 = xy_to_spherical(*p0)
    sp1 = xy_to_spherical(*p1)

    sx0, sx1 = sp0[0], sp1[0]

    sx0_gt_sx1 = sx0 > sx1

    if sx0 == sx1:
        raise ValueError('Full circle?')
    else:
        new_direction = (sx1 - sx0) / 2

    if sx0_gt_sx1 != x0_gt_x1:
        return new_direction != orig_direction
    else:
        return new_direction == orig_direction


if __name__ == '__main__':
#    simple_cases()

    import cartopy.crs as ccrs
    from functools import partial

    pc_to_spherical = partial(ccrs.Geodetic().transform_point, src_crs=ccrs.PlateCarree())
    # XXX TODO: test perfect sphere transform.

    p0 = (170, 0)
    p1_crosses = (190, 0)
    p1_same_side = (-170, 0)
    p0_plus_360 = (170 + 360, 0)

    assert crosses_antipodal_line(p0, p1_crosses, pc_to_spherical) == True
    assert crosses_antipodal_line(p1_crosses, p0, pc_to_spherical) == True

    assert crosses_antipodal_line(p0, p1_same_side, pc_to_spherical) == False
    assert crosses_antipodal_line(p1_same_side, p0, pc_to_spherical) == False

    assert crosses_antipodal_line(p0, p0_plus_360, pc_to_spherical) == True
    assert crosses_antipodal_line(p0_plus_360, p0, pc_to_spherical) == True

    assert crosses_antipodal_line(p0, p0, pc_to_spherical) == False

    pc_to_spherical = partial(ccrs.Geodetic().transform_point, src_crs=ccrs.PlateCarree(central_longitude=180))

    p0 = (-10, 0)
    p1_crosses = (10, 0)
    p1_same_side = (-350, 0)
    p0_plus_360 = (-10 + 360, 0)

    assert crosses_antipodal_line(p0, p1_crosses, pc_to_spherical) == True
    assert crosses_antipodal_line(p1_crosses, p0, pc_to_spherical) == True

    assert crosses_antipodal_line(p0, p1_same_side, pc_to_spherical) == False
    assert crosses_antipodal_line(p1_same_side, p0, pc_to_spherical) == False

    assert crosses_antipodal_line(p0, p0_plus_360, pc_to_spherical) == True
    assert crosses_antipodal_line(p0_plus_360, p0, pc_to_spherical) == True

    assert crosses_antipodal_line(p0, p0, pc_to_spherical) == False

