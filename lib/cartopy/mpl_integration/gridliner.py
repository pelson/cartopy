import matplotlib
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.collections as mcollections


import numpy

#
#class GridlineDomain(object):
#    def __init__(self, min_v, max_v):
#        self.min_v, self.max_v = min_v, max_v

class Gridliner(object):
    DEBUG = False
    def __init__(self, axes):
        self.axes = axes
        self.gridlines = {}

    def do_gridlines(self, ax_transform, transform, nx=None, ny=None, background_patch=None):
        x_lim, y_lim = self.get_domain(ax_transform, transform, nx=nx, ny=ny, background_patch=background_patch)

        rc_params = matplotlib.rcParams

        n_steps = 100
        n_ticks = 10

        lines = []
        for x in numpy.linspace(x_lim[0], x_lim[1], n_ticks, endpoint=False):
            l = zip(numpy.zeros(n_steps) + x, numpy.linspace(y_lim[0], y_lim[1], n_steps, endpoint=True))
            lines.append(l)

        lc = mcollections.LineCollection(lines,
                                     color=rc_params['grid.color'],
                                     linestyle=rc_params['grid.linestyle'],
                                     linewidth=rc_params['grid.linewidth'],
                                     # XXX Should only draw in data or axes coordinates?
                                     transform=transform,
                                     )
        self.gridlines['x'] = lc
        self.axes.add_collection(lc, autolim=False)


        lines = []
        for y in numpy.linspace(y_lim[0], y_lim[1], n_ticks, endpoint=False):
            l = zip(numpy.linspace(x_lim[0], x_lim[1], n_steps, endpoint=True),
                              numpy.zeros(n_steps) + y)
            lines.append(l)

        lc = mcollections.LineCollection(lines,
                                     color=rc_params['grid.color'],
                                     linestyle=rc_params['grid.linestyle'],
                                     linewidth=rc_params['grid.linewidth'],
                                     # XXX Should only draw in data or axes coordinates?
                                     transform=transform,
                                     )
        self.gridlines['y'] = lc
        self.axes.add_collection(lc, autolim=False)

    def get_domain(self, ax_transform, transform, nx=None, ny=None, background_patch=None):
        """Returns x_range, y_range"""
        desired_trans = ax_transform - transform

        nx = nx or 5
        ny = ny or 5
        x = numpy.linspace(0., 1, nx)
        y = numpy.linspace(0., 1, ny)
        x, y = numpy.meshgrid(x, y)

        coords = numpy.concatenate([x.flatten()[:, None], y.flatten()[:, None]], 1)

        in_data = desired_trans.transform(coords)

        ax_to_bkg_patch = self.axes.transAxes - background_patch.get_transform()

        ok = numpy.zeros(in_data.shape[:-1], dtype=numpy.bool)
        # XXX Vectorise contains_point
        for i, val in enumerate(in_data):
                # convert the coordinates of the data to the background patches coordinates
                background_coord = ax_to_bkg_patch.transform(coords[i:i+1, :])
                if background_patch.get_path().contains_point(background_coord[0, :]):
                    color = 'r'
                    ok[i] = True
                else:
                    color = 'b'

                if self.DEBUG:
                    plt.plot(coords[i, 0], coords[i, 1], 'o' + color, clip_on=False, transform=ax_transform)
#                plt.text(coords[i, 0], coords[i, 1], str(val), clip_on=False,
#                         transform=ax_transform, rotation=23,
#                         horizontalalignment='right')

        inside = in_data[ok, :]
        x_range = numpy.nanmin(inside[:, 0]), numpy.nanmax(inside[:, 0])
        y_range = numpy.nanmin(inside[:, 1]), numpy.nanmax(inside[:, 1])
        return x_range, y_range

class PolarGridliner(Gridliner):
    def get_domain(self, ax_transform, transform, nx, ny, background_patch=None):
        # the polar domain is fixed except for the extent of r
        _, r_range = Gridliner.get_domain(self, ax_transform, transform, nx, ny, background_patch=background_patch)
        return [0, 2 * numpy.pi], [0, r_range[1]]


if __name__ == '__main__':

    import matplotlib.pyplot as plt
    import cartopy
    ax = plt.axes(projection='polar')
#    ax = plt.axes(projection=cartopy.prj.NorthPolarStereo())
    ax = plt.gca()
    r = plt.plot(range(10), range(10))

    gl = Gridliner(ax)
#    gl = PolarGridliner(ax)

#    ax.set_global()

#    print gl.get_domain(ax.transAxes, cartopy.prj.PlateCarree()._as_mpl_transform(ax), background_patch=ax.patch)
    print gl.get_domain(ax.transAxes, ax.transAxes, nx=50, ny=50, background_patch=ax.patch)
#    print gl.get_domain(ax.transAxes, ax.transData, nx=50, ny=50, background_patch=ax.patch)
#    gl.do_gridlines(ax.transAxes, ax.transData, background_patch=ax.patch)
    gl.do_gridlines(ax.transAxes, ax.transAxes, nx=50, ny=50, background_patch=ax.patch)
#    gl.do_gridlines(ax.transAxes, cartopy.prj.PlateCarree()._as_mpl_transform(ax), background_patch=ax.patch)
#    plt.plot(0, 0, 'bo', transform=ax.transAxes, clip_on=False)
    plt.grid(False)

#    ax.gshhs_line(resolution='coarse')

    plt.draw()
    plt.show()