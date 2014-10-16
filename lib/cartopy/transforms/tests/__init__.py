import cartopy.crs as ccrs
import cartopy.transforms.clipping
from cartopy.transforms.interpolate import great_circle_interpolation
from cartopy.transforms.geom_interpolate import interpolate_and_project_path, Precision

from cartopy.transforms.apply_topolgy import geom_apply_topology




if __name__ == '__main__':
    import matplotlib.path as mpath
    from functools import partial

    do_africa = False

    rotation = -70
    proj = ccrs.Robinson(central_longitude=-rotation)
    precision = 4e6

    path = mpath.Path([[-180, 90], [0, 90], [180, 90], [180, 0], [180, -90],
                       [0, -90], [-180, -90], [-180, 0], [-180, 90]])


    print 'Prec {}; XLim: {}'.format(precision, proj.x_limits)
    transform_point = proj.transform_point

    trans_fn = partial(transform_point, src_crs=ccrs.Geodetic())
    result = []

    def unrotate(x, y):
        return x - rotation, y

    def project_fn(x, y):
        x, y = ccrs.Geodetic().transform_point(x, y, ccrs.PlateCarree())
#        return trans_fn(*pt)
        return trans_fn(*unrotate(x, y))

    precision = Precision(precision, 30)
    new_path = interpolate_and_project_path(path, project_fn, great_circle_interpolation, precision=precision)

    if do_africa:
        # Africa
        import cartopy.io.shapereader as shpreader
        shpfilename = shpreader.natural_earth(resolution='110m',
                                          category='cultural',
                                          name='admin_0_countries')
        reader = shpreader.Reader(shpfilename)
        countries = reader.records()
        shapes = []
        for country in countries:
            if country.attributes['continent'] == 'Africa':
                shapes.append(country.geometry)
        import cartopy.mpl.patch as cpatch
        from shapely.ops import cascaded_union
        africa = cpatch.geos_to_path(cascaded_union(shapes))
        africa = mpath.Path.make_compound_path(*africa)

        africa_interp = interpolate_and_project_path(africa, trans_fn, great_circle_interpolation, precision=precision)


#    import cartopy.transforms.topology as topology
#    topo = [topology.CutLine([[180, -90], [180, 90]])]
#    segments = [(-50, 20), (50, 20), (50, -20), (-50, -20)]
#    segments = [unrotate(*seg) for seg in segments]
#    segments = geom_apply_topology(segments, topo, closed=True)
#    print segments






    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch

    plt.figure(figsize=(18, 8))
    ax = plt.subplot(1, 2, 1)
    ax.add_patch(PathPatch(path, facecolor='yellow', edgecolor='red'))
    if do_africa:
        ax.add_patch(PathPatch(africa, facecolor='green', edgecolor='black'))
    ax.autoscale_view()

    print path.vertices.shape, new_path.vertices.shape

    ax = plt.subplot(1, 2, 2)
    ax.add_patch(PathPatch(new_path, facecolor='yellow', edgecolor='red'))
    if do_africa:
        ax.add_patch(PathPatch(africa_interp, facecolor='green', edgecolor='black', zorder=2))
    ax.autoscale_view()
    plt.show()
