"""

"""
from __future__ import absolute_import, division

import contextlib
import os
import tempfile

import matplotlib.pyplot as plt
from PyQt4.QtCore import QSettings
import qgis.core

import cartopy.crs as ccrs


def add_layer(fname, layer_name=None, transparency=None):
    """
    Adds a raster layer to QGIS from the given filename. The
    file should be in EPSG:4326 and have an associated world file.
    """
    # Temporarily disable the projection dialogue so that we can set the
    # projection ourselves.
    with disabled_projection_dialogue():
        raster_layer = qgis.core.QgsRasterLayer(fname,
                                                os.path.basename(fname))
        epsg_type = qgis.core.QgsCoordinateReferenceSystem.EpsgCrsId
        raster_layer.setCrs(qgis.core.QgsCoordinateReferenceSystem(4326,
                                                                   epsg_type))

    # QGIS does not default to setting an RGBA image's transparency band.
    raster_layer.setTransparentBandName(raster_layer.bandName(4))
    raster_layer.setLayerName(layer_name or fname)

    if transparency is not None:
        raster_layer.setTransparency(transparency)

    if not raster_layer.isValid():
        raise RuntimeError("Layer failed to load!")

    qgis.core.QgsMapLayerRegistry.instance().addMapLayer(raster_layer)

    return raster_layer


@contextlib.contextmanager
def disabled_projection_dialogue():
    """
    Disables the QGIS projection dialogue for the lifetime
    of the context manager. Useful if you have a raster layer to add and you
    want to programmatically set the projection.

    """
    settings = QSettings()
    old_setting = settings.value("/Projections/defaultBehaviour",
                                 "useGlobal").toString()
    settings.setValue("/Projections/defaultBehaviour", "useGlobal")
    yield
    settings.setValue("/Projections/defaultBehaviour", old_setting)


def refresh_layer(layer):
    """
    Refreshes the given raster layer. Currently has issues successfully
    triggering QGIS to redraw.

    """
    layer.reload()
    if hasattr(layer, "setCacheImage"):
        layer.setCacheImage(None)
    layer.triggerRepaint()


@contextlib.contextmanager
def frozen_interface():
    """
    Freezes the QGIS interface for compute intensive operations.
    """
    qgis.utils.iface.mapCanvas().freeze(True)
    yield
    qgis.utils.iface.mapCanvas().freeze(False)


@contextlib.contextmanager
def cartopy_layer(img_fname=None, name=None, transparency=256,
                  img_size=(7200, 3600), dpi=100):
    """
    img_fname : str
        The filename of the resulting image. If None a temporary file
        will be created and used. The temporary file will not be deleted
        automatically.
    name : str
        The name of the layer in QGIS. Defaults to using the filename if no
        name is given.
    transparency : unsigned 8bit integer
        The transparency to apply to the finished QGIS layer.
    img_size : interable of ints
        The pixel size of the resulting image. Values must be multiples
        of the ``dpi``.
    dpi : int
        The dpi of the resulting image, should be a divisor of the
        ``img_size`` values.

    """
    x_pix, y_pix = img_size
    fig = plt.figure(figsize=(x_pix / dpi, y_pix / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())

    ax.set_global()
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)

    if img_fname is None:
        img_fname = tempfile.mktemp(prefix='qgis_cartopy_layer', suffix='.png')

    yield ax

    ax.set_global()
    fig.savefig(img_fname, dpi=dpi,
                facecolor='none', edgecolor='none')

    world_fname = os.path.splitext(img_fname)[0] + '.wld'
    with open(world_fname, 'w') as fh:
        # Write a global world file.
        fh.write('\n'.join([str(v) for v in
                            [360 / x_pix, 0, 0, -180 / y_pix, -180, 90]]))

    # Add the newly created image.
    add_layer(img_fname, layer_name=name, transparency=transparency)
