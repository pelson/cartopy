
def display_segment(segment, **kwargs):
    x, y = [], []
    for vert in segment:
        if vert is not Ellipsis:
            x.append(vert[0])
            y.append(vert[1])
    return plt.plot(x, y, **kwargs)

class Vertex(object):
    def __init__(self, p0, p1, prev_vertex, exclude):
        self.p0, self.p1 = p0, p1
        self.prev_vertex = prev_vertex
        if prev_vertex is not None:
            prev_vertex.next_vertex = self
        self.exclude = exclude

    def set_next(self, next_vertex):
        self.next_vertex = next_vertex
        next_vertex.prev_vertex = self

    def walk(self):
        next_vertex = self.next_vertex
        while next_vertex is not self:
            yield next_vertex
            next_vertex = next_vertex.next_vertex


def pc_to_spherical(polygon):
    # XXX Because we are using 180 everywhere, the polygon
    # should come with a xy to spherical fn.
    rings = []
    for ring in polygon:
        rings.extend(cut_segments(ring))
    return join_open_rings(rings)

def cut_segments(segments):
    # Essentially removes the pole from a polygon, and
    # splits a filled middle -180 -> 180 into two rings
    # of opposite direction. A more effective algorithm almost
    # certainly exists!

    # 1. INPUT GEOMETRY ORDER MUST BE CONSTANT FOR A CRS.
    # 2. I'VE NOT EVEN THOUGHT ABOUT COMPLEXT GEOMETRIES (imagine
    #    a figure of 8 containing both poles)
    
    prev_vertex = None
    first_vertex = None

    bad_seen = good_seen = False

    n = len(segments)
    for i in range(n):
        p0, p1 = segments[i % n], segments[(i + 1) % n]
        bad = False
        if ((p0[0] == p1[0] and p1[0] in [-180, 180]) or
                (p0[1] == p1[1] and p1[1] in [-90, 90])):
            bad = True
            bad_seen = True
        else:
            bad = False
            good_seen = True

        vertex = Vertex(p0, p1, prev_vertex, bad)
        if first_vertex is None:
            first_vertex = vertex
        prev_vertex = vertex

    first_vertex.prev_vertex = vertex
    vertex.next_vertex = first_vertex

    if not good_seen:
        # XXX Return a sphere. (Ellipsis?)
        return []
    elif not bad_seen:
        # No bad segments - just return the segments
        return [segments]

    result = []
    ring = []

    # Pick the first "bad" vertex as a starting point.
    # We know there is at least one of them.
    for vertex in first_vertex.walk():
        if vertex.exclude:
            first_vertex = vertex
            break

    start_vertex = None

    import itertools
    for vertex in itertools.chain(first_vertex.walk(), [first_vertex]):
        if vertex.exclude:
            if start_vertex is not None:
                ring.append(Ellipsis)
                start_vertex = None
        else:
            if start_vertex is None:
                start_vertex = vertex
                ring = [vertex.p0]
                result.append(ring)
            ring.append(vertex.p1)
        prev_vertex = vertex

    return result


def spherical_equal(p0, p1):
    # TODO: Accept a fn which converts to spherical.
    if (p0[0] + 720) % 360 == (p1[0] + 720) % 360:
        return p0[1] == p1[1]
    else:
        return False


def join_open_rings(in_rings):
    rings = []
    open_rings = []
    for ring in in_rings:
#         if not spherical_equal(ring[0], ring[-1]):
        if not (ring[-1] is Ellipsis or
                spherical_equal(ring[0], ring[-1])):
            open_rings.append(ring)
        else:
            rings.append(ring)

    while open_rings:
        target_ring = open_rings.pop(0)
        for ring in open_rings:
            # If the first == last and last == first of both
            # rings, then match them up.
            if (spherical_equal(target_ring[0], ring[-1]) and
                    spherical_equal(target_ring[-1], ring[0])):
                open_rings.remove(ring)
                ring = target_ring + [Ellipsis] + ring + [Ellipsis]
                rings.append(ring)
                break
        else:
            print 'No matching rings found.'
            # XXX Close them again?
            rings.append(target_ring + target_ring[0:1])
    return rings
    

from nose.tools import assert_equal
import numpy as np

class Test_cut_segments(object):
    def test_fill_middle(self):
        expected = [[(-180, 20), (0, 30), (180, 20), Ellipsis],
                    [(180, -80), (0, -80), (-180, -80), Ellipsis]]
        bottom = -80
        right = 180
        segment = [(-right, bottom), (-right, 20),
                   (0, 30),
                   (right, 20),
                   (right, 0),
                   (right, bottom),
                   (0, bottom),
                   (-right, bottom)]
        for i in range(len(segment)):
            s = np.roll(segment, i, axis=0)
            result = self.un_numpy(cut_segments(s))
            assert_equal(expected, sorted(result))
    
    def un_numpy(self, segments):
        return [[tuple(pair) if pair is not Ellipsis else Ellipsis
                 for pair in seg]
                      for seg in segments]
    
    def test_no_bad(self):
        # Identity.
        bottom = -80
        right = 170
        segment = [(-right, bottom), (-right, 20),
                   (0, 30),
                   (right, 20),
                   (right, 0),
                   (right, bottom),
                   (0, bottom),
                   (-right, bottom)]
        for i in range(len(segment)):
            s = np.roll(segment, i, axis=0)
            result = self.un_numpy(cut_segments(s))
            assert_equal(sorted(result), 
                         self.un_numpy([s]))

    def test_no_good(self):
        r = cut_segments([(-180, -90), (-180, 0), (-180, 90),
                          (0, 90), (180, 90), (180, -90), (-180, -90)])
        assert_equal(r, [])
    
    def test_two_sides(self):
        r = cut_segments([(-180, -90), (-180, 0), (-180, 90),
                          (0, 90), (180, 90), (180, -90), (-180, -90)])
        assert_equal(r, [])


class Test_join_open_rings(object):
    def test_two_open(self):
        rings = [[(180, -30), (70, -30), (70, -60), (180, -60)],
                 [(-180, -60), (-70, -60), (-70, -30), (-180, -30)]]
        expected = [[(180, -30), (70, -30), (70, -60), (180, -60), Ellipsis,
                     (-180, -60), (-70, -60), (-70, -30), (-180, -30),
                     Ellipsis]]
        result = join_open_rings(rings)
        assert_equal(expected, result)
    
    def test_no_open(self):
        # Closed rings stay closed.
        # XXX TODO This needs to handle ellipsis.
        rings = [[(-180, -30), (0, -30), (180, -30), (180, -30)]]
        result = join_open_rings(rings)
        assert_equal(rings, result)
        
    def test_one_open(self):
        # One open ring just gets closed.
        rings = [[(180, -30), (70, -30), (70, -60), (180, -60)]]
        expected = [rings[0] + rings[0][0:1]]
        result = join_open_rings(rings)
        assert_equal(expected, result)

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-s'], exit=False)

    import matplotlib.pyplot as plt

    bottom = -80
    right = 180
    segment = [
                (-right, bottom), (-right, 20),
                (0, 30),
                (right, 20),
                (right, 0),
                (right, bottom),
                (0, bottom),
                (-right, bottom),
               ]

    segments = np.roll(segment, 3, axis=0)
    rings = cut_segments(segments)
#     print segments[0:2, ]

    spherical = pc_to_spherical([segment])
    print spherical
    exit()

    display_segment(segment, color='blue', linestyle='', lw=5,
                    marker='o', markersize=25)
    for ring in rings:
        display_segment(ring, color='r')
        print ring
    plt.gca().margins(0.2)
    plt.gcf().canvas._master.geometry('336x852+952+22')
    plt.show()

# from nose.tools import assert_equal
#
# import shapely.geometry as sgeom
#
# def fix_topology(polygons):
#     for polygon in polygons:
#         if polygon.contains(sgeom.Point(90, 0)):
#             if polygon
#
# def tests():
#     box = sgeom.box(-180, -90, 180, 90)
#     assert_equal(fix_topology([box]), False)
#
# if __name__ == '__main__':
#     import nose
#     nose.runmodule(argv=['-s'], exit=False)