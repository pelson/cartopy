__tags__ = ['Lines and polygons']
import matplotlib.pyplot as plt

import cartopy.crs as ccrs


def main():
    ax = plt.axes(projection=ccrs.Mercator())
    ax.set_extent([-90, -45, -60, -30])

    ax.stock_img()
    ax.coastlines()
    
    gl = ax.gridlines(draw_labels=True)
    import matplotlib.ticker as mticker
    
    gl.xlocator = mticker.FixedLocator(range(-90, -45, 4)) 
    
    plt.show()


if __name__ == '__main__':
    main()
