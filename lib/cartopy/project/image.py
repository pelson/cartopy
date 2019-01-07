import logging
import time

import cartopy.crs as ccrs
import netCDF4
import numpy as np
from pykdtree.kdtree import KDTree

from cartopy.io import RasterSource, LocatedImage


class KDRasterize(RasterSource):
    def __init__(self, lons, lats, img):
        self._geocent = ccrs.Geocentric(globe=ccrs.Globe())
        self.img = img
        xyz = self._geocent.transform_points(ccrs.Geodetic(), lons, lats)

        start = time.time()
        self._kd = KDTree(xyz)
        end = time.time()
        logging.info('KD Construction time ({} points): {}'.format(lons.size, end - start))

    def validate_projection(self, projection):
        return True

    def fetch_raster(self, projection, extent, target_resolution):
        target_resolution = np.array(target_resolution, dtype=int)
        x = np.linspace(extent[0], extent[1], target_resolution[0])
        y = np.linspace(extent[2], extent[3], target_resolution[1])
        xs, ys = np.meshgrid(x, y)
        xyz_sample = self._geocent.transform_points(
                projection, xs.flatten(), ys.flatten())
        start = time.time()
        _, img = self._kd.query(xyz_sample, k=1, sqr_dists=True)
        end = time.time()
        logging.info('Query of {} points: {}'.format(np.prod(target_resolution),
                                              end - start))
        img = np.array(img).reshape(target_resolution[1], target_resolution[0])
        img = self.img.flatten()[img]
        return [LocatedImage(img, extent)]

