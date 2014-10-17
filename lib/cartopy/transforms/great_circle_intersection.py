import numpy as np


# SEE http://www.jasondavies.com/maps/intersect/

# For solutions, http://geo.javawa.nl/coordcalc/index_en.html

def intersect(a, b):
    var a0 = d3_geo_cartesian([a[0][0] * radians, a[0][1] * radians]),
    a1 = d3_geo_cartesian([a[1][0] * radians, a[1][1] * radians]),
    b0 = d3_geo_cartesian([b[0][0] * radians, b[0][1] * radians]),
    b1 = d3_geo_cartesian([b[1][0] * radians, b[1][1] * radians]);

c = """
function intersect(a, b) {
  var a0 = d3_geo_cartesian([a[0][0] * radians, a[0][1] * radians]),
      a1 = d3_geo_cartesian([a[1][0] * radians, a[1][1] * radians]),
      b0 = d3_geo_cartesian([b[0][0] * radians, b[0][1] * radians]),
      b1 = d3_geo_cartesian([b[1][0] * radians, b[1][1] * radians]);
  a = d3_geo_cartesianCross(a0, a1);
  b = d3_geo_cartesianCross(b0, b1);
  a0 = d3_geo_cartesianCross(a, a0);
  a1 = d3_geo_cartesianCross(a, a1);
  b0 = d3_geo_cartesianCross(b, b0);
  b1 = d3_geo_cartesianCross(b, b1);
  var axb = d3_geo_cartesianCross(a, b);
  d3_geo_cartesianNormalize(axb);
  a0 = d3_geo_cartesianDot(axb, a0);
  a1 = d3_geo_cartesianDot(axb, a1);
  b0 = d3_geo_cartesianDot(axb, b0);
  b1 = d3_geo_cartesianDot(axb, b1);
  if (a0 > -ε && a1 < ε && b0 >- ε && b1 < ε) {
    var i = d3_geo_spherical(axb);
    return [i[0] * degrees, i[1] * degrees];
  }

  if (a0 < ε && a1 > -ε && b0 < ε && b1 > -ε) {
    axb[0] = -axb[0], axb[1] = -axb[1], axb[2] = -axb[2];
    var i = d3_geo_spherical(axb);
    return [i[0] * degrees, i[1] * degrees];
  }
}

function d3_geo_cartesian(spherical) {
  var λ = spherical[0],
      φ = spherical[1],
      cosφ = Math.cos(φ);
  return [
    cosφ * Math.cos(λ),
    cosφ * Math.sin(λ),
    Math.sin(φ)
  ];
}

function d3_geo_cartesianDot(a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function d3_geo_cartesianCross(a, b) {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ];
}

function d3_geo_cartesianNormalize(d) {
  var l = Math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
  d[0] /= l;
  d[1] /= l;
  d[2] /= l;
}

function d3_geo_spherical(cartesian) {
  return [
    Math.atan2(cartesian[1], cartesian[0]),
    Math.asin(Math.max(-1, Math.min(1, cartesian[2])))
  ];
}
"""