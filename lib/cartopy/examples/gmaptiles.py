# (C) British Crown Copyright 2011 - 2012, Met Office
#
# This file is part of cartopy.
#
# cartopy is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cartopy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cartopy.  If not, see <http://www.gnu.org/licenses/>.


# PLEASE NOTE: This example is a work in progress. It is anticipated that a tile generating 
# interface will simplify this significantly.

import matplotlib.pyplot as plt
import numpy

import cartopy
from cartopy.examples.waves import sample_data
import cartopy.io.img_tiles
import cartopy.crs as ccrs


def produce_axes2(ax):
    coords = [(-0.08, 51.53), (132.00, 43.17)] # London to Vladivostock
    r = ax.plot(*zip(*coords), transform=ll)

    x, y, z = sample_data()
    ax.contour(x, y, z, transform=ll)
    ax.coastlines()
    ax.gridlines()

def produce_axes(ax):
    import cartopy
    import cartopy.mpl.patch as pt
    import matplotlib.pyplot as plt
    import matplotlib.path as mpath
    import numpy

    import matplotlib.textpath
    import matplotlib.patches
    from matplotlib.font_manager import FontProperties

    pc = ccrs.PlateCarree()

    # create a transform from PlateCarree to the axes' projection
    pc_t = pc._as_mpl_transform(ax)

#    ax.coastlines()
#    ax.gridlines()
#    im = ax.stock_img()
    
    import os
    import cartopy
    source_proj = ccrs.PlateCarree()
    fname = os.path.join(cartopy.config["repo_data_dir"],
                         'raster', 'natural_earth',
                         '50-natural-earth-1-downsampled.png')
    img_origin = 'lower'
    img = plt.imread(fname)
    img = img[::-1]
    im = ax.imshow(img, origin=img_origin, transform=source_proj,
                     extent=[-180, 180, -90, 90], interpolation='none')
    
    name, pos = 'cartopy', (-180, -30)
    logo_path = matplotlib.textpath.TextPath(pos, name, size=1, prop=FontProperties(family='Arial', weight='bold'))
    # put the letters in the right place
    logo_path._vertices *= numpy.array([95, 160])
    
    im.set_clip_path(logo_path, transform=pc_t)
    

def main():
    prj = ccrs.Mercator()
    # set up a 1:1 ratio figure, which when saved will produce a 256x256 image
    f = plt.figure(figsize=[16, 16])
    ax = plt.axes(
                  [0, 0, 1, 1],
                  projection=prj,
                  frameon=False
                  )

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

#    produce_axes(ax)
#    ax.add_feature(cartopy.feature.GSHHSFeature(), lw=5)
    ax.coastlines('10m', linewidth=5)

    ax.patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)
    ax.set_aspect('auto')
    
    import shapely.geometry as sgeom
    geom = sgeom.box(-5, 50, 1, 52)
    
    gt = cartopy.io.img_tiles.GoogleTiles
    
    for i, j, z in gt.tiles_in_domain(geom, zmin=5, zmax=10):
        x_lim, y_lim = gt.tile_bbox(prj, i, j, z, bottom_up=True)
        print i, j, z, y_lim
        
        ax.set_xlim(x_lim)
        ax.set_ylim(y_lim)
        # Remove the previous display
        # This should be done automatically by MPL, but it is not... 
        # (http://old.nabble.com/Transparency-with-fig.canvas.mpl_connect-td27724532.html)
        plt.gcf().canvas.get_renderer().clear()
        plt.savefig('logo/z%s_y%s_x%s.png' % (z, j, i), dpi=16, transparent=True)

#    plt.show()
    


if __name__ == '__main__':
    main()
