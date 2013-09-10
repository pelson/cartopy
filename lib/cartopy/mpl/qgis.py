from __future__ import absolute_import
import os

def add_layer(fname):
    import qgis.core
    baseName = os.path.basename(fname)
    raster_layer = qgis.core.QgsRasterLayer(fname, baseName)
    if not raster_layer.isValid():
        print "Layer failed to load!"
    
    qgis.core.QgsMapLayerRegistry.instance().addMapLayer(raster_layer)
    
    return raster_layer
    # Needed? 


def refresh_layer(layer):
    if hasattr(layer, "setCacheImage"):
        layer.setCacheImage(None)
    layer.triggerRepaint()


import matplotlib
matplotlib.use('TkAgg')
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


def new_layer():
    import cartopy.crs as ccrs
    fig = plt.figure(figsize=(20, 10))
    # Draw the empty figure to create a _cachedRenderer attribute.
    import tempfile
    fh = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    fig.savefig(fh, facecolor='none', edgecolor='none')
    fname = fh.name
    print fname
    fh.close()
    import types
    fig.original_draw = fig.draw
    fig._qgis_fname = fname
#    fig._qgis_layer = add_layer(fname)
    def new_draw(self, renderer):
        print 'draw called'
        self.was_drawn = True
        # XXX Handle updating of the qgis layer. (perhaps checksum the image)
        fig.draw = fig.original_draw
        fig.savefig(fname, facecolor='none', edgecolor='none', dpi=fig.dpi)
        fig.draw = fig.new_draw
#        refresh_layer(self._qgis_layer)
        
        self.original_draw(renderer)

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


def example():
    ax = new_layer()
    
    plt.plot(range(10))
    ax.coastlines()
    #plt.plot(range(-10, 12))
    
    # Display in traditional form too?
    #plt.show(block=True)

if __name__ == '__main__':
    example()
#    plt.show()