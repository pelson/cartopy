# -*- coding: UTF-8 -*-
# Efficient Clipping of Arbitrary Polygons
#
# Copyright (c) 2011, 2012 Helder Correia <helder.mc@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

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

    first = None

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

    def clip(self, clip):

        # prep by removing repeat of startpoint at end
        first = self.first
        last = first.prev
        if last.x == first.x and last.y == first.y:
            first.prev = last.prev
            last.prev.next = first
        first = clip.first
        last = first.prev
        if last.x == first.x and last.y == first.y:
            first.prev = last.prev
            last.prev.next = first
        
        # phase one - find intersections
        anyintersection = False
        for s in self.iter(): # for each vertex Si of subject polygon do
            if not s.intersect:
                for c in clip.iter(): # for each vertex Cj of clip polygon do
                    if not c.intersect:
                        try:
                            i, alphaS, alphaC = intersect_or_on(s, self.next(s.next),
                                                          c, clip.next(c.next))
                        except TypeError:
                            continue
                            # OLD CATCH ALL...
##                            if (0 < alphaS < 1) and (0 < alphaC < 1):
##                                #subj and clip line intersect eachother somewhere in the middle
##                                iS = Vertex(i, alphaS, intersect=True, entry=False)
##                                iC = Vertex(i, alphaC, intersect=True, entry=False)
##                                self.insert(iS, s, self.next(s.next))
##                                clip.insert(iC, c, clip.next(c.next))
##                            else:
##                                #degenerate case, so mark the "degen"-flag, and replace vertex instead of inserting
##                                iS = Vertex(i, alphaS, intersect=True, entry=False, degen=True)
##                                iC = Vertex(i, alphaC, intersect=True, entry=False, degen=True)
##                                print "replace",c
##                                #self.insert(iS, s, self.next(s.next))
##                                #clip.insert(iC, c, clip.next(c.next))
##                                self.replace(s, iS)
##                                clip.replace(c, iC)
##                                print "with",iC
##                                
##                            iS.neighbour = iC
##                            iC.neighbour = iS

                        s_between = (0 < alphaS < 1)
                        c_between = (0 < alphaC < 1)
                        if s_between and c_between:
                            #both subj and clip intersect each other somewhere in the middle
                            iS = Vertex(i, alphaS, intersect=True, entry=False)
                            iC = Vertex(i, alphaC, intersect=True, entry=False)
                            self.insert(iS, s, self.next(s.next))
                            clip.insert(iC, c, clip.next(c.next))
                        else:
                            if s_between:
                                #subj line is touched by the start or stop point of a line from the clip polygon, so insert and mark that intersection as a degenerate
                                iS = Vertex(i, alphaS, intersect=True, entry=False, degen=True)
                                self.insert(iS, s, self.next(s.next))
                            elif alphaS == 0:
                                #subj line starts at intersection, so mark the "degen"-flag, and replace vertex instead of inserting
                                iS = Vertex(i, alphaS, intersect=True, entry=False, degen=True)
                                self.replace(s, iS)
                            elif alphaS == 1:
                                #subj line ends at intersection, so mark the "degen"-flag, and replace vertex instead of inserting
                                iS = Vertex(i, alphaS, intersect=True, entry=False, degen=True)
                                self.replace(self.next(s.next), iS)
                            if c_between:
                                #clip line is touched by the start or stop point of a line from the subj polygon, so insert and mark that intersection as a degenerate
                                iC = Vertex(i, alphaC, intersect=True, entry=False, degen=True)
                                clip.insert(iC, c, clip.next(c.next))
                            elif alphaC == 0:
                                #clip line starts at intersection, so mark the "degen"-flag, and replace vertex instead of inserting
                                iC = Vertex(i, alphaC, intersect=True, entry=False, degen=True)
                                clip.replace(c, iC)
                            elif alphaC == 1:
                                #clip line ends at intersection, so mark the "degen"-flag, and replace vertex instead of inserting
                                iC = Vertex(i, alphaC, intersect=True, entry=False, degen=True)
                                clip.replace(clip.next(c.next), iC)
                            
                        iS.neighbour = iC
                        iC.neighbour = iS
                        
                        anyintersection = True

        if not anyintersection: # special case, no intersections between subject and clip
            raise ValueError('No Intersections!')

        return self.phase_two(clip)

        # phase two - identify entry/exit points
##        s_entry ^= self.first.isInside(clip)
##        for s in self.iter():
##            if s.intersect:
##                s.entry = s_entry
##                s_entry = not s_entry
##
##        c_entry ^= clip.first.isInside(self)
##        for c in clip.iter():
##            if c.intersect:
##                c.entry = c_entry
##                c_entry = not c_entry

##        # phase two - DEGEN SUPPORT ALTERNATIVE
##        #(prereq, during intersection phase mark .on flag as True if alphas are 0 or 1)
##        #then mark entry/exit as usual, but if .on flag then check prev and next and neighbour location first
##        def locationCombi(i, poly):
##            # degenerate point, ie subject line starts or ends on clipline
##            # i stands for the intersection point to be labelled
##            prevloc = testLocation(i.prev, poly)
##            nextloc = testLocation(i.next, poly)
##            if i.prev.on:
##                if i.next.on:
##                    return "on_on"
##                elif nextloc == "in":
##                    return "on_in"
##                elif nextloc == "out":
##                    return "on_out"
##            elif prevloc == "in":
##                if nextloc:
##                    return "in_on"
##                elif nextloc == "in":
##                    return "in_in"
##                elif nextloc == "out":
##                    return "in_out"
##            elif prevloc == "out":
##                if i.next.on:
##                    return "out_on"
##                elif nextloc == "in":
##                    return "out_in"
##                elif nextloc == "out":
##                    return "out_out"
##        s_entry ^= self.first.isInside(clip)
##        for s in self.iter():
##            if s.intersect:
##                if s.on:
##                    # intersection is degenerate, is the start/endpoint of a line
##                    # so label entry/exit based on prev/next locations
##                    s_combi = locationCombi(s, clip)
##                    if s_combi in ("in_in","on_on","out_out"):
##                        c_combi = locationCombi(s.neighbour, self)
##                        if c_combi in ("in_in","on_on","out_out"):
##                            s.intersect = False
##                        elif s_combi == "out_out":
##                            s.entry = False
##                        elif s_combi == "in_in":
##                            s.entry = True
##                        elif s_combi == "on_on":
##                            # label opposite of neighbour
##                            # ...but it hasnt been labelled yet, endless loop?
##                            s.entry = not s.neighbour.entry
##                    # at least one on
##                    elif s_combi in ("on_out","in_on"):
##                        s.entry = False
##                    elif s_combi in ("out_on","on_in"):
##                        s.entry = True
##                    # finally check for conflict with neighbour
##                    # ...but it hasnt been labelled yet, endless loop?
##                    if s.entry and s.neighbour.entry:
##                        s.intersect = False
##                        s.inside = True
##                    elif not s.entry and not s.neighbour.entry:
##                        s.intersect = False
##                        s.inside = False
##                else:
##                    #pure inside or outside, so use normal entry toggle
##                    s.entry = s_entry
##                    s_entry = not s_entry


    def phase_two(self, clip):
        # phase two - MY OWN IMPROV
        #RECENT FIXES
        # "ON" DOESNT NECESARILY MEAN IT'S ALONG ONE EDGE, BC NEXT CAN JUMP ACROSS EDGES INWARDS AND OUTWARDS EVEN THOUGH IT IS ON
        #  NEED TO TEST FOR THIS, MAYBE WITH LINE-POLY INTERSECTION TEST
        #  ACTUALLY, TEST IT BY ALSO SEEING HOW THE NEIGHBOUR PREV AND NEXT ARE, WILL TELL IF ITS ENTERING OR EXITING THE OTHER POLYGON
        #  ACTUALLY, PROB JUST EASIEST WITH USING THE IN/OUT STATUS OF MIDPOINT BW CUR-PREV AND CUR-NEXT
        # ALSO UNRELATED, REMOVE LAST POINT OF POLYS IF SAME AS FIRST, AND JUST APPEND FIRST TO END BEFORE RETURNING RESULTS
        #---
        #FINAL UNRELATED, SHAPES NEXT TO EACH OTHER HAVE PROBLEMS, MAYBE CUS OF WRONG INSIDE TEST AND EARLY RETURN AFTER PHASE1
        #FINAL FINAL, RELATED? STARTPOINT MUST BE MADE AN OPENING INTERSECTION IF ITS ON AN EDGE AND MIDPOINT TO NEXT IS "IN"
        #MAYBE ALSO DOESNT DIFFERENTIATE THE RESULT HOLES CORRECTLY, MAYBE DUE TO INSIDE TESTS
        #AND MAYBE GETS STUCK IN ENDLESS LOOP IF TOO MANY RANDOM POLYGON VERTICES, BUT NEED TO CHECK OUT IF IT'S THE AMOUNT OF VERTICES OR JUST UNSUPPORTED SELFINTERSECTIONS
        #
        #  (prereq, during intersection phase mark .degen flag as True if any of the alphas are 0 or 1)
        #  then mark entry/exit as usual, but if .degen flag then check prev and next location first

        # based on Forster, start by looping both subj and clip and marking each vertex location
        for s in self.iter():
            s.loc = testLocation(s, clip)
        for c in clip.iter():
            c.loc = testLocation(c, self)
            
        # proceed to loop subj, marking as entry or exit, and potentially changing the location flags
        for s in self.iter():
            
            if s.intersect:
                
                def mark(current):
                    neighbour = current.neighbour
                    #on/on
                    if current.prev.loc == "on" and current.next.loc == "on":
                      #Determine what to do based on the neighbour
                      #en tag is the opposite of the neighbour's en tag 
                      if neighbour.prev.loc == "on" and neighbour.next.loc == "on":
                          current.intersect = False
                          if neighbour.loc == "in": current.loc = "out"
                          elif neighbour.loc == "out": current.loc = "in"
                          #neighbour.entry = True
                      elif neighbour.prev.loc == "on" and neighbour.next.loc == "out":
                          current.entry = True
                          current.loc = "in"
                      elif neighbour.prev.loc == "on" and neighbour.next.loc == "in":
                          current.entry = False
                          current.loc = "in"
                      elif neighbour.prev.loc == "out" and neighbour.next.loc == "on":
                          current.entry = False
                          current.loc = "in"
                      elif neighbour.prev.loc == "out" and neighbour.next.loc == "out":
                          current.intersect = False
                          if neighbour.loc == "in": current.loc = "out"
                          elif neighbour.loc == "out": current.loc = "in"
                          #neighbour.entry = False
                      elif neighbour.prev.loc == "out" and neighbour.next.loc == "in":
                          current.entry = False
                          current.loc = "in"
                      elif neighbour.prev.loc == "in" and neighbour.next.loc == "on":
                          current.entry = True
                          current.loc = "in"
                      elif neighbour.prev.loc == "in" and neighbour.next.loc == "out":
                          current.entry = True
                          current.loc = "in"
                      elif neighbour.prev.loc == "in" and neighbour.next.loc == "in":
                          current.intersect = False
                          if neighbour.loc == "in": current.loc = "out"
                          elif neighbour.loc == "out": current.loc = "in"
                          #neighbour.entry = True
                    #on/out
                    elif current.prev.loc == "on" and current.next.loc == "out":
                        current.entry = False
                    #on/in  
                    elif current.prev.loc == "on" and current.next.loc == "in":
                        current.entry = True
                    #out/on  
                    elif current.prev.loc == "out" and current.next.loc == "on":
                        current.entry = True
                    #out/out  
                    elif current.prev.loc == "out" and current.next.loc == "out":
                        if neighbour.prev.loc == "on" and neighbour.next.loc == "on":
                            current.intersect = False
                            current.loc = "out"
                            #neighbour.entry = True
                        elif neighbour.prev.loc == neighbour.next.loc == "out" or neighbour.prev.loc == neighbour.next.loc == "in":
                            current.intersect = False
                            current.loc = "out"
                        else:
                            if neighbour.prev.loc == "on" and neighbour.next.loc == "out":
                                current.entry = True
                            else:
                                current.entry = False
                    #out/in  
                    elif current.prev.loc == "out" and current.next.loc == "in":
                        current.entry = True
                    #in/on
                    elif current.prev.loc == "in" and current.next.loc == "on":
                        current.entry = False
                    #in/out
                    elif current.prev.loc == "in" and current.next.loc == "out":
                        current.entry = False
                    #in/in
                    elif current.prev.loc == "in" and current.next.loc == "in":
                        if neighbour.prev.loc == "on" and neighbour.next.loc == "on":
                            current.intersect = False
                            current.loc = "in"
                            #neighbour.entry = False
                        elif neighbour.prev.loc == neighbour.next.loc == "out" or neighbour.prev.loc == neighbour.next.loc == "in":
                            current.intersect = False
                            current.loc = "in"
                        else:
                            if neighbour.prev.loc == "in" and neighbour.next.loc == "out":
                                current.entry = True
                            else:
                                current.entry = False


                # mark curr
                mark(s)

##                # mark neighbour
##                # NOTE: the algorithm explained in the article only explains
##                # how to mark the main subject polygon, but never says how
##                # to mark the neighbour, so just using the same procedure
##                mark(s.neighbour)

                # finally make sure curr and neighbour dont have same flags
                if s.intersect and s.neighbour.intersect:
                    if s.entry and s.neighbour.entry:
                        s.intersect = False
                        s.loc = "in"
                    elif not s.entry and not s.neighbour.entry:
                        s.intersect = False
                        s.loc = "out"

        return self.phase_three()

    def phase_three(self):
        # phase three - construct a list of clipped polygons
        resultpolys = []
        for _ in self.unprocessed():
            current = self.first_intersect
            clipped = Polygon()
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

            polytuple = (clipped, [])
            resultpolys.append(polytuple)

        #sort into exteriors and holes
        for pindex,(polyext,polyholes) in enumerate(resultpolys):
            for otherext,otherholes in resultpolys:
                if polyext == otherext:
                    continue # don't compare to self
                if polyext.first.isInside(otherext):
                    otherholes.append(polyext) #poly is within other so make into a hole
                    del resultpolys[pindex] #and delete poly from being an independent poly
        return resultpolys

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


def intersect(s1, s2, c1, c2):
    """Test the intersection between two lines (two pairs of coordinates for two points).

    Return the coordinates for the intersection and the subject and clipper alphas if the test passes.

    Algorithm based on: http://paulbourke.net/geometry/lineline2d/
    """
    den = float( (c2.y - c1.y) * (s2.x - s1.x) - (c2.x - c1.x) * (s2.y - s1.y) )

    if not den:
        return None

    us = ((c2.x - c1.x) * (s1.y - c1.y) - (c2.y - c1.y) * (s1.x - c1.x)) / den
    uc = ((s2.x - s1.x) * (s1.y - c1.y) - (s2.y - s1.y) * (s1.x - c1.x)) / den

    if (us == 0 or us == 1) and (0 <= uc <= 1) or\
       (uc == 0 or uc == 1) and (0 <= us <= 1):
        print "whoops! degenerate case!"
        return None

    elif (0 < us < 1) and (0 < uc < 1):
        x = s1.x + us * (s2.x - s1.x)
        y = s1.y + us * (s2.y - s1.y)
        return (x, y), us, uc

    return None

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


def clip_polygon(subject, clipper, operation = 'difference'):
    """
    Higher level function for clipping two polygons (from a list of points).
    Since input polygons are lists of points, output is also in list format.
    Each polygon in the resultlist is a tuple of: (polygon exterior, list of polygon holes)
    """
    Subject = Polygon()
    Clipper = Polygon()

    for s in subject:
        Subject.add(Vertex(s))

    for c in clipper:
        Clipper.add(Vertex(c))

    clipped = Subject.clip(Clipper)

    clipped = [(ext.points,[hole.points for hole in holes]) for ext,holes in clipped]
    return clipped



if __name__ == "__main__":
 
    subjpoly = [(0,0),(6,0),(6,6),(0,6),(0,0)]

    # normal intersections
#     clippoly = [(4,4),(10,4),(10,10),(4,10),(4,4)] #simple overlap
    clippoly = [(1,4),(3,8),(5,4),(5,10),(1,10),(1,4)] #jigzaw overlap
#     clippoly = [(7,7),(7,9),(9,9),(9,7),(7,7)] #smaller, outside
    #clippoly = [(2,2),(2,4),(4,4),(4,2),(2,2)] #smaller, inside
    #clippoly = [(-1,-1),(-1,7),(7,7),(7,-1),(-1,-1)] #larger, covering all
    #clippoly = [(-10,-10),(-10,-70),(-70,-70),(-70,-10),(-10,-10)] #larger, outside
    # degenerate intersections
    #clippoly = [(0,5),(6,4),(10,4),(10,10),(4,10),(0,5)] #degenerate, starts on edge intersection and goes inside
    #clippoly = [(5,6),(5.2,5.5),(5,5.4),(4.8,5.5)] #degenerate, starts on edge intersection and goes outside
    #clippoly = [(1,5),(6,4),(6,5),(10,4),(10,10),(4,10),(2,6),(1,6),(1,5)] #degenerate, hesitating to enter and exit
    #clippoly = [(1,5),(6,4),(6,5),(10,4),(10,10),(4,10),(2,6),(1.3,6),(1.6,6),(1,6),(1,5)] #degenerate, also multiple degens along shared line
#     clippoly = [(1,5),(6,4),(6,5),(10,4),(10,10),(4,10),(2,6),(1.5,5.7),(1,6),(0,6),(1,5)] #degenerate, back and forth on-out along shared line
    #clippoly = [(0,0),(6,0),(6,6),(0,6),(0,0)] #degenerate, perfect overlap
    #clippoly = [(1,0),(6,0),(6,6),(1,6),(1,0)] #degenerate, partial inside overlap
    #clippoly = [(0,6),(6,6),(6,10),(0,10),(0,6)] #degenerate, right next to eachother
    #clippoly = [(2,6),(6,6),(6,10),(2,10),(2,6)] #degenerate, partial right next to eachother
    # self intersecting polygons
#     clippoly = [(1,4),(3,8),(1,5),(5,4),(5,10),(1,10),(1,4)]
    # random polygon
    #clippoly = [(random.randrange(0,10),random.randrange(0,10)) for _ in xrange(10)] #random
    #run operation
    import time
    t = time.time()

    resultpolys = clip_polygon(subjpoly,clippoly,"difference")

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
#         for hole in holes:
#             paths.append(mpath.Path(hole))
        print 'Ext:', ext
        ax2.add_patch(PathPatch(paths[0],
                                alpha=0.5, color='green'))
    
    ax2.margins(0.1)
    ax2.autoscale_view()
    plt.show()