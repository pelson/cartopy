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
            return [[p0, self.p0, 'PLACEHOLDER'],
                    ['PLACEHOLDER', self.p0, p1]]
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
                return [[p0, r, 'PLACEHOLDER'],
                        ['PLACEHOLDER', r, p1]]
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
        cline = sgeom.LineString(self.line)
        if cline.contains(ls):
            return [self.p0]
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


if __name__ == '__main__':
#     # Single point intersection.
#     print handle_segment([0, 80], [0, 100],
#                          [PointToLine([0, 90], [[-180, 90], [180, 90]])])
# 
#     # Single point intersection.
#     print handle_segment([-190, 80], [-170, 70],
#                          [CutLine([[-180, -90], [-180, 90]])])
# 
#     # Single point intersection.
#     print handle_segment([170, 20], [190, 10],
#                          [CutLine([[180, -90], [180, 90]])])
# 
#     # Along cut line.
#     print handle_segment([-180, 60], [-180, 80],
#                          [CutLine([[-180, -90], [-180, 90]])])
# 
#     # No impact.
#     print handle_segment([-160, 60], [-150, 80],
#                          [CutLine([[-180, -90], [-180, 90]])])

    # Single point intersection.
    print handle_inverse_segment([10, 90], [40, 90],
                                 [PointToLine([0, 90], [[-180, 90], [180, 90]])])

    print handle_inverse_segment([10, 90], [40, 90],
                                 [CutLine([[-180, 90], [180, 90]])])


