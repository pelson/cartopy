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

def remove_interiors(geom):
    geoms = []
    for p in geom:
        geoms.append(sgeom.Polygon(p.exterior))
    geom = sgeom.MultiPolygon(geoms)
    return geom


LHS, RHS = ccrs.PlateCarree(), ccrs.PlateCarree(central_longitude=180)

geom = continent('Africa')
geom = remove_interiors(geom)

fig = plt.figure(figsize=(7, 2))

ax1 = plt.subplot(1, 2, 1, projection=LHS)
ax2 = plt.subplot(1, 2, 2, projection=RHS)

ax1.coastlines(color='gray', alpha=0.4)
ax2.coastlines(color='gray', alpha=0.4)

bbox_props = dict(boxstyle="rarrow", fc=(0.8,0.9,0.9), ec="b", lw=2)

t = fig.text(0.475, 0.5, "Transform", transform=fig.transFigure, ha="center", va="center",
            size=15, bbox=bbox_props, zorder=10)

ax1.add_geometries([geom], LHS, facecolor='gray', edgecolor='black', alpha=0.8)
ax2.add_geometries([geom], LHS, facecolor='gray', edgecolor='black', alpha=0.8)

fig.subplots_adjust(wspace=0.4, left=0.05, right=0.95)

plt.show()