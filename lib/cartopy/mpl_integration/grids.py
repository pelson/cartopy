

import numpy
import matplotlib.pyplot as plt
from matplotlib.artist import allow_rasterization

# XXX aalocators can be replaced once the locator interface is on master
import axisartist.locators as aalocators
import matplotlib.ticker as mticker


import cartopy.crs as ccrs


degree_locator = aalocators.MaxNLocator(nbins=9, steps=[1, 2, 3, 6, 15, 18])


def edge_line(ax, edge='bottom'):

    slice_lookup = {'bottom': slice(0, 2),
                    'right': slice(2, 4),
                    'top': slice(4, 6),
                    'left': slice(6, 8),
                    }
    slices = slice_lookup[edge]

    import cartopy.mpl_integration.patch as p
    import shapely.geometry as sgeom
    coords = ax.projection.boundary.coords
    bottom = sgeom.LineString(coords[slices])

    paths = p.geos_to_path(bottom)
    assert len(paths) == 1
    path = paths[0]

    import matplotlib.patches as mpatches

    patch = mpatches.PathPatch(path,
                               facecolor='none',
                               edgecolor='k',
                               zorder=1000,
                               clip_on=False, # clip is done by the transform
                                )
    ax.add_patch(patch)
    patch.set_transform(ax.sct)
    return patch


import matplotlib.lines as mlines
class AxisLine(mlines.Line2D):
    """
    represents the "spine" of the axis. ticks and labels are separate artists.
    """
    def __init__(self, *args, **kwargs):
        self.labels = []
        self.gridlines = []
        mlines.Line2D.__init__(self, *args, **kwargs)

    def _update_axis_ticks(self):
        print 'called'
        tr = ccrs.PlateCarree()._as_mpl_transform(self.axes)
        # xxx use the cached version???
        p = self._get_transformed_path().get_fully_transformed_path()
#        print type(p)
#        print p.vertices
        x = tr.inverted().transform(p.vertices)[:, 0]
#        x = transformed_path.vertices[:, 0]

        points = degree_locator.gen_tick_locations(numpy.nanmin(x), numpy.nanmax(x))

        for label in self.labels:
            label.remove()

        for gridline in self.gridlines:
            self.axes.lines.remove(gridline)
#            gridline.remove()
#            del gridline


        import matplotlib.transforms as mtransform
        print self.gridlines
        self.gridlines = []
        self.labels = []
        for pt in points:
            pc_to_prj = ccrs.PlateCarree()._as_mpl_transform(self.axes)

            import geoaxes
            pc_to_prj = geoaxes.InterProjectionTransform(ccrs.PlateCarree(), self.axes.projection) + self.axes.smt
#            pc_to_prj = pc_to_prj + self.get_transform()
#            pt_trans = pc_to_prj.transform([pt, 0])
            pos = pc_to_prj.transform([pt, 0.0])
            if pt == -60.0:
                print pt, pos

            if not numpy.any(pos.mask):
                self.labels.append(self.axes.text(pos[0], pos[1], str(pt),
    #                                               transform=self.axes.projection.as_geodetic(),
                                                   transform=mtransform.IdentityTransform(),
                                                   )
                                   )

                l = mlines.Line2D([pt, pt], [-80, 80],
                                                   transform=self.axes.projection.as_geodetic(),
                                                   clip_on=True,
                                                   color='gray',
                                                   linestyle='--',
                                                    )
                self.axes.add_line(l)
                self.gridlines.append(l)
#            for gridline in self.gridlines:
#
#                self.axes.add_line(gridline)
#                gridline.set_axes(self.axes)


#        print numpy.nanmin(x), numpy.nanmax(x)

    @allow_rasterization
    def draw(self, renderer):
        # remove the incorrectly cached spine line.
        # TODO: This could probably be fixed by setting some parent in the transform...
        self._transformed_path = None
        # update the axis ticks
        self._update_axis_ticks()
        return mlines.Line2D.draw(self, renderer)


def axis_line(ax, line='equator'):

    import cartopy.mpl_integration.patch as p
    import shapely.geometry as sgeom

#    ls = sgeom.LineString([(-180, 0), (180, 0)])
#    ls = sgeom.LineString([(0, 0), (360, 0)])

    import numpy
    n_seg = 100
    if line == 'equator':
        ls = sgeom.LineString(zip(numpy.linspace(-180, 180, n_seg), numpy.zeros(n_seg)))
    else:
        x = numpy.append(numpy.zeros(n_seg), numpy.zeros(n_seg) + 180)
        y = numpy.linspace(-90, 90, n_seg, endpoint=True)
        y = numpy.append(y, y[::-1])
        ls = sgeom.LineString(zip(x, y))
#
    # XXX plate carree should have the same central longitude... ???
    equator = ax.projection.project_geometry(ls,
                                             ccrs.PlateCarree(central_longitude=ax.projection.proj4_params.get('lon_0', -180))
                                             )
    import shapely.ops
    equator = shapely.ops.linemerge(equator)
    paths = p.geos_to_path(equator)
    assert len(paths) == 1
    path = paths[0]

    import matplotlib.patches as mpatches
    l = AxisLine(path.vertices[:, 0], path.vertices[:, 1],
                 lw=10)
#    patch = mpatches.PathPatch(path,
#                               facecolor='none',
#                               edgecolor='k',
#                               zorder=1000,
#                               lw=5,
#                               clip_on=False, # clip is done by the transform
#                               )
#    ax.add_patch(patch)
#    patch.set_transform(ax.sct)

    ax.add_line(l)
    l.set_transform(ax.smt)

    return l


if __name__ == '__main__':

    pc = ccrs.PlateCarree()
    rp = ccrs.RotatedPole(180, 45)
#    rp = ccrs.Robinson()
#    rp = ccrs.NorthPolarStereo()
    ax = plt.axes(projection=rp)
#    ax = plt.axes(projection=pc)

    ax.set_global()
    ax.coastlines()

    if True:

#        edge_line(ax, 'right')
        axis_line(ax)
#        axis_line(ax, line='meridian')

#    ax.xaxis.set_visible(True)
#    ax.yaxis.set_visible(True)
#    ax.grid(True)
#    ax.gridlines()

    plt.show()