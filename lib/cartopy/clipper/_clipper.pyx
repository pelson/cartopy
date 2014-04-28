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
    
    ctypedef signed long long cInt
    ctypedef char bool 

    cdef struct IntPoint:
        cInt X
        cInt Y

    cdef cppclass Path:
        Path()
        void push_back(IntPoint&)
        IntPoint& operator[](int)
        IntPoint& at(int)
        int size()
        
    cdef cppclass Paths:
        Paths()
        void push_back(Path&)
        Path& operator[](int)
        Path& at(int)
        int size()

    void SimplifyPolygon(Path in_poly, Paths out_polys)
    void SimplifyPolygons(Paths in_polys, Paths out_polys)
    void SimplifyPolygons(Paths polys)


    cdef cppclass Clipper:
        Clipper()
        #~Clipper()
        bool Run(ClipType clipType, Paths solution, PolyFillType subjFillType, PolyFillType clipFillType)
        void Clear()
        
        bool AddPath( Path pg, PolyType polyType, bool closed)
        bool AddPaths( Paths ppg, PolyType polyType, bool closed)
        void Clear()


def simplify_polygons(pypolygons):
    print "SimplifyPolygons "
    cdef Path poly =  Path() 
    cdef IntPoint a
    cdef Paths polys =  Paths()
    for pypolygon in pypolygons:
        for pypoint in pypolygon:
            a = IntPoint(pypoint[0], pypoint[1])
            poly.push_back(a)
        polys.push_back(poly)  

    cdef Paths solution
    SimplifyPolygons(polys, solution)
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
    cdef Path poly =  Path() 
    cdef IntPoint a
    for x, y in vertices:
        a = IntPoint(x, y)
        poly.push_back(a)

    cdef Paths solution
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
    def add_path(self, pypolygon):
        print "Adding polygon"

        cdef Path square =  Path() 
        cdef IntPoint a
        for p in pypolygon:
            a = IntPoint(p[0], p[1])
            square.push_back(a)

        cdef Paths subj =  Paths() 
        subj.push_back(square)  
        self.thisptr.AddPaths(subj, ptSubject, 0)


    #===========================================================
    #bool AddPath(Path pg, PolyType polyType)
    def sub_polygon(self, pypolygon):
        print "Sub polygon"
        cdef Path square =  Path() 
        cdef IntPoint a
        for p in pypolygon:
            a = IntPoint(p[0], p[1])
            square.push_back(a)

        cdef Paths subj =  Paths() 
        subj.push_back(square)  
        self.thisptr.AddPaths(subj, ptClip, 0)
        
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
        