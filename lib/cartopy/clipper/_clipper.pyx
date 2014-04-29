import numpy as np
cimport numpy as np

        
cdef extern from "clipper.hpp" namespace "ClipperLib":
    ctypedef signed long long cInt
    ctypedef char bool 

    cdef struct IntPoint:
        cInt X
        cInt Y

    cdef cppclass Path:
        Path()
        void push_back(IntPoint&)
        IntPoint& operator[](int)
        int size()
        
    cdef cppclass Paths:
        Paths()
        void push_back(Path&)
        Path& operator[](int)
        int size()

    void SimplifyPolygons(Paths polys)


cdef clipper_to_mpl(Paths clipper_paths, scale_factor=10**5):
    solution = clipper_paths
    n = solution.size()
    cdef IntPoint point
    
    solution_paths = [] 
    for i in range(n):
        solution_clpath = solution[i]
        m = solution_clpath.size()
        # Make the solution longer by one - Clipper has done *polygon* simplification,
        # so we need to put the final vertex equal to the first for mpl.
        solution_path = np.empty([m + 1, 2], dtype=np.float32)
        solution_paths.append(solution_path)
        for j in range(m):
            solution_path[j, 0] = float(solution_clpath[j].X) / scale_factor
            solution_path[j, 1] = float(solution_clpath[j].Y) / scale_factor
        else:
            solution_path[m, 0] = float(solution_clpath[0].X) / scale_factor
            solution_path[m, 1] = float(solution_clpath[0].Y) / scale_factor
    return solution_paths


cdef Paths mpl_to_clipper(path, scale_factor=10**5):
    cdef Paths clipper_path
    cdef Path sub_clipper_path
    cdef int i
    cdef IntPoint a
    vertices = path.vertices * scale_factor
    codes = path.codes
    
    clipper_path = Paths()
    sub_clipper_path = Path()
    
    for i in xrange(len(path)):
        code = codes[i]
        vertex = vertices[i]
        
        if code == 1: # moveto
            if sub_clipper_path.size() > 0:
                clipper_path.push_back(sub_clipper_path)
            sub_clipper_path = Path()
        elif code == 79: # closepoly
            if sub_clipper_path.size() > 0:
                clipper_path.push_back(sub_clipper_path)
            sub_clipper_path = Path()
        elif code == 0: # stop
            if sub_clipper_path.size() > 0:
                clipper_path.push_back(sub_clipper_path)
            break
        elif code == 2:
            pass
        else:
            raise ValueError('Unsupported Path code.')
        
        a = IntPoint(vertex[0], vertex[1])
        sub_clipper_path.push_back(a)
    else:
        if sub_clipper_path.size() > 0:
            clipper_path.push_back(sub_clipper_path)
    return clipper_path


def simplify_mpl_path(path, scale_factor=10**5):
    """Remove self intersections into multiple paths."""
    cdef Paths clipper_paths = mpl_to_clipper(path, scale_factor=scale_factor)
    SimplifyPolygons(clipper_paths)
    return clipper_to_mpl(clipper_paths, scale_factor=scale_factor)
