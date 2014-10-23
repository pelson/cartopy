# -*- coding: utf-8 -*-

# SEE http://www.jasondavies.com/maps/intersect/
# 
# For solutions, http://geo.javawa.nl/coordcalc/index_en.html
# http://www.dirkbertels.net/computing/greatCircles_files/great_circles_070206.pdf


import numpy as np

from cartopy.transforms.geom_interpolate import to_cartesian

def to_spherical(cartesian_p):
    x, y, z = cartesian_p
    lamb = np.arctan2(y, x)
    phi = np.arcsin(np.clip(z, -1, 1))
    return np.rad2deg(np.array([lamb, phi]))
    

def normalise_vector(vect):
    # Normalise a vector of any length into a unit vector.
    vect = np.array(vect, dtype=np.float64)
    vect /= np.sqrt(np.sum(vect**2))
    return vect


def intersect(a0, a1, b0, b1):
    # The intersection of two great circles on the sphere is just their
    # intersection in 3d cartesian space projected onto the surface.
    a0 = to_cartesian(a0)
    a1 = to_cartesian(a1)
    b0 = to_cartesian(b0)
    b1 = to_cartesian(b1)

    a = np.cross(a0, a1)
    b = np.cross(b0, b1)
    a0 = np.cross(a, a0)
    a1 = np.cross(a, a1)
    b0 = np.cross(b, b0)
    b1 = np.cross(b, b1)

    axb = normalise_vector(np.cross(a, b))
    a0 = np.dot(axb, a0)
    a1 = np.dot(axb, a1)
    b0 = np.dot(axb, b0)
    b1 = np.dot(axb, b1)

    eps = 1e-16
    if a0 >= -eps and a1 <= eps and b0 >= -eps and b1 <= eps:
        return to_spherical(axb)
    if a0 <= eps and a1 >= -eps and b0 <= eps and b1 >= -eps:
        return to_spherical(-axb)
    return None




if __name__ == '__main__':
    from nose.tools import assert_equal
    from numpy.testing import assert_almost_equal
    assert_almost_equal(np.array([0, 0]),
                        intersect((-40, 0), (40, 0), (0, 40), (0, -40)),
                        decimal=6)

    assert_almost_equal(np.array([0, 0]),
                        intersect((-40, 0), (100, 0), (20, 40), (-20, -40)),
                        decimal=6)

    assert_equal(None,
                 intersect((-160, 0), (100, 0), (20, 40), (-20, -40))
                 )
    assert_almost_equal((180, 0),
                        intersect((-160, 0), (160, 0), (180, -40), (180, 40)),
                        decimal=6)

#     print intersect((-31, 0), (30, 0), (-16, 0), (15, 0))

    print intersect((180, 10), (160, 20), (180, 0), (180, 90))

