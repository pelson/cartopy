# copied from matplotlib.ticker.
import numpy as np
from matplotlib import transforms as mtransforms



class TickHelper:
    axis = None
    class DummyAxis:
        def __init__(self):
            self.dataLim = mtransforms.Bbox.unit()
            self.viewLim = mtransforms.Bbox.unit()

        def get_view_interval(self):
            return self.viewLim.intervalx

        def set_view_interval(self, vmin, vmax):
            self.viewLim.intervalx = vmin, vmax

        def get_data_interval(self):
            return self.dataLim.intervalx

        def set_data_interval(self, vmin, vmax):
            self.dataLim.intervalx = vmin, vmax


    def set_axis(self, axis):
        self.axis = axis

    def create_dummy_axis(self):
        if self.axis is None:
            self.axis = self.DummyAxis()

    def set_view_interval(self, vmin, vmax):
        self.axis.set_view_interval(vmin, vmax)

    def set_data_interval(self, vmin, vmax):
        self.axis.set_data_interval(vmin, vmax)

    def set_bounds(self, vmin, vmax):
        self.set_view_interval(vmin, vmax)
        self.set_data_interval(vmin, vmax)

# xxx removes the need for an axis. will be better for contour too.
class Locator(TickHelper):
    """
    Determine the tick locations;

    Note, you should not use the same locator between different :class:`~matplotlib.axis.Axis`
    because the locator stores references to the Axis data and view
    limits
    """

    # some automatic tick locators can generate so many ticks they
    # kill the machine when you try and render them, see eg sf bug
    # report
    # https://sourceforge.net/tracker/index.php?func=detail&aid=2715172&group_id=80706&atid=560720.
    # This parameter is set to cause locators to raise an error if too
    # many ticks are generated
    MAXTICKS = 1000
    def __call__(self):
        'Return the locations of the ticks'
        raise NotImplementedError('Derived must override')

    def raise_if_exceeds(self, locs):
        'raise a RuntimeError if Locator attempts to create more than MAXTICKS locs'
        if len(locs)>=self.MAXTICKS:
            raise RuntimeError('Locator attempting to generate %d ticks from %s to %s: exceeds Locator.MAXTICKS'%(len(locs), locs[0], locs[-1]))

        return locs

    def view_limits(self, vmin, vmax):
        """
        select a scale for the range from vmin to vmax

        Normally This will be overridden.
        """
        return mtransforms.nonsingular(vmin, vmax)

    def autoscale(self):
        'autoscale the view limits'
        return self.view_limits(*self.axis.get_view_interval())

    def pan(self, numsteps):
        'Pan numticks (can be positive or negative)'
        ticks = self()
        numticks = len(ticks)

        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander = 0.05)
        if numticks>2:
            step = numsteps*abs(ticks[0]-ticks[1])
        else:
            d = abs(vmax-vmin)
            step = numsteps*d/6.

        vmin += step
        vmax += step
        self.axis.set_view_interval(vmin, vmax, ignore=True)


    def zoom(self, direction):
        "Zoom in/out on axis; if direction is >0 zoom in, else zoom out"

        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander = 0.05)
        interval = abs(vmax-vmin)
        step = 0.1*interval*direction
        self.axis.set_view_interval(vmin + step, vmax - step, ignore=True)

    def refresh(self):
        'refresh internal information based on current lim'
        pass


class MaxNLocator(Locator):
    """
    Select no more than N intervals at nice locations.
    """
    default_params = dict(nbins = 10,
                          steps = None,
                          trim = True,
                          integer=False,
                          symmetric=False,
                          prune=None)
    def __init__(self, *args, **kwargs):
        """
        Keyword args:

        *nbins*
            Maximum number of intervals; one less than max number of ticks.

        *steps*
            Sequence of nice numbers starting with 1 and ending with 10;
            e.g., [1, 2, 4, 5, 10]

        *integer*
            If True, ticks will take only integer values.

        *symmetric*
            If True, autoscaling will result in a range symmetric
            about zero.

        *prune*
            ['lower' | 'upper' | 'both' | None]
            Remove edge ticks -- useful for stacked or ganged plots
            where the upper tick of one axes overlaps with the lower
            tick of the axes above it.
            If prune=='lower', the smallest tick will
            be removed.  If prune=='upper', the largest tick will be
            removed.  If prune=='both', the largest and smallest ticks
            will be removed.  If prune==None, no ticks will be removed.

        """
        # I left "trim" out; it defaults to True, and it is not
        # clear that there is any use case for False, so we may
        # want to remove that kwarg.  EF 2010/04/18
        if args:
            kwargs['nbins'] = args[0]
            if len(args) > 1:
                raise ValueError(
                    "Keywords are required for all arguments except 'nbins'")
        self.set_params(**self.default_params)
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'nbins' in kwargs:
            self._nbins = int(kwargs['nbins'])
        if 'trim' in kwargs:
            self._trim = kwargs['trim']
        if 'integer' in kwargs:
            self._integer = kwargs['integer']
        if 'symmetric' in kwargs:
            self._symmetric = kwargs['symmetric']
        if 'prune' in kwargs:
            prune = kwargs['prune']
            if prune is not None and prune not in ['upper', 'lower', 'both']:
                raise ValueError(
                    "prune must be 'upper', 'lower', 'both', or None")
            self._prune = prune
        if 'steps' in kwargs:
            steps = kwargs['steps']
            if steps is None:
                self._steps = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]
            else:
                if int(steps[-1]) != 10:
                    steps = list(steps)
                    steps.append(10)
                self._steps = steps
        if 'integer' in kwargs:
            self._integer = kwargs['integer']
        if self._integer:
            self._steps = [n for n in self._steps if divmod(n,1)[1] < 0.001]

    def bin_boundaries(self, vmin, vmax):
        nbins = self._nbins
        scale, offset = scale_range(vmin, vmax, nbins)
        if self._integer:
            scale = max(1, scale)
        vmin -= offset
        vmax -= offset
        raw_step = (vmax-vmin)/nbins
        scaled_raw_step = raw_step/scale
        best_vmax = vmax
        best_vmin = vmin

        for step in self._steps:
            if step < scaled_raw_step:
                continue
            step *= scale
            best_vmin = step*divmod(vmin, step)[0]
            best_vmax = best_vmin + step*nbins
            if (best_vmax >= vmax):
                break
        if self._trim:
            extra_bins = int(divmod((best_vmax - vmax), step)[0])
            nbins -= extra_bins
        return (np.arange(nbins+1) * step + best_vmin + offset)


    def gen_tick_locations(self, vmin, vmax):
#        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander = 0.05)
        locs = self.bin_boundaries(vmin, vmax)
        #print 'locs=', locs
        prune = self._prune
        if prune=='lower':
            locs = locs[1:]
        elif prune=='upper':
            locs = locs[:-1]
        elif prune=='both':
            locs = locs[1:-1]
        return self.raise_if_exceeds(locs)

    def view_limits(self, dmin, dmax):
        if self._symmetric:
            maxabs = max(abs(dmin), abs(dmax))
            dmin = -maxabs
            dmax = maxabs
        dmin, dmax = mtransforms.nonsingular(dmin, dmax, expander = 0.05)
        return np.take(self.bin_boundaries(dmin, dmax), [0,-1])


class AutoLocator(MaxNLocator):
    def __init__(self):
        MaxNLocator.__init__(self, nbins=9, steps=[1, 2, 5, 10])


def scale_range(vmin, vmax, n = 1, threshold=100):
    dv = abs(vmax - vmin)
    maxabsv = max(abs(vmin), abs(vmax))
    if maxabsv == 0 or dv/maxabsv < 1e-12:
        return 1.0, 0.0
    meanv = 0.5*(vmax+vmin)
    if abs(meanv)/dv < threshold:
        offset = 0
    elif meanv > 0:
        ex = divmod(np.log10(meanv), 1)[0]
        offset = 10**ex
    else:
        ex = divmod(np.log10(-meanv), 1)[0]
        offset = -10**ex
    ex = divmod(np.log10(dv/n), 1)[0]
    scale = 10**ex
    return scale, offset
