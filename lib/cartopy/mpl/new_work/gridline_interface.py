class Gridliner(object):
    def __init__(self, gridlines, labels, xlocator=None, ylocator=None):
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
        
    @visible.setter
    def visible(self, value):
        self.x.visible = value
        self.y.visible = value


class Gridline1D(object):
    def __init__(self, style, visible=True):
        self.visible = visible
        self.style = style
    
    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}({}, visible={})'.format(class_name, 
                                           self.style, self.visible)
        

class Labeller2D(object):
    def __init__(self, xlabels, ylabels):
        self.x = xlabels
        self.y = ylabels
        
    @property
    def visible(self):
        """A *write-only* property to define whether the labels are visible."""
        return None
        
    @visible.setter
    def visible(self, value):
        self.x.visible = value
        self.y.visible = value
        
    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}(xlabels={},\n{indent}ylabels={})'.format(class_name,
                                                            self.x, self.y,
                                                            indent=' ' * (len(class_name) + 11))


class Labeller1D(object):
    def __init__(self, formatters, positioners, styles=None, visibles=None, n_labels=1):
        """
        n_labels is immutable.
        
        # XXX SHOULD YOU BE ABLE TO GIVE LOCATORS??? That is the question...
        
        """
        self._n_labels = n_labels 
        self._formatters = [None] * n_labels
        self._positioners = [None] * n_labels
        self._styles = [{} for _ in xrange(n_labels)]
        self._visibles = [True] * n_labels
        
        self.formatters = formatters
        self.positioners = positioners
        
        if styles is not None:
            self.styles = styles
        
        if visibles is not None:
            self.visibles = visibles
        
    @property
    def n_labels(self):
        return self._n_labels
    
    def __repr__(self):
        class_name = self.__class__.__name__
        format_str = '{}({}, {}, {}, {}, n_labels={})'
        return format_str.format(class_name,
                                 self._formatters, self._positioners,
                                 self._styles, self._visibles, 
                                 self.n_labels)
        
    @property
    def visibles(self):
        return tuple(self._visibles)
    
    @visibles.setter
    def visibles(self, value):
        if isinstance(value, basestring):
            raise TypeError()
        
        if len(value) != self.n_labels:
            raise ValueError('Wrong number of values given to visibles.')

        self._visibles = list(value)
        
    @property
    def style(self):
        """A *write-only* property to define the style of the labels."""
        return None
        
    @style.setter
    def style(self, value):
        self.styles = [value.copy() for _ in xrange(self.n_labels)]
        

    @property
    def styles(self):
        return tuple(self._styles)
    
    @styles.setter
    def styles(self, value):
        if isinstance(value, basestring):
            raise TypeError()
        
        if len(value) != self.n_labels:
            raise ValueError('Wrong number of values given to styles.')

        self._styles = list(value)

    
        
gliner = Gridliner(
                   Gridlines2D(
                               Gridline1D({'ec': 'gray'}),
                               Gridline1D({'ec': 'yellow'})
                               ),
                   labels=Labeller2D(Labeller1D([None, None], [None, None], n_labels=2),
                                     Labeller1D([None, None], [None, None], n_labels=2)
                                     )
                   )
print gliner.gridlines.x


print gliner.gridlines
print gliner
assert gliner.gridlines.x.visible == True and gliner.gridlines.y.visible == True
gliner.gridlines.visible = False
assert gliner.gridlines.x.visible == False and gliner.gridlines.y.visible == False
gliner.gridlines.x.visible = True
assert gliner.gridlines.x.visible == True and gliner.gridlines.y.visible == False



l = Labeller1D([None, None], [None, None], n_labels=2)

assert l.style is None
a_style_dict = {'ec': 'red'}
l.style = a_style_dict
assert l.style is None
print l.styles
assert l.styles == (a_style_dict.copy(), a_style_dict.copy())
assert isinstance(l.styles, tuple)


