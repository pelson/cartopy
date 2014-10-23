# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

def rotate_fn(euler0, euler1, euler2):
    """
    Note:

    To turn a lat lon to a rotated pole lat lon:

    def UM_rotated_pole(pole_lon, pole_lat):
        return rotate_fn(180 + -pole_lon, pole_lat - 90, 0)

    And the inverse:

    def UM_rotated_pole_inverse(pole_lon, pole_lat):
        return rotate_fn(pole_lon - 180, 90 - pole_lat, 0)


    The third argument gives an oblique rotation - not a new "rotated"
    longitude as per possible with rotated pole.

    """
    e1, e2 = np.deg2rad([euler1, euler2])
    cose1, sine1 = np.cos(e1), np.sin(e1)
    cose2, sine2 = np.cos(e2), np.sin(e2)

    def rotate(x, y):
        # Sort out the simple rotation first.
        x = x + euler0
        if e1 == e2 == 0:
            x = ((x + 180 + 360 * 10) % 360) - 180
            return np.array([x, y])

        lam, phi = np.deg2rad([x, y])

        cosy = np.cos(phi)
        x = np.cos(lam) * cosy
        y = np.sin(lam) * cosy
        z = np.sin(phi)
        k = z * cose1 + x * sine1
        return np.rad2deg([np.arctan2(y * cose2 - k * sine2, x * cose1 - z * sine1),
                           np.arcsin(k * cose2 + y * sine2)])
    return rotate


def UM_rotated_pole(pole_lon, pole_lat):
    return rotate_fn(180 + -pole_lon, pole_lat - 90, 0)

def UM_rotated_pole_inverse(pole_lon, pole_lat):
    """
    Return a function that can give lats and lons for a given rotated coordinate pair.

    """
    return rotate_fn(pole_lon - 180, 90 - pole_lat, 0)

if __name__ == '__main__':
    pole = -180, -40
    pole = 180, 90

    import cartopy.crs as ccrs
    rp = ccrs.RotatedPole(pole_longitude=pole[0], pole_latitude=pole[1])
    pc = ccrs.PlateCarree()

    if True:
        fn = UM_rotated_pole(pole[0], pole[1])
        print fn(0, 0.), fn(45, 45.)

        print rp.transform_point(0, 0, pc)
        print rp.transform_point(45, 45, pc)
    else:
        fn = UM_rotated_pole_inverse(pole[0], pole[1])
        print fn(0, 0.), fn(45, 45.), fn(-45, 45.)

        print pc.transform_point(0, 0, rp)
        print pc.transform_point(45, 45, rp)
        print pc.transform_point(-45, 45, rp)
