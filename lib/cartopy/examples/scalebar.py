"""
Adaptive Scalebar
--------------------

Demonstrates cartopy's ability to draw scale bars that adapt their
scale based on pan/zoom. 

Note that because 

"""
__tags__ = ["Miscellanea"]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.mpl.scalebar import ScaleBarArtist, ScaleLineArtist


def main():
    ax1 = plt.subplot(1, 2, 1, projection=ccrs.OSGB())
    ax1.coastlines(resolution='10m')
    ax1.add_artist(ScaleBarArtist(location=(0.5, -0.05), max_width=1))
    ax1.stock_img()

    ax1.add_artist(ScaleBarArtist(location=(0.5, 0.05), max_width=1, units='miles'))

    ax1.add_artist(ScaleLineArtist(location=(0.1, 0.5), max_width=0.8, alignment='left'))
    ax1.add_artist(ScaleLineArtist(location=(0.1, 0.5), max_width=0.8, tick_text_y_offset=6, units='miles', alignment='left'))
    
    l = ScaleLineArtist(location=(0.1, 0.5), max_width=0.8, alignment='left')
    # Now try to rotate this.
    ax1.add_artist(l)

    # TODO: Support this (or at least allow use of Affine2D transform to do it manually.
#    ax1.add_artist(ScaleBarArtist(location=(0.95, 0.5), max_width=1, rotation=90))

    ax2 = plt.subplot(1, 2, 2, projection=ccrs.NorthPolarStereo())
    ax2.set_extent([-21, -95.5, 14, 76], ccrs.Geodetic())
    ax2.stock_img()
    ax2.coastlines(resolution='110m')
    ax2.add_artist(ScaleBarArtist(max_width=0.75))

    a = ScaleBarArtist(location=(0.5, 0.95), max_width=0.75)
    #a.bar_kwargs.set_color('red')
    a.tick_kwargs.update({'rotation': -90, 'va': 'top', 'visible': True})
    def strip(artist, context):
        artist.set_text(artist.get_text().strip())
    a.tick_kwargs._callbacks.append(strip)
    a.text_kwargs.set_visible(False)
    ax2.add_artist(a)
    #    scale_bar(ax, ccrs.Mercator(), 1000)  # 100 km scale bar

    # or to use m instead of km
    # scale_bar(ax, ccrs.Mercator(), 100000, m_per_unit=1, units='m')
    # or to use miles instead of km
    # scale_bar(ax, ccrs.Mercator(), 60, m_per_unit=1609.34, units='miles')

    plt.show()


if __name__ == '__main__':
    main()
