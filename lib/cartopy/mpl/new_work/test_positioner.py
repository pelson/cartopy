from nose.tools import assert_equal, assert_raises

from numpy.testing import assert_array_almost_equal
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from cartopy.mpl.new_work.positioner import where_on_line


class Test_where_on_line(object):

    def setup(self):
        self.ax = plt.axes()
        # make sensible limits for the axes
        self.ax.set_ylim([0, 70])
        self.ax.set_xlim([-1, 4])
        
        self.line = mlines.Line2D([0, 0, 2, 3, 3, 2], 
                                  [10, 20, 30, 40, 50, 20],
                                  transform=self.ax.transData) 
        self.ax.add_line(self.line)

    def test_x(self):
        l = self.line 
        
        with assert_raises(ValueError):
            where_on_line(l, x=-1.5, xy_trans=self.ax.transData)
            
        with assert_raises(ValueError):
            where_on_line(l, x=3.1, xy_trans=self.ax.transData)
    
        # XXX Double check these values
        x_to_val = ((0, [[0], [20]]),
                    (1, [[1], [25]]),
                    (3, [[3, 3], [40, 50]]),
                    (2.5, [[2.5], [35]]),
                    )
        
        for x, expected in x_to_val:
            result = where_on_line(l, x=x, xy_trans=self.ax.transData)
            msg = ('where_on_line returned an unexpected position for x={!r}. '
                   'Got {}, expected {}.'.format(x, result, expected))
            assert_array_almost_equal(result, expected, err_msg=msg)
            
    def test_y(self):
        l = self.line 
        
        with assert_raises(ValueError):
            where_on_line(l, y=0, xy_trans=self.ax.transData)
            
        with assert_raises(ValueError):
            where_on_line(l, y=55, xy_trans=self.ax.transData)
    
        # XXX Double check these values
        y_to_val = (
#                    (10, [[0], [10]]),
                    (20, [[0, 2], [20, 20]]),
                    (25, [[1, 2.16666667], [25, 25]]),
                    (50, [[3], [50]]),
                    )
        
        for y, expected in y_to_val:
            result = where_on_line(l, y=y, xy_trans=self.ax.transData)
            msg = ('where_on_line returned an unexpected position for y={!r}. '
                   'Got {}, expected {}.'.format(y, result, expected))
            assert_array_almost_equal(result, expected, err_msg=msg)

    def test_different_coordinate_systems(self):
        xy = where_on_line(self.line, x=0.75, xy_trans=self.ax.transAxes)
        assert_array_almost_equal(xy, [[0.75, 0.75], [0.53571429, 0.60714286]])
        
        xy = where_on_line(self.line, x=0.25, xy_trans=self.ax.transAxes)
        assert_array_almost_equal(xy, [[0.25], [0.30357143]])
        
        xy = where_on_line(self.line, x=0.5, xy_trans=self.ax.transAxes)
        assert_array_almost_equal(xy, [[0.5], [0.39285714]])
        
        xy = where_on_line(self.line, y=0.5, xy_trans=self.ax.transAxes)
        assert_array_almost_equal(xy, [[0.7], [0.5]])
        
        xy = where_on_line(self.line, y=0.25, xy_trans=self.ax.transAxes)
        assert_array_almost_equal(xy, [[0.2], [0.25]])


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-s', '--with-doctest'], exit=False)
