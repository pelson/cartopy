import numpy as np

import matplotlib.ticker as mticker
import matplotlib.collections as mcollections
from matplotlib import rcParams

class Gridliner(object):
    def __init__(self, axes, crs, gridlines, labels, xlocator=None, ylocator=None):
        self.axes = axes
        self.crs = crs
        self.xlocator = xlocator
        self.ylocator = ylocator
        self.gridlines = gridlines
        self.labels = labels

    def __repr__(self):
        class_name = self.__class__.__name__
        # split the __repr__ over 4 lines to make it more readable.
        format_str = '{}({},\n{indent}{},''\n{indent}{},\n{indent}{})'
        return format_str.format(class_name, 
                                 self.xlocator, self.ylocator,
                                 self.gridlines, self.labels,
                                 indent=' ' * (len(class_name) + 1))
        
    def draw(self, renderer):
        x_lim = [-180, 180]
        y_lim = [-90, 90]
        
        xticks = self.xlocator.tick_values(*x_lim)
        yticks = self.ylocator.tick_values(*y_lim)
#        transform = self.crs
#        if not isinstance(transform, mtrans.Transform):
#            transform = transform._as_mpl_transform(self.axes)
        transform = None
        line_collections = []
        for gridline_1D in self.gridlines:
            if gridline_1D.visible:
                col = gridline_1D.create_collection(xticks, yticks, transform)
                line_collections.append(col)
        
        labels = self.labels.draw_labels(xlim, ylim, transform)

        
        


class Gridlines2D(object):
    def __init__(self, xgridline, ygridline):
        self.x = xgridline
        self.y = ygridline

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}(xgridline={}, ygridline={})'.format(class_name, 
                                                       self.x, self.y)
        
    @property
    def visible(self):
        """A *write-only* property to define whether the gridlines are visible."""
        return None
    
    def __iter__(self):
        return iter([self.x, self.y])
    
    @visible.setter
    def visible(self, value):
        self.x.visible = value
        self.y.visible = value
        
    def style(self, **kwargs):
        for item in [self.x, self.y]:
            item.style(**kwargs)
            
class Gridline1D(object):
    def __init__(self, style, visible=True, interp_steps=30):
        self.visible = visible
        self.style_dict = style
        self.interp_steps = interp_steps
    
    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}({}, visible={})'.format(class_name, 
                                           self.style_dict, self.visible)
        
    def style(self, **kwargs):
        self.style_dict.update(kwargs)
        
    def create_collection(self, xticks, yticks, transform):
        collection_kwargs = {}
        # TODO doesn't gracefully handle aliases (e.g. lw & linewidth)
        collection_kwargs.setdefault('color', rcParams['grid.color'])
        collection_kwargs.setdefault('linestyle', rcParams['grid.linestyle'])
        collection_kwargs.setdefault('linewidth', rcParams['grid.linewidth'])
        
        collection_kwargs.update(self.style_dict)
        collection_kwargs['transform'] = transform

        lc = mcollections.LineCollection(list(self._line_coords(xticks, yticks)), 
                                           **collection_kwargs)
        return lc        
    
    def _line_coords(self, xticks, yticks):
        """
        Returns a generator of line segments suitable for 
        :class:`matplotlib.collections.LineCollection`.
        """
        # XXX Do we *really* need ABC?
        raise ValueError('Subclass should implement.')
        
        
class XGridline(Gridline1D):
    def _line_coords(self, xticks, yticks):
        for x in xticks:
            line_segment = zip(np.zeros(self.interp_steps) + x,
                               np.linspace(min(yticks), max(yticks),
                                           self.interp_steps, endpoint=True)
                               )
            yield line_segment


class YGridline(Gridline1D):
    def _line_coords(self, xticks, yticks):
        for y in yticks:
            line_segment = zip(np.linspace(min(xticks), max(yticks),
                                           self.interp_steps),
                               np.zeros(self.interp_steps) + y)
            yield line_segment

class Labeller2D(object):
    def __init__(self, xlabels, ylabels):
        self.x = xlabels
        self.y = ylabels
        
    def __iter__(self):
        return iter([self.x, self.y])
    
    def draw_labels(self, xlim, ylim, transform):
        
        labels = []
        for labeller_1D in self.x:
            if labeller_1D.visible:
                xticks = labeller_1D.locator(*xlim)
                
        for labeller_1D in self.y:
            if labeller_1D.visible:
                yticks = labeller_1D.locator(*ylim)
                tick_positions = labeller_1D.positioner(yticks)
                for (tick_x, tick_y), tick_val in zip(tick_positions, yticks):
                    tick_str = labeller_1D.formatter
                    # ax.text(tick_x, tick_y, 
                
#            if labeller_1D.visible:
#                xticks = labeller_1D.locator(*x_lim)
#                yticks = self.ylocator.tick_values(*y_lim)
#                labs = labeller_1D.
    
    @property
    def visible(self):
        """A *write-only* property to define whether the labels are visible."""
        return None
        
    @visible.setter
    def visible(self, value):
        for item in self:
            item.visible = value
        
    @property
    def formatter(self):
        """A *write-only* property to define the label formatter."""
        return None
        
    @formatter.setter
    def formatter(self, value):
        for item in self:
            item.formatter = value
        
    @property
    def positioner(self):
        """A *write-only* property to define the label positioner."""
        return None
        
    @positioner.setter
    def positioner(self, value):
        for item in self:
            item.positioner = value
            
    @property
    def locator(self):
        """A *write-only* property to define the label locator."""
        return None
        
    @locator.setter
    def locator(self, value):
        for item in self:
            item.locator = value
            
    def style(self, **kwargs):
        for item in self:
            item.style(**kwargs)
        
    def __repr__(self):
        class_name = self.__class__.__name__
        indent_str =' ' * (len(class_name) + 11)
        return '{}(xlabels={},\n{indent}ylabels={})'.format(class_name,
                                                            self.x, self.y,
                                                            indent=indent_str)


class Labeller1DList(list):
    """
    Represents multiple rows or columns of labels.
    In Cartesian form this could represent both the left 
    and right hand side y axis labels.
    
    """
    @property
    def visible(self):
        """A *write-only* property to define whether the labels are visible."""
        return None
        
    @visible.setter
    def visible(self, value):
        for item in self:
            item.visible = value
 
    @property
    def formatter(self):
        """A *write-only* property to define the label formatter."""
        return None
        
    @formatter.setter
    def formatter(self, value):
        for item in self:
            item.formatter = value
            
    @property
    def positioner(self):
        """A *write-only* property to define the label positioner."""
        return None
        
    @positioner.setter
    def positioner(self, value):
        for item in self:
            item.positioner = value
            
    @property
    def locator(self):
        """A *write-only* property to define the label locator."""
        return None
        
    @locator.setter
    def locator(self, value):
        for item in self:
            item.locator = value

    def style(self, **kwargs):
        for item in self:
            item.style(**kwargs)


class Labeller1D(object):
    """
    Represents a single column of labels.
    
    In Cartesian form this could be the left hand y axis labels.
    
    """
    
    def __init__(self, formatter, positioner, locator, style=None, visible=True):
        self.formatter = formatter
        self.positioner = positioner
        self.locator = locator
        self.style_dict = style or {}
        self.visible = visible
        
    def __repr__(self):
        class_name = self.__class__.__name__
        format_str = '{}({}, {}, {}, {}, visible={})'
        return format_str.format(class_name,
                                 self.formatter, self.positioner,
                                 self.locator,
                                 self.style_dict, self.visible)
        
    
    def style(self, **kwargs):
        self.style_dict.update(kwargs)
 

        
gliner = Gridliner(None, None,
                   Gridlines2D(
                               XGridline({'edgecolor': 'gray'}),
                               YGridline({'color': 'yellow'})
                               ),
                   labels=Labeller2D(
                                     Labeller1DList([Labeller1D([None, None], [None, None], None)]),
                                     Labeller1DList([Labeller1D([None, None], [None, None], None)])
                                     ),
                   xlocator=mticker.AutoLocator(),
                   ylocator=mticker.AutoLocator()
                   )
print gliner.gridlines.x


print gliner.gridlines
print gliner
assert gliner.gridlines.x.visible == True and gliner.gridlines.y.visible == True
gliner.gridlines.visible = False
assert gliner.gridlines.x.visible == False and gliner.gridlines.y.visible == False
gliner.gridlines.x.visible = True
assert gliner.gridlines.x.visible == True and gliner.gridlines.y.visible == False


assert gliner.labels.x[0].visible == True and gliner.labels.y[0].visible == True
gliner.labels.x.visible = False
assert gliner.labels.x[0].visible == False and gliner.labels.y[0].visible == True
gliner.labels.visible = False
gliner.labels.x.visible = True
assert gliner.labels.x[0].visible == True and gliner.labels.y[0].visible == False


l = Labeller1D(None, None, None)

assert l.style_dict == {}
a_style_dict = {'ec': 'red'}
l.style(**a_style_dict)
assert l.style_dict == a_style_dict
l.style_dict.pop('ec')
assert l.style_dict == {}


gliner.draw(None)
