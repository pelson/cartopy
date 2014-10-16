# -*- coding: utf-8 -*-
"""Efficient Clipping of Arbitrary Polygons

Based on the paper "Efficient Clipping of Arbitrary Polygons" by Günther
Greiner and Kai Hormann, ACM Transactions on Graphics
1998;17(2):71-83.

Available at: http://www.inf.usi.ch/hormann/papers/Greiner.1998.ECO.pdf

You should have received the README file along with this program.
If not, see <https://github.com/helderco/polyclip>
"""


class Vertex(object):
    """Node in a circular doubly linked list.

    This class is almost exactly as described in the paper by Günther/Greiner.
    """
    def __init__(self, vertex, alpha=0.0, intersect=False, entry=True, checked=False, degen=False):
        if isinstance(vertex, Vertex):
            vertex = (vertex.x, vertex.y)
            # checked = True

        self.x, self.y = vertex     # point coordinates of the vertex
        self.next = None            # reference to the next vertex of the polygon
        self.prev = None            # reference to the previous vertex of the polygon
        self.neighbour = None       # reference to the corresponding intersection vertex in the other polygon
        self.entry = entry          # True if intersection is an entry point, False if exit
        self.degen = degen
        self.alpha = alpha          # intersection point's relative distance from previous vertex
        self.intersect = intersect  # True if vertex is an intersection
        self.checked = checked      # True if the vertex has been checked (last phase)

    def isInside(self, poly):
        if testLocation(self, poly) in ("in","on"):
            return True
        else: return False

    def setChecked(self):
        self.checked = True
        if self.neighbour and not self.neighbour.checked:
            self.neighbour.setChecked()

    def __repr__(self):
        """String representation of the vertex for debugging purposes."""
        return "(%.2f, %.2f) <-> %s(%.2f, %.2f)%s <-> (%.2f, %.2f) %s" % (
            self.prev.x, self.prev.y,
            'i' if self.intersect else ' ',
            self.x, self.y,
            ('e' if self.entry else 'x') if self.intersect else ' ',
            self.next.x, self.next.y,
            ' !' if self.intersect and not self.checked else ''
            )


class Polygon(object):
    """Manages a circular doubly linked list of Vertex objects that represents a polygon."""

    def __init__(self):
        self.first = None

    def add(self, vertex):
        """Add a vertex object to the polygon (vertex is added at the 'end' of the list")."""
        if not self.first:
            self.first = vertex
            self.first.next = vertex
            self.first.prev = vertex
        else:
            next = self.first
            prev = next.prev
            next.prev = vertex
            vertex.next = next
            vertex.prev = prev
            prev.next = vertex

    def replace(self, old, new):
        new.next = old.next
        new.prev = old.prev
        old.prev.next = new
        old.next.prev = new
        if old is self.first:
            self.first = new

    def insert(self, vertex, start, end):
        """Insert and sort a vertex between a specified pair of vertices.

        This function inserts a vertex (most likely an intersection point)
        between two other vertices (start and end). These other vertices
        cannot be intersections (that is, they must be actual vertices of
        the original polygon). If there are multiple intersection points
        between the two vertices, then the new vertex is inserted based on
        its alpha value.
        """
        curr = start
        while curr != end and curr.alpha < vertex.alpha:
            curr = curr.next

        vertex.next = curr
        prev = curr.prev
        vertex.prev = prev
        prev.next = vertex
        curr.prev = vertex

    def next(self, v):
        """Return the next non intersecting vertex after the one specified."""
        c = v
        while c.intersect:
            c = c.next
        return c

    @property
    def nextPoly(self):
        """Return the next polygon (pointed by the first vertex)."""
        return self.first.nextPoly

    @property
    def first_intersect(self):
        """Return the first unchecked intersection point in the polygon."""
        for v in self.iter():
            if v.intersect and not v.checked:
                break
        return v

    @property
    def points(self):
        """Return the polygon's points as a list of tuples (ordered coordinates pair)."""
        p = []
        for v in self.iter():
            p.append((v.x, v.y))
        return p

    def unprocessed(self):
        """Check if any unchecked intersections remain in the polygon."""
        for v in self.iter():
            if v.intersect and not v.checked:
                yield True

    def __repr__(self):
        """String representation of the polygon for debugging purposes."""
        count, out = 1, "\n"
        for s in self.iter():
            out += "%02d: %s\n" % (count, str(s))
            count += 1
        return out

    def iter(self):
        """Iterator generator for this doubly linked list."""
        s = self.first
        while True:
            yield s
            s = s.next
            if s == self.first:
                return


class Clipper(object):
    def __init__(self, subject, clip):
        self.subject = subject
        self.clip = clip

        # prep by removing repeat of startpoint at end
        first = subject.first
        last = first.prev
        if last.x == first.x and last.y == first.y:
            first.prev = last.prev
            last.prev.next = first
        first = clip.first
        last = first.prev
        if last.x == first.x and last.y == first.y:
            first.prev = last.prev
            last.prev.next = first
    
    def do_it(self):
        polygons = self.phase_one(self.clip)
        if polygons is None:
            self.phase_two()
            polygons = self.phase_three()
        
        return self.hole_handler(polygons)
        
    def hole_handler(self, polygons):
        print 'Input:', polygons
        resultpolys = [(poly, []) for poly in polygons]
        #sort into exteriors and holes
        for pindex, (polyext, polyholes) in enumerate(resultpolys):
            for otherext, otherholes in resultpolys:
                if polyext == otherext:
                    continue # don't compare to self
                if polyext.first.isInside(otherext):
                    otherholes.append(polyext) #poly is within other so make into a hole
                    del resultpolys[pindex] #and delete poly from being an independent poly
        return resultpolys
        
    def phase_one(self, clip):
        # phase one - find intersections
        n_intersections = 0
        for s in self.subject.iter():
            for c in self.clip.iter():
                try:
                    i, alphaS, alphaC = intersect_or_on(s, s.next,
                                                        c, c.next)
                except TypeError:
                    continue

                s_between = (0 < alphaS < 1)
                c_between = (0 < alphaC < 1)
                if s_between and c_between:
                    #both subj and clip intersect each other somewhere in the middle
                    iS = Vertex(i, alphaS, intersect=True, entry=None)
                    iC = Vertex(i, alphaC, intersect=True, entry=None)
                    self.subject.insert(iS, s, self.subject.next(s.next))
                    self.clip.insert(iC, c, clip.next(c.next))

                    iS.neighbour = iC
                    iC.neighbour = iS

                    n_intersections += 1

        print 'Found {} intersections'.format(n_intersections)
        if not n_intersections: # special case, no intersections between subject and clip
            return list(self.subject.iter())

    def phase_two(self):
        polys = self.subject, self.clip
        
        for poly, other_poly in [polys, polys[::-1]]:
            status = poly.first.isInside(other_poly)
            for vertex in poly.iter():
                if vertex.intersect:
                    status = not status
                    vertex.entry = status
                    print vertex.entry, vertex.neighbour.entry

    def phase_three(self):
        result = []
        for _ in self.subject.unprocessed():
            current = self.subject.first_intersect
            clipped = Polygon()
            result.append(clipped)
            clipped.add(Vertex(current))
            while True:
                current.setChecked()
                if current.entry:
                    while True:
                        current = current.next
                        clipped.add(Vertex(current))
                        if current.intersect:
                            break
                else:
                    while True:
                        current = current.prev
                        clipped.add(Vertex(current))
                        if current.intersect:
                            break
                current = current.neighbour

                if current.checked:
                    break
        return result



class Cutter(Clipper):
    def phase_three(self):
        result = []
        start = self.subject.first
        while True:
            current = start
            while current.checked:
                current = current.next
                if current is start:
                    return result
            isSubject = True
            clipped = Polygon()
            result.append(clipped)
            clipped.add(Vertex(current))
            current_checked = False
            while not current_checked:
                current.setChecked()
                if current.entry and isSubject:
                    while True:
                        current = current.next
                        clipped.add(Vertex(current))
                        if current.intersect:
                            break
                elif current.entry and not isSubject:
                    print 'Interpolate forwards!!!!'
                    clipped.add(Vertex(current))
                    import cut_d3
                    r = cut_d3.clip_anti_meridian_interpolate((current.x, current.y),
                                                              (current.next.x, current.next.y),
                                                              1)
                    for geom in r:
                        for v in geom:
                            clipped.add(v)
                    current = current.next
                elif not current.entry and isSubject:
                    while True:
                        current = current.prev
                        clipped.add(Vertex(current))
                        if current.intersect:
                            break
                elif not current.entry and not isSubject:
                    print 'Interpolate backwards!!!'
                    import cut_d3
                    r = cut_d3.clip_anti_meridian_interpolate((current.x, current.y),
                                                         (current.previous.x, current.previous.y),
                                                         -1)
                    for geom in r:
                        for v in geom:
                            clipped.add(v)
#                     clipped.add(Vertex(current))
                    current = current.prev
                    
                current = current.neighbour
                isSubject = not isSubject
                current_checked = current.checked
            print 'Outer while. ', len(result)
        return result
        

def intersect_or_on(s1, s2, c1, c2):
    """Same as intersect(), except returns
    intersection even if degenerate.
    """
    den = float( (c2.y - c1.y) * (s2.x - s1.x) - (c2.x - c1.x) * (s2.y - s1.y) )
    if not den:
        return None

    us = ((c2.x - c1.x) * (s1.y - c1.y) - (c2.y - c1.y) * (s1.x - c1.x)) / den
    uc = ((s2.x - s1.x) * (s1.y - c1.y) - (s2.y - s1.y) * (s1.x - c1.x)) / den

    if (0 <= us <= 1) and (0 <= uc <= 1):
        #subj and clip line intersect eachother somewhere in the middle
        #this includes the possibility of degenerates (edge intersections)
        x = s1.x + us * (s2.x - s1.x)
        y = s1.y + us * (s2.y - s1.y)
        return (x, y), us, uc
    else:
        return None

def testLocation(point, polygon):
    """
    Effective scanline test for the location of a point vis a vis a polygon.
    Returns either "in","on",or "out".
    Based on algorithm 7 from the Holman point-in-polygon article (2001)
    """
    # begin
    if polygon.first.y == point.y and polygon.first.x == point.x:
        return "on" # vertex
    w =0
    for v in polygon.iter():
        if v.next.y == point.y:
            if v.next.x == point.x:
                return "on" # vertex
            else:
                if v.y == point.y and (v.next.x > point.x) == (v.x < point.x):
                    return "on" # edge
        # if crossing horizontal line
        if (v.y < point.y and v.next.y >= point.y)\
               or (v.y >= point.y and v.next.y < point.y):
            if v.x >= point.x:
                if v.next.x > point.x:
                    # modify w
                    if v.next.y > v.y: w += 1
                    else: w -= 1
                else:
                    det = (v.x - point.x) * (v.next.y - point.y) \
                        - (v.next.x - point.x) * (v.y - point.y)
                    if det == 0: return "on" # edge
                    # if right crossing
                    if (det > 0 and v.next.y > v.y)\
                       or (det < 0 and v.next.y < v.y):
                        # modify w
                        if v.next.y > v.y: w += 1
                        else: w -= 1
            else:
                if v.next.x > point.x:
                    det = (v.x - point.x) * (v.next.y - point.y) \
                        - (v.next.x - point.x) * (v.y - point.y)
                    if det == 0: return "on" # edge
                    # if right crossing
                    if (det > 0 and v.next.y > v.y)\
                       or (det < 0 and v.next.y < v.y):
                        # modify w
                        if v.next.y > v.y: w += 1
                        else: w -= 1
    if (w % 2) != 0:
        return "in"
    else:
        return "out"



def clip_polygon(subject_vertices, clip_vertices, klass=Clipper):
    """
    Higher level function for clipping two polygons (from a list of points).
    Since input polygons are lists of points, output is also in list format.
    Each polygon in the resultlist is a tuple of: (polygon exterior, list of polygon holes)
    """
    subject = Polygon()
    clip = Polygon()

    for s in subject_vertices:
        subject.add(Vertex(s))

    for c in clip_vertices:
        clip.add(Vertex(c))
 
    clipper = klass(subject, clip)
 
    clipped = clipper.do_it()
 
    clipped = [(ext.points,[hole.points for hole in holes]) for ext,holes in clipped]
    return clipped




def test():
 
    subjpoly = [(0,0),(6,0),(6,6),(0,6),(0,0)]

    # normal intersections
#     clippoly = [(4,4),(10,4),(10,10),(4,10),(4,4)] #simple overlap
    clippoly = [(1,4),(3,8),(5,4),(5,10),(1,10),(1,4)] #jigzaw overlap
#     clippoly = [(7,7),(7,9),(9,9),(9,7),(7,7)] #smaller, outside
    #clippoly = [(2,2),(2,4),(4,4),(4,2),(2,2)] #smaller, inside
    #clippoly = [(-1,-1),(-1,7),(7,7),(7,-1),(-1,-1)] #larger, covering all
    #clippoly = [(-10,-10),(-10,-70),(-70,-70),(-70,-10),(-10,-10)] #larger, outside
    # degenerate intersections
#     clippoly = [(0,5),(6,4),(10,4),(10,10),(4,10),(0,5)] #degenerate, starts on edge intersection and goes inside
    #clippoly = [(5,6),(5.2,5.5),(5,5.4),(4.8,5.5)] #degenerate, starts on edge intersection and goes outside
    #clippoly = [(1,5),(6,4),(6,5),(10,4),(10,10),(4,10),(2,6),(1,6),(1,5)] #degenerate, hesitating to enter and exit
    #clippoly = [(1,5),(6,4),(6,5),(10,4),(10,10),(4,10),(2,6),(1.3,6),(1.6,6),(1,6),(1,5)] #degenerate, also multiple degens along shared line
#     clippoly = [(1,5),(6,4),(6,5),(10,4),(10,10),(4,10),(2,6),(1.5,5.7),(1,6),(0,6),(1,5)] #degenerate, back and forth on-out along shared line
    #clippoly = [(0,0),(6,0),(6,6),(0,6),(0,0)] #degenerate, perfect overlap
#     clippoly = [(1,0),(6,0),(6,6),(1,6),(1,0)] #degenerate, partial inside overlap
    #clippoly = [(0,6),(6,6),(6,10),(0,10),(0,6)] #degenerate, right next to eachother
    #clippoly = [(2,6),(6,6),(6,10),(2,10),(2,6)] #degenerate, partial right next to eachother
    # self intersecting polygons
#     clippoly = [(1,4),(3,8),(1,5),(5,4),(5,10),(1,10),(-1,4)]
    # random polygon
    #clippoly = [(random.randrange(0,10),random.randrange(0,10)) for _ in xrange(10)] #random
    #run operation
    import time
    t = time.time()

    resultpolys = []
    resultpolys = clip_polygon(subjpoly,clippoly)

    print "finished:",resultpolys,time.time()-t
   
    print subjpoly
    import matplotlib.pyplot as plt
    
    import matplotlib.path as mpath
    from matplotlib.patches import PathPatch
    
    ax = plt.subplot(1, 2, 1)
    ax.add_patch(PathPatch(mpath.Path(subjpoly), alpha=0.5, color='red'))
    ax.add_patch(PathPatch(mpath.Path(clippoly), alpha=0.5, color='green'))
    ax.margins(0.1)
    ax.autoscale_view()
    
    ax2 = plt.subplot(1, 2, 2)
#     paths = []
    for ext, holes in resultpolys:
        paths = []
        
        paths.append(mpath.Path(ext, closed=True))
        for hole in holes:
            print 'Hole:', hole
            paths.append(mpath.Path(hole))
        print 'Ext:', ext
        ax2.add_patch(PathPatch(mpath.Path.make_compound_path(*paths),
                                alpha=0.5, color='green'))
    
    ax2.margins(0.1)
    ax2.autoscale_view()
    plt.show()

if __name__ == "__main__":
#     test()

    subjpoly = [(0,0), (-190,0), (-190,80), (0,80), (0,0)]
    clippoly = [(-180, -90), (-180, 90)]

    resultpolys = clip_polygon(subjpoly, clippoly,
                                klass=Cutter
                               )

    import matplotlib.pyplot as plt
    
    import matplotlib.path as mpath
    from matplotlib.patches import PathPatch
    
    ax = plt.subplot(1, 2, 1)
    ax.add_patch(PathPatch(mpath.Path(subjpoly), alpha=0.5, color='red'))
    ax.add_patch(PathPatch(mpath.Path(clippoly), alpha=0.5, color='green'))
    ax.margins(0.1)
    ax.autoscale_view()
    
    ax2 = plt.subplot(1, 2, 2)
    print len(resultpolys)
    for ext, holes in resultpolys:
        paths = []
        
        paths.append(mpath.Path(ext, closed=True))
        for hole in holes:
            paths.append(mpath.Path(hole))
        print ext
        ax2.add_patch(PathPatch(mpath.Path.make_compound_path(*paths),
                                alpha=0.5, color='green'))
    
    ax2.margins(0.1)
    ax2.autoscale_view()
#     plt.show()

