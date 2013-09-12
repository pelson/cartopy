from __future__ import absolute_import
import os

import qgis.core












import PIL.Image
import numpy as np


def alpha_to_color(image, color=(253, 255, 254)):
    """Set all fully transparent pixels of an RGBA image to the specified color.
    This is a very simple solution that might leave over some ugly edges, due
    to semi-transparent areas. You should use alpha_composite_with color instead.

    Source: http://stackoverflow.com/a/9166671/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """ 
    x = np.array(image)
    r, g, b, a = np.rollaxis(x, axis=-1)
    print a
    r[a == 0] = color[0]
    g[a == 0] = color[1]
    b[a == 0] = color[2] 
    x = np.dstack([r, g, b, a])
    return PIL.Image.fromarray(x, 'RGBA')




def add_layer(fname, layer_name=None):
    baseName = os.path.basename(fname)
    with disable_projection_dialogue():
        raster_layer = qgis.core.QgsRasterLayer(fname, baseName)
        epsg = qgis.core.QgsCoordinateReferenceSystem.EpsgCrsId
        epsg4326 = qgis.core.QgsCoordinateReferenceSystem(4326, epsg)
        raster_layer.setCrs(epsg4326)
    
    raster_layer.setTransparentBandName(raster_layer.bandName(4))
    raster_layer.setLayerName(layer_name or fname)
#     raster_layer.
    
    if not raster_layer.isValid():
        print "Layer failed to load!"
    
    qgis.core.QgsMapLayerRegistry.instance().addMapLayer(raster_layer)
    
#     from PyQt4.QtCore import QFileSystemWatcher

#     def refreshLayer():
#         raster_layer.setCacheImage( None )
#         raster_layer.triggerRepaint()
#     
#     watcher = QFileSystemWatcher()
#     watcher.addPath(fname)
#     watcher.fileChanged.connect( refreshLayer )
    
#     raster_layer.setTransparency(200)
    return raster_layer
    # Needed? 


import contextlib
@contextlib.contextmanager
def disable_projection_dialogue():
    from PyQt4.QtCore import QSettings
    
    s = QSettings()
    oldValidation = s.value( "/Projections/defaultBehaviour", "useGlobal" ).toString()
    s.setValue( "/Projections/defaultBehaviour", "useGlobal" )
    yield
    s.setValue( "/Projections/defaultBehaviour", oldValidation )

def refresh_layer(layer):
    print 'refreshing:', layer
    print dir(layer)
    
    layer.reload()
    if hasattr(layer, "setCacheImage"):
        layer.setCacheImage(None)
    layer.triggerRepaint()
#     layer.update()
    
#     import qgis.utils
#     qgis.utils.iface.legendInterface().refreshLayerSymbology(layer)

def refresh_all():
    import qgis.utils
    qgis.utils.iface.mapCanvas().freeze(True)
    layers = qgis.utils.iface.legendInterface().layers()
    for layer in layers:
        refresh_layer(layer)
    qgis.utils.iface.mapCanvas().freeze(False)



import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

qgis_layers = []

if not hasattr(plt, 'orig'):
    plt.orig = plt.draw_if_interactive

def new_draw_if_interactive():
    print 'drawing if interactive'
    for layer in qgis_layers:
        layer.was_drawn = False
    plt.orig()
    for layer in qgis_layers:
        if not layer.was_drawn:
            assert layer._cachedRenderer is not None, "Figure hasn't yet been drawn with pyplot."
            layer.draw(layer._cachedRenderer)
        
plt.draw_if_interactive = new_draw_if_interactive


def new_layer(directory=os.path.dirname(__file__)):
    import cartopy.crs as ccrs
    dpi = 90
    x_pix = 3600.
    y_pix = 1800.
    fig = plt.figure(figsize=(x_pix / dpi, y_pix / dpi), dpi=dpi)
    # Draw the empty figure to create a _cachedRenderer attribute.

    import datetime
    dt = datetime.datetime.now()
    img_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.png')
    world_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.wld')
    with open(img_fname, 'wb') as fh:
        fig.savefig(fh, facecolor='none', edgecolor='none', dpi=fig.dpi)
    
    import types
    fig.original_draw = fig.draw
    fig._qgis_fname = img_fname
    fig._qgis_world_fname = world_fname
    fig._qgis_layer = None 
    def new_draw(self, renderer):
        self.original_draw(renderer)
        print 'draw called'
        self.was_drawn = True
        # XXX Handle updating of the qgis layer. (perhaps checksum the image)
        self.draw = self.original_draw
#         os.remove(self._qgis_fname)
        

        with open(self._qgis_fname, 'wb') as fh:
            self.savefig(fh, facecolor='none', edgecolor='none', dpi=self.dpi)
        
        if self._qgis_layer is None:
            # XXX center coordinates need calculating.
            world = dict(x_pix_size=360./x_pix, y_rotation=0, x_rotation=0,
                         y_pix_size=-180./y_pix, x_center=-180, y_center=90)
            
            from cartopy.tests.test_img_nest import _save_world
            _save_world(world_fname, world)       
            
            self._qgis_layer = add_layer(self._qgis_fname)    
        
        else:
            refresh_layer(self._qgis_layer)
#         alpha_to_color(PIL.Image.open(img_fname)).save(img_fname)
        self.draw = self.new_draw
#         refresh_all()
#         import time
#         time.sleep(2)
        
#         refresh_all()
        

    fig.new_draw = types.MethodType(new_draw, fig)
    fig.draw = fig.new_draw

    def destructor(self):
        print 'destroying.'

    fig.__del__ = types.MethodType(destructor, fig)

    qgis_layers.append(fig)
    ax = plt.axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    ax.set_global()
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)
    
    # XXX TODO - add figure destructor to remove from the QGIS_LAYERS list and temporary file.
    return ax




def new_layer_non_interactive(directory=None, layer_name=None):
    import cartopy.crs as ccrs
    dpi = 90
    x_pix = 7200.
    y_pix = 3600.
    fig = plt.figure(figsize=(x_pix / dpi, y_pix / dpi), dpi=dpi)
    ax = plt.axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    ax.set_global()
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)
    
    if directory is None:
        import datetime
        dt = datetime.datetime.now()
        import tempfile
        directory = tempfile.mkdtemp(prefix=dt.strftime("%Y%m%d_%H%M%S"))
    
    def create():
        import datetime
        dt = datetime.datetime.now()
        img_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.png')
        world_fname = os.path.join(directory, dt.strftime("%Y%m%d_%H%M%S") + '.wld')
        with open(img_fname, 'wb') as fh:
            fig.savefig(fh, facecolor='none', edgecolor='none', dpi=fig.dpi)
        world = dict(x_pix_size=360./x_pix, y_rotation=0, x_rotation=0,
                         y_pix_size=-180./y_pix, x_center=-180, y_center=90)

        from cartopy.tests.test_img_nest import _save_world
        _save_world(world_fname, world)
        add_layer(img_fname, layer_name=layer_name)
    
    return create, ax






def example():
    import datetime
    dt = datetime.datetime.now()
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix=dt.strftime("%Y%m%d_%H%M%S"))
    ax = new_layer(tmp_dir)
    
    plt.plot(range(10))
    ax.coastlines()
    plt.draw()
    #plt.plot(range(-10, 12))
    
    # Display in traditional form too?
    #plt.show(block=True)

if __name__ == '__main__':
    example()
#    plt.show()