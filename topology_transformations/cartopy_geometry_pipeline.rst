The cartopy geometry pipeline
=============================

Introduction
------------

Taking a spherical geometry representation from one projected coordinate system into another for all but the simplest cases inevitably involves a topological transformation.

.. note::
    
    A topolological transform - cut and glue a geometry into the desired form. Stretching is not a topological transform.

For instance, imagine transforming the outline of Africa onto a projection with the dateline (which is also the antimeridian of the PlateCarree projection) in the middle.
Essentially, we must cut the geometry into two parts at the new antimeridian (now 0 degrees longitude):

.. plot::
    code/africa_to_pc180.py


Transforming from one cylindrical projection to another is a relatively straightforward concept, at least, until we start to involve geometries covering the poles.

Irrespective of the coordinate system of the vertices, it is very unusual to have geometries in a non-projected (i.e. spherical) topology.
To help understand this, in your minds eye, imagine the outline of Antarctica.

.. plot::
    code/antarctica.py

Tracing the coordinates of the Antarctica polygon on the left hand plot in a clockwise direction starting from north-most point, after following the coastline of Antarctica, we eventually come to a straight line which follows the dateline down to the bottom of our plot, then goes back across to the left hand side and then up to the coastal coordinate and along.
When we look at the map on the right hand side, we see that there is no such line in real life - in actual fact, the straight lines on the left-hand map are just how we must represent a polygon which crosses the dateline of the map.

The polygon therefore has a topology suitable for this map, but does not have a spherical topology.

The right hand map however, does link the two points which cross the dateline together, therefore its topology is close to being spherical.

Why close? Because in 2D space, a sequence of coordinates which start and end at the same place are sufficient to represent a filled area un-ambiguously - on the sphere however we cannot determine which side of the line should be filled, and therefore impose an extra constraint - namely that the order of the coordinate sequence determines the side on which to fill (e.g. always fill on the right hand side of the line). **Action**: Ask Jason how complex spherical geometries are handled - or just try it.

It is not possible to have a projected topology in which all polygons have a spherical topology - going from a sphere to a projected map **always** involves a topological transformation of some kind.


The three phases of geometry transformation in Cartopy
------------------------------------------------------

Cartopy separates the process of transforming a projected geometry to another projected geometry into 3 distinct phases:

 1. Transform the geometry from the topology of the source projection to spherical topology.
 2. Transform the geometry from spherical topology to the topology of the target projection.
 3. Interpolate the geometry to a suitable precision in the target projection's coordinate system.


Phase one: Source topolgy to spherical topology
################################################

The first phase in the process involves knowledge of the topology of the incoming geometry.
 - For cylindrical projections, the topology is a single antimeridian line and singularities at both poles.
 - For stereographic projections, the topology is a ring at the anti-podal point (e.g. the south pole for north polar stereographic).

With this knowledge, we inspect each geometry and identify and remove any topological features that have been applied to the given geometry.
For example, in Plate Carree we remove the lines, at, to and from the south pole from the outline of Antarctica.
Any points which link up to another spherically (aka a line which crosses a discontinuity) are joined back together and a note that the join has taken place is recorded.
This is the inverse operation to phase 2, so see there for more clarity on what needs to be undone.

.. plot::
    code/pc_to_spherical_antarctica.py

All geometries are now correctly oriented (fill on right hand side of vertex, aka clockwise).

The coordinate **values** of the original geometry are preserved (the topology is spherical, but the coordinates themselves are not).


Phase Two: Spherical toplogy to target topology
################################################

Again, we must know the topology of the target projection, with this knowledge we apply this topology to the spherical geometry.

For example, supposing we have the ring which represents the outline of Antarctica (in a spherical topology, remember) and wanted to project the geometry to a Cylindirical topology.
We traverse the coordinates and cut those segments which cross the antimeridian. Any cut points are then joined together by great circles, taking care to apply the appropriate fill direction based on the order of the incoming geometry.

The coordinate **values** of the original geometry are still preserved, except for the inserted great circles, but the topology is now that of the target projection.

.. plot::
    code/spherical_antarctica_to_pc180.py


Phase Three: Interpolate to arbitrary precision
################################################

Now that we have done all of the hard work of ensuring that the geomerty is in the topology of the target coordinate system we can guarantee that no matter
what precision we wish to draw the geometry, it will not need to be cut or glued together.

We now need to be provided a function which, given two vertices in the source coordinate system, can interpolate smaller vertices which we can insert into the projected geometry.
The interpolation doesn't need to worry about whether a segment crosses the dateline (or any other topological effect) as we have already determined that no such segment exists in the transformed geometry. We also need a function which can interpolate our great circles in the same regard.

Armed with these two functions, we traverse the geometry, interpolating each segment until it reaches a threshold of "acceptablity", and eventually end up with a geometry which can be used for various purposes, including drawing on a map.


.. plot::
    code/interpolate.py

