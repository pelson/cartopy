__tags__ = ['Lines and polygons']
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
import cartopy.feature

# http://nsidc.org/data/seaice_index/archives.html
# ftp://sidads.colorado.edu/DATASETS/NOAA/G02135/shapefiles/






def main():
    ax = plt.axes(projection=ccrs.SouthPolarStereo())

    # Limit the map to -60 degrees latitude and below.
    ax.set_extent([-180, 180, -90, -60], ccrs.PlateCarree())

    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.OCEAN)

    # Compute a circle in axes coordinates, which we can use as a boundary
    # for the map. We can pan/zoom as much as we like - the boundary will be
    # permanently circular.
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)

    ax.set_boundary(circle, transform=ax.transAxes)

    plt.show()


if __name__ == '__main__':
#     main()
    from cartopy.io import GenericDownloader

#     url = 'ftp://sidads.colorado.edu/DATASETS/NOAA/G02135/shapefiles/Jan/shp_extent/extent_S_201501_polygon.zip'
#     url = 'ftp://sidads.colorado.edu/DATASETS/NOAA/G02135/shapefiles/Aug/shp_extent/extent_S_201408_polygon.zip'

#     for 

    url_template = ('ftp://sidads.colorado.edu/DATASETS/NOAA/G02135/'
                    'shapefiles/{month_name}/shp_extent/'
                    'extent_S_{year:04d}{month_number:02d}_polygon.zip')

    ax = plt.axes(projection=ccrs.SouthPolarStereo())

    month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    ax.set_global()
#     ax.stock_img()
    plt.ion()
    plt.show()
    feature = None
    for year in range(2000, 2015):
        for month_num, month in enumerate(month_name, start=1):
            if feature is not None:
                feature.remove()
            url = url_template.format(year=year, month_number=month_num, month_name=month)
            shp_feature = cartopy.feature.ShapefileFeature(GenericDownloader(url, 'ice_extent').path())

            feature = ax.add_feature(shp_feature, facecolor='#A5F2F3', edgecolor='gray', alpha=0.2)
            plt.draw()
            plt.pause(0.5)
    plt.ioff()
    plt.show()

    # ftp://sidads.colorado.edu/DATASETS/NOAA/G02135/shapefiles/Jan/shp_extent/extent_S_201501_polygon.zip
    pass