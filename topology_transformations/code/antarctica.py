import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import shapely.geometry as sgeom


def continent(name):
    import cartopy.io.shapereader as shpreader

    shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_0_countries')
    reader = shpreader.Reader(shpfilename)
    countries = reader.records()
    shapes = []
    for country in countries:
        if country.attributes['continent'] == name:
            shapes.append(country.geometry)
    
    from shapely.ops import cascaded_union
    geom = cascaded_union(shapes)
    return geom


if __name__ == '__main__':
    LHS, RHS = ccrs.PlateCarree(), ccrs.Orthographic(0, -45)
    
    geom = continent('Antarctica')
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], ccrs.PlateCarree(), facecolor='gray', edgecolor='black', alpha=0.8)
    ax1.gridlines()
    ax2.add_geometries([geom], ccrs.PlateCarree(), facecolor='gray', edgecolor='black', alpha=0.8)
    ax2.gridlines()
    # ax1.set_extent([-180, 180, -90, 70], ccrs.PlateCarree())
    
    fig.subplots_adjust(left=0.05, right=0.95)
    
    plt.show()