# -*- coding: utf-8 -*-

import numpy as np


def sphericalEqual(p0, p1):
    return (np.allclose(p0[0], p1[0]) and
            np.allclose(p0[1], p1[1]))


from collections import namedtuple

### TRANSLATION OF CLIP-POLYGON.js


class IntersectedSegment(object):
    def __init__(self, point, points, other, entry):
        self.point = point
        self.points = points
        self.other = other
        self.entry = entry
        self.visited = False
        self.next = self.previous = None


def clip_Polygon_Link_Circular(segment_list):
    # TODO: Turn this highly JS like code into *real* python!
    if len(segment_list) == 0:
        return
        # Note: Was if (!(n = array.length)) return;

    n = len(segment_list)
    i = 0
    a = segment_list[0]
    while i < (n - 1):
        i += 1
        a.next = b = segment_list[i]
        b.previous = a
        a = b
    a.next = b = segment_list[0]
    b.previous = a



class SphericalPolygonCutter():
    def __init__(self, segments, sort_fn, is_clip_start_inside, interpolator):
        self.segments = segments
        self.subject = []
        self.clip = []
        self.sort_fn = sort_fn
        self.is_clip_start_inside = is_clip_start_inside
        self.interpolator = interpolator


    def cut_antimeridian(self):
        pass

"""
function d3_geo_clipAntimeridianLine(listener) {
  var λ0 = NaN,
      φ0 = NaN,
      sλ0 = NaN,
      clean; // no intersections

  return {
    lineStart: function() {
      listener.lineStart();
      clean = 1;
    },
    point: function(λ1, φ1) {
      var sλ1 = λ1 > 0 ? π : -π,
          dλ = abs(λ1 - λ0);
      if (abs(dλ - π) < ε) { // line crosses a pole
        listener.point(λ0, φ0 = (φ0 + φ1) / 2 > 0 ? halfπ : -halfπ);
        listener.point(sλ0, φ0);
        listener.lineEnd();
        listener.lineStart();
        listener.point(sλ1, φ0);
        listener.point(λ1, φ0);
        clean = 0;
      } else if (sλ0 !== sλ1 && dλ >= π) { // line crosses antimeridian
        // handle degeneracies
        if (abs(λ0 - sλ0) < ε) λ0 -= sλ0 * ε;
        if (abs(λ1 - sλ1) < ε) λ1 -= sλ1 * ε;
        φ0 = d3_geo_clipAntimeridianIntersect(λ0, φ0, λ1, φ1);
        listener.point(sλ0, φ0);
        listener.lineEnd();
        listener.lineStart();
        listener.point(sλ1, φ0);
        clean = 0;
      }
      listener.point(λ0 = λ1, φ0 = φ1);
      sλ0 = sλ1;
    },
    lineEnd: function() {
      listener.lineEnd();
      λ0 = φ0 = NaN;
    },
    // if there are intersections, we always rejoin the first and last segments.
    clean: function() { return 2 - clean; }
  };
}
"""



    def to_cartesian(self):
        result = []
        for segment in self.segments:
            p0 = segment[0]
            p1 = segment[-1]

            # If the first and last points of a segment are coincident, then treat as
            # a closed ring.
            # TODO if all rings are closed, then the winding order of the exterior
            # ring should be checked.
            if sphericalEqual(p0, p1):
                result.append(segment)
                # NOTE: Was the following in JS. 
                # for (var i = 0; i < n; ++i) listener.point((p0 = segment[i])[0], p0[1])

                # We're done with this segment.
                continue

            a = IntersectedSegment(p0, segment, None, True)
            b = IntersectedSegment(p0, None, a, False)
            a.other = b;
            self.subject.append(a)
            self.clip.append(b)

            a = IntersectedSegment(p1, segment, None, False)
            b = IntersectedSegment(p1, None, a, True)
            a.other = b;
            self.subject.append(a)
            self.clip.append(b)

        self.clip.sort(self.sort_fn)
        clip_Polygon_Link_Circular(self.subject)
        clip_Polygon_Link_Circular(self.clip)

        print self.subject
        if not self.subject:
            # XXX Can't we do this before sorting?
            return

        # Alternate the entry/exit of a clip segment.
        entry = self.is_clip_start_inside
        n = len(self.clip)
        for i in range(n):
            self.clip[i].entry = entry = not entry

        start = self.subject[0]
        while True:
            # Find first unvisited intersection.
            current = start
            isSubject = True
            while (current.visited):
                current = current.next
                if current == start:
                    return result
            points = current.points
            line = []
            while True:
                current.visited = current.other.visited = True
                if current.entry:
                    if isSubject:
#                        for (var i = 0, n = points.length; i < n; ++i) listener.point((point = points[i])[0], point[1]);
                        line.extend(points)
                    else:
                        # XXX NOT A REAL CALL.
                        print 'Interp'
                        print self.interpolator(current.point, current.next.point, 1)
                        
                        line.extend(self.interpolator(current.point, current.next.point, 1))
                    current = current.next
                else:
                    if isSubject:
                        points = current.previous.points
                        line.extend(points[::-1])
                    else:
                        # XXX NOT A REAL CALL.
                        print 'Interp'
#                        print self.interpolator(current.point, current.previous.point, -1)
#                        print 'PS', current.point, current.previous.point, self.interpolator(current.point, current.previous.point, -1)
                        line.extend(self.interpolator(current.point, current.previous.point, -1))
                    current = current.previous

                current = current.other
                points = current.points
                isSubject = not isSubject
                if current.visited:
                    break
            result.append(line)
        return result

# Intersection points are sorted along the clip edge. For both antimeridian
# cutting and circle clipping, the same comparison is used.
def edge_sort(p0, p1):
    a = p0.point
    b = p1.point
#    function d3_geo_clipSort(a, b) {
#        return ((a = a.x)[0] < 0 ? a[1] - halfpi - eps : halfpi - a[1])
#                - ((b = b.x)[0] < 0 ? b[1] - halfpi - eps : halfpi - b[1]);
#    }
    epsilon = np.finfo(np.float32).eps
    return ((a[1] - 90 - epsilon if a[0] < 0 else 90 - a[1])
            - (b[1] - 90 - epsilon if b[0] < 0 else 90 - b[1]))



def clip_anti_meridian_interpolate(p0=None, p1=None, direction=1):
    pi = 180
    if p0 is None:
        phi = direction * 90
        r = [[-pi, phi],
             [0, phi],
             [pi, phi],
             [pi, 0],
             [pi, -phi],
             [0, -phi],
             [-pi, -phi],
             [-pi, 0],
             [-pi, phi],
             ]
    elif not np.allclose(p0[0], p1[0]):
        s = pi if p0[0] < p1[0] else -pi;
        phi = direction * s / 2.;
        r = [[-s, phi],
             [0, phi],
             [s, phi]]
    else:
        r = [[p0[0], p1[1]]]
    return r


if __name__ == '__main__':
    segments = [[[170, 0], [190, 0]]]
    r = SphericalPolygonCutter(segments, edge_sort, False, clip_anti_meridian_interpolate)
    result = r.to_cartesian()
    print 'Result:', result




######## NOW WE HAVE CLIP>JS


# d3_geo_clip
class Cutter(object):
    def __init__(self, point_visible_fn, clipLine, interpolator, clipStart, rotate,
                 ):
        self.point_visible_fn = point_visible_fn
        self.clipLine = clipLine
        self.interpolator = interpolator
        self.clipStart = clipStart
        self.rotate = rotate

    def cut_line(self, segments):
        return self.clipLine.to_cartesian(segments)









c = """

import "../arrays/merge";
import "../core/noop";
import "../math/trigonometry";
import "clip-polygon";

function d3_geo_clip(pointVisible, clipLine, interpolate, clipStart) {
  return function(rotate, listener) {
    var line = clipLine(listener),
        rotatedClipStart = rotate.invert(clipStart[0], clipStart[1]);

    var clip = {
      point: point,
      lineStart: lineStart,
      lineEnd: lineEnd,
      polygonStart: function() {
        clip.point = pointRing;
        clip.lineStart = ringStart;
        clip.lineEnd = ringEnd;
        segments = [];
        polygon = [];
      },
      polygonEnd: function() {
        clip.point = point;
        clip.lineStart = lineStart;
        clip.lineEnd = lineEnd;

        segments = d3.merge(segments);
        var clipStartInside = d3_geo_pointInPolygon(rotatedClipStart, polygon);
        if (segments.length) {
          if (!polygonStarted) listener.polygonStart(), polygonStarted = true;
          d3_geo_clipPolygon(segments, d3_geo_clipSort, clipStartInside, interpolate, listener);
        } else if (clipStartInside) {
          if (!polygonStarted) listener.polygonStart(), polygonStarted = true;
          listener.lineStart();
          interpolate(null, null, 1, listener);
          listener.lineEnd();
        }
        if (polygonStarted) listener.polygonEnd(), polygonStarted = false;
        segments = polygon = null;
      },
      sphere: function() {
        listener.polygonStart();
        listener.lineStart();
        interpolate(null, null, 1, listener);
        listener.lineEnd();
        listener.polygonEnd();
      }
    };

    function point(λ, φ) {
      var point = rotate(λ, φ);
      if (pointVisible(λ = point[0], φ = point[1])) listener.point(λ, φ);
    }
    function pointLine(λ, φ) {
      var point = rotate(λ, φ);
      line.point(point[0], point[1]);
    }
    function lineStart() { clip.point = pointLine; line.lineStart(); }
    function lineEnd() { clip.point = point; line.lineEnd(); }

    var segments;

    var buffer = d3_geo_clipBufferListener(),
        ringListener = clipLine(buffer),
        polygonStarted = false,
        polygon,
        ring;

    function pointRing(λ, φ) {
      ring.push([λ, φ]);
      var point = rotate(λ, φ);
      ringListener.point(point[0], point[1]);
    }

    function ringStart() {
      ringListener.lineStart();
      ring = [];
    }

    function ringEnd() {
      pointRing(ring[0][0], ring[0][1]);
      ringListener.lineEnd();

      var clean = ringListener.clean(),
          ringSegments = buffer.buffer(),
          segment,
          n = ringSegments.length;

      ring.pop();
      polygon.push(ring);
      ring = null;

      if (!n) return;

      // No intersections.
      if (clean & 1) {
        segment = ringSegments[0];
        var n = segment.length - 1,
            i = -1,
            point;
        if (n > 0) {
          if (!polygonStarted) listener.polygonStart(), polygonStarted = true;
          listener.lineStart();
          while (++i < n) listener.point((point = segment[i])[0], point[1]);
          listener.lineEnd();
        }
        return;
      }

      // Rejoin connected segments.
      // TODO reuse bufferListener.rejoin()?
      if (n > 1 && clean & 2) ringSegments.push(ringSegments.pop().concat(ringSegments.shift()));

      segments.push(ringSegments.filter(d3_geo_clipSegmentLength1));
    }

    return clip;
  };
}

function d3_geo_clipSegmentLength1(segment) {
  return segment.length > 1;
}

function d3_geo_clipBufferListener() {
  var lines = [],
      line;
  return {
    lineStart: function() { lines.push(line = []); },
    point: function(λ, φ) { line.push([λ, φ]); },
    lineEnd: d3_noop,
    buffer: function() {
      var buffer = lines;
      lines = [];
      line = null;
      return buffer;
    },
    rejoin: function() {
      if (lines.length > 1) lines.push(lines.pop().concat(lines.shift()));
    }
  };
}

// Intersection points are sorted along the clip edge. For both antimeridian
// cutting and circle clipping, the same comparison is used.
function d3_geo_clipSort(a, b) {
  return ((a = a.x)[0] < 0 ? a[1] - halfπ - ε : halfπ - a[1])
       - ((b = b.x)[0] < 0 ? b[1] - halfπ - ε : halfπ - b[1]);
}


"""



####### NOW WE HAVE CLIP_ANTIMERIDIAN.js


c = """
var d3_geo_clipAntimeridian = d3_geo_clip(
    d3_true,
    d3_geo_clipAntimeridianLine,
    d3_geo_clipAntimeridianInterpolate,
    [-π, -π / 2]);

// Takes a line and cuts into visible segments. Return values:
//   0: there were intersections or the line was empty.
//   1: no intersections.
//   2: there were intersections, and the first and last segments should be
//      rejoined.
function d3_geo_clipAntimeridianLine(listener) {
  var λ0 = NaN,
      φ0 = NaN,
      sλ0 = NaN,
      clean; // no intersections

  return {
    lineStart: function() {
      listener.lineStart();
      clean = 1;
    },
    point: function(λ1, φ1) {
      var sλ1 = λ1 > 0 ? π : -π,
          dλ = abs(λ1 - λ0);
      if (abs(dλ - π) < ε) { // line crosses a pole
        listener.point(λ0, φ0 = (φ0 + φ1) / 2 > 0 ? halfπ : -halfπ);
        listener.point(sλ0, φ0);
        listener.lineEnd();
        listener.lineStart();
        listener.point(sλ1, φ0);
        listener.point(λ1, φ0);
        clean = 0;
      } else if (sλ0 !== sλ1 && dλ >= π) { // line crosses antimeridian
        // handle degeneracies
        if (abs(λ0 - sλ0) < ε) λ0 -= sλ0 * ε;
        if (abs(λ1 - sλ1) < ε) λ1 -= sλ1 * ε;
        φ0 = d3_geo_clipAntimeridianIntersect(λ0, φ0, λ1, φ1);
        listener.point(sλ0, φ0);
        listener.lineEnd();
        listener.lineStart();
        listener.point(sλ1, φ0);
        clean = 0;
      }
      listener.point(λ0 = λ1, φ0 = φ1);
      sλ0 = sλ1;
    },
    lineEnd: function() {
      listener.lineEnd();
      λ0 = φ0 = NaN;
    },
    // if there are intersections, we always rejoin the first and last segments.
    clean: function() { return 2 - clean; }
  };
}

function d3_geo_clipAntimeridianIntersect(λ0, φ0, λ1, φ1) {
  var cosφ0,
      cosφ1,
      sinλ0_λ1 = Math.sin(λ0 - λ1);
  return abs(sinλ0_λ1) > ε
      ? Math.atan((Math.sin(φ0) * (cosφ1 = Math.cos(φ1)) * Math.sin(λ1)
                 - Math.sin(φ1) * (cosφ0 = Math.cos(φ0)) * Math.sin(λ0))
                 / (cosφ0 * cosφ1 * sinλ0_λ1))
      : (φ0 + φ1) / 2;
}

function d3_geo_clipAntimeridianInterpolate(from, to, direction, listener) {
  var φ;
  if (from == null) {
    φ = direction * halfπ;
    listener.point(-π,  φ);
    listener.point( 0,  φ);
    listener.point( π,  φ);
    listener.point( π,  0);
    listener.point( π, -φ);
    listener.point( 0, -φ);
    listener.point(-π, -φ);
    listener.point(-π,  0);
    listener.point(-π,  φ);
  } else if (abs(from[0] - to[0]) > ε) {
    var s = from[0] < to[0] ? π : -π;
    φ = direction * s / 2;
    listener.point(-s, φ);
    listener.point( 0, φ);
    listener.point( s, φ);
  } else {
    listener.point(to[0], to[1]);
  }
}

"""