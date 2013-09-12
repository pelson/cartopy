"""

"""
from __future__ import absolute_import, division

import contextlib
import os
import tempfile

from PyQt4.QtCore import QSettings
import qgis.core

import cartopy.crs as ccrs


from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure





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
    
    if not raster_layer.isValid():
        raise RuntimeError("Layer failed to load!")
    
    qgis.core.QgsMapLayerRegistry.instance().addMapLayer(raster_layer)
    
    if transparency is not None:
        raster_layer.setTransparency(transparency)
        
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
    settings.setValue( "/Projections/defaultBehaviour", old_setting)


def refresh_layer(layer):
    """
    Refreshes the given raster layer. Currently has issues successfully
    triggering QGIS to update.
    
    """
    layer.reload()
    if hasattr(layer, "setCacheImage"):
        layer.setCacheImage(None)
    layer.triggerRepaint()


@contextlib.contextmanager
def frozen_interface():
    qgis.utils.iface.mapCanvas().freeze(True)
    yield
    qgis.utils.iface.mapCanvas().freeze(False)


@contextlib.contextmanager
def cartopy_layer(img_fname=None, name=None,
                  img_size=(3600, 1800), dpi=100):
    """
    img_fname : str
        The filename of the resulting image. If None a temporary file
        will be created and used. The temporary file will not be deleted
        automatically.
    name : str
        The name of the layer in QGIS. Defaults to using the filename if no
        name is given.
    img_size : interable of ints
        The pixel size of the resulting image. Values must be multiples
        of the ``dpi``.
    dpi : int
        The dpi of the resulting image, should be a divisor of the
        ``img_size`` values.
    
    """
    x_pix, y_pix = img_size
    
    fig = Figure(figsize=(x_pix / dpi, y_pix / dpi), dpi=dpi)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    ax.set_global()
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)
    
    if img_fname is None:
        img_fname = tempfile.mktemp(prefix='qgis_cartopy_layer', suffix='.png')
    
    yield ax
    
    ax.set_global()
    canvas.print_figure(img_fname, dpi=dpi,
                        facecolor='none', edgecolor='none')
    
    world_fname = os.path.splitext(img_fname)[0] + '.wld'
    with open(world_fname, 'w') as fh:
        # Write a global world file. 
        fh.write('\n'.join(360/x_pix, 0, 0, -180/y_pix, -180, 90))

    # Add the newly created image.
    add_layer(img_fname, layer_name=name)


#
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
#
#qgis_layers = []
#
#if not hasattr(plt, 'orig'):
#    plt.orig = plt.draw_if_interactive
#
#def new_draw_if_interactive():
#    print 'drawing if interactive'
#    for layer in qgis_layers:
#        layer.was_drawn = False
#    plt.orig()
#    for layer in qgis_layers:
#        if not layer.was_drawn:
#            assert layer._cachedRenderer is not None, "Figure hasn't yet been drawn with pyplot."
#            layer.draw(layer._cachedRenderer)
#        
#plt.draw_if_interactive = new_draw_if_interactive
#
#
#def new_layer(directory=os.path.dirname(__file__)):
#    import cartopy.crs as ccrs
#    dpi = 90
#    x_pix = 3600.
#    y_pix = 1800.
#    fig = plt.figure(figsize=(x_pix / dpi, y_pix / dpi), dpi=dpi)
#    # Draw the empty figure to create a _cachedRenderer attribute.
#
#    import datetime
#    dt = datetime.datetime.now()
#    img_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.png')
#    world_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.wld')
#    with open(img_fname, 'wb') as fh:
#        fig.savefig(fh, facecolor='none', edgecolor='none', dpi=fig.dpi)
#    
#    import types
#    fig.original_draw = fig.draw
#    fig._qgis_fname = img_fname
#    fig._qgis_world_fname = world_fname
#    fig._qgis_layer = None 
#    def new_draw(self, renderer):
#        self.original_draw(renderer)
#        print 'draw called'
#        self.was_drawn = True
#        # XXX Handle updating of the qgis layer. (perhaps checksum the image)
#        self.draw = self.original_draw
##         os.remove(self._qgis_fname)
#        
#
#        with open(self._qgis_fname, 'wb') as fh:
#            self.savefig(fh, facecolor='none', edgecolor='none', dpi=self.dpi)
#        
#        if self._qgis_layer is None:
#            # XXX center coordinates need calculating.
#            world = dict(x_pix_size=360./x_pix, y_rotation=0, x_rotation=0,
#                         y_pix_size=-180./y_pix, x_center=-180, y_center=90)
#            
#            from cartopy.tests.test_img_nest import _save_world
#            _save_world(world_fname, world)       
#            
#            self._qgis_layer = add_layer(self._qgis_fname)    
#        
#        else:
#            refresh_layer(self._qgis_layer)
##         alpha_to_color(PIL.Image.open(img_fname)).save(img_fname)
#        self.draw = self.new_draw
##         refresh_all()
##         import time
##         time.sleep(2)
#        
##         refresh_all()
#        
#
#    fig.new_draw = types.MethodType(new_draw, fig)
#    fig.draw = fig.new_draw
#
#    def destructor(self):
#        print 'destroying.'
#
#    fig.__del__ = types.MethodType(destructor, fig)
#
#    qgis_layers.append(fig)
#    ax = plt.axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
#    ax.set_global()
#    ax.outline_patch.set_visible(False)
#    ax.background_patch.set_visible(False)
#    
#    # XXX TODO - add figure destructor to remove from the QGIS_LAYERS list and temporary file.
#    return ax




#def new_layer_non_interactive(directory=None, layer_name=None):
#    import cartopy.crs as ccrs
#    dpi = 90
#    x_pix = 7200.
#    y_pix = 3600.
#    fig = plt.figure(figsize=(x_pix / dpi, y_pix / dpi), dpi=dpi)
#    ax = plt.axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
#    ax.set_global()
#    ax.outline_patch.set_visible(False)
#    ax.background_patch.set_visible(False)
#    
#    if directory is None:
#        import datetime
#        dt = datetime.datetime.now()
#        import tempfile
#        directory = tempfile.mkdtemp(prefix=dt.strftime("%Y%m%d_%H%M%S"))
#    
#    def create():
#        import datetime
#        dt = datetime.datetime.now()
#        img_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.png')
#        world_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.wld')
#        with open(img_fname, 'wb') as fh:
#            fig.savefig(fh, facecolor='none', edgecolor='none', dpi=fig.dpi)
#        world = dict(x_pix_size=360./x_pix, y_rotation=0, x_rotation=0,
#                         y_pix_size=-180./y_pix, x_center=-180, y_center=90)
#
#        from cartopy.tests.test_img_nest import _save_world
#        _save_world(world_fname, world)
#        add_layer(img_fname, layer_name=layer_name)
#    
#    return create, ax





#
#def example():
#    import datetime
#    dt = datetime.datetime.now()
#    import tempfile
#    tmp_dir = tempfile.mkdtemp(prefix=dt.strftime("%Y%m%d_%H%M%S"))
#    ax = new_layer(tmp_dir)
#    
#    plt.plot(range(10))
#    ax.coastlines()
#    plt.draw()
#    #plt.plot(range(-10, 12))
#    
#    # Display in traditional form too?
#    #plt.show(block=True)
#
#if __name__ == '__main__':
#    example()
##    plt.show()