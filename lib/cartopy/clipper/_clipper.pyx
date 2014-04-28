import sys
import struct
from ctypes import *
import copy
import unicodedata
import time
from cython import *

from cython.operator cimport dereference as deref

from libcpp.vector cimport vector

        
cdef extern from "clipper.hpp" namespace "ClipperLib":
    cdef enum ClipType:
        ctIntersection= 1,
        ctUnion=2,
        ctDifference=3,
        ctXor=4
    
    cdef enum PolyType:
        ptSubject= 1,
        ptClip=2

    cdef enum PolyFillType:
        pftEvenOdd= 1,
        pftNonZero=2,
        pftPositive=3,
        pftNegative=4
    
    ctypedef signed long long long64
    ctypedef unsigned long long ulong64
    ctypedef char bool 

    cdef struct IntPoint:
        long64 X
        long64 Y

    cdef cppclass Polygon:
        Polygon()
        void push_back(IntPoint&)
        IntPoint& operator[](int)
        IntPoint& at(int)
        int size()
        
    cdef cppclass Polygons:
        Polygons()
        void push_back(Polygon&)
        Polygon& operator[](int)
        Polygon& at(int)
        int size()

    void SimplifyPolygon(Polygon in_poly, Polygons out_polys)
    void SimplifyPolygons(Polygons in_polys, Polygons out_polys)
    void SimplifyPolygons(Polygons polys)


    cdef cppclass Clipper:
        Clipper()
        #~Clipper()
        bool Run(ClipType clipType, Polygons solution, PolyFillType subjFillType, PolyFillType clipFillType)
        void Clear()
        
        bool AddPolygon( Polygon pg, PolyType polyType)
        bool AddPolygons( Polygons ppg, PolyType polyType)
        void Clear()


def simplify_polygons(pypolygons):
    print "SimplifyPolygons "
    cdef Polygon poly =  Polygon() 
    cdef IntPoint a
    cdef Polygons polys =  Polygons()
    for pypolygon in pypolygons:
        for pypoint in pypolygon:
            a = IntPoint(pypoint[0], pypoint[1])
            poly.push_back(a)
        polys.push_back(poly)  

    cdef Polygons solution
    SimplifyPolygons( polys, solution)
    n = solution.size()
    sol = []

    cdef IntPoint point
    for i in range(n):
        poly = solution[i]
        m = poly.size()
        loop = []
        for i in range(m):
            point = poly[i]
            loop.append([point.X ,point.Y])
        sol.append(loop)
    return sol


def simplify_mpl_vertices(vertices):
    """
    Removes any self intersecting polygons so that the resulting polygons are strictly simple (not strictly yet).
    """
    cdef Polygon poly =  Polygon() 
    cdef IntPoint a
    for x, y in vertices:
        a = IntPoint(x, y)
        poly.push_back(a)

    cdef Polygons solution
    SimplifyPolygon(poly, solution)
    n = solution.size()
    sol = []

    cdef IntPoint point
    for i in range(n):
        poly = solution[i]
        m = poly.size()
        loop = []
        for i in range(m):
            point = poly[i]
            loop.append([point.X ,point.Y])
        sol.append(loop)
    return sol



cdef class Pyclipper:
    cdef Clipper *thisptr      # hold a C++ instance which we're wrapping
    error_code = {-1:"UNSPECIFIED_ERROR", -2: "BAD_TRI_INDEX", -3:"NO_VOX_MAP", -4:"QUERY_FAILED"}

    #===========================================================
    def __cinit__(self):
        print "Creating a Clipper"
        self.thisptr = new Clipper()

    #===========================================================
    def __dealloc__(self):
        print "Deleting a Clipper"
        del self.thisptr

    #===========================================================
    #bool AddPolygon(Polygon pg, PolyType polyType)
    def add_polygon(self, pypolygon):
        print "Adding polygon"

        cdef Polygon square =  Polygon() 
        cdef IntPoint a
        for p in pypolygon:
            a = IntPoint(p[0], p[1])
            square.push_back(a)

        cdef Polygons subj =  Polygons() 
        subj.push_back(square)  
        self.thisptr.AddPolygons(subj, ptSubject)


    #===========================================================
    #bool AddPolygon(Polygon pg, PolyType polyType)
    def sub_polygon(self, pypolygon):
        print "Sub polygon"
        cdef Polygon square =  Polygon() 
        cdef IntPoint a
        for p in pypolygon:
            a = IntPoint(p[0], p[1])
            square.push_back(a)

        cdef Polygons subj =  Polygons() 
        subj.push_back(square)  
        self.thisptr.AddPolygons(subj, ptClip)
        
    def test(self):
        import random
        shapes = []

        shape = []
        for i in range(3):
            p = [500+int(1000*random.random()), 500+int(1000*random.random())]
            shape.append(p)
        shapes.append(shape)
        
        for i in range(3):
            p = [500+int(1000*random.random()), 500+int(1000*random.random())]
            shape.append(p)
        shapes.append(shape)
        
        shapes = simplify_polygons(shapes)
        print shapes
        print 'bar.'
        return
        