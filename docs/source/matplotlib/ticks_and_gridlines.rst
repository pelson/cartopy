Drawing ticks and gridlines on the matplotlib GeoAxes
=====================================================

Drawing gridlines and tick labels is a common requirement when drawing maps.
Because of the curvilinear nature of some of the projections that Cartopy supports,
Cartopy has diverged from the standard matplotlib tick and grid interface.

The primary class for dealing with gridlines and tick labels is the 
:py:class:`cartopy.mpl.gridliner.Gridliner`. The convenience method
:py:class:`GeoAxes.gridlines <cartopy.mpl.geoaxes.GeoAxes.gridlines>` exists to construct
a :py:class:`~cartopy.mpl.gridliner.Gridliner` instance for a given
:py:class:`~cartopy.mpl.geoaxes.GeoAxes` instance - this is generally
the first step to adding gridlines and tick labels to any map. 


.. autoclass:: cartopy.mpl.gridliner.Gridliner


Functionality:

.. csv-table::

    Draw x or y only gridlines and/or labels, T, F
    Draw gridlines without labels, T, F
    Draw labels without gridlines, T, F
    Control the labels & gridlines which are drawn, T, F
    Format the labels which are drawn, T, F
    Control where the labels are drawn (normally longitude), T, F
    Control where the labels are drawn (top vs bottom), T, F
    
    Draw hook for gridline drawing notification, F, F
    Draw labels for other projections (such as rotated pole), F, F
    Control whether the gridlines & labels are re-drawn in interactive mode, F, F
    

 
Toggling gridlines and labels independently
-------------------------------------------

It is often desirable to draw gridlines or tick labels without drawing the
other. The :py:class:`~cartopy.mpl.gridliner.Gridliner` class supports this
by using the appropriate :py:class:`~cartopy.mpl.gridliner.Gridliner.gridlines` or
:py:class:`~cartopy.mpl.gridliner.Gridliner.labels` methods.

For example, to make the x gridlines invisible::

    gl.gridlines['x'].visible = False
    
Or for all gridlines to be disabled::

    gl.gridlines.visible = False
 
For 'x' labels to be disabled::

    gl.labels['x'].visible = False
    
Or for all labels::

    gl.labels.visible = False
    
    
Controlling which gridlines & labels are drawn
----------------------------------------------

To control the ticks which are drawn, several methods are provided
:py:class:`~cartopy.mpl.gridliner.Gridliner.locators`::
    
    gl.xlocator = degree_locator
    
    gl.ylocator = degree_locator
    
A special meaning allows one to control the top/bottom or left/right locators for labels independently
from the gridlines themselves::

    gl.labels['y'].locator = degree_locator

    gl.labels['x'].locators = [degree_locator, None]
    gl.labels['y'].locators = [degree_locator, None]


Format the labels which are drawn
---------------------------------

To control the label text for a tick, formatters are used::

    gl.labels.formatter = degree_formatter

    gl.labels['y'].formatter = degree_formatter

    # (should not be mutable & should always be of the same length as the number of label rows)
    gl.labels['x'].formatters = [degree_formatter, degree_formatter]
    gl.labels['y'].formatters = [degree_formatter, degree_formatter]
    
    
Control where the labels are drawn (normally longitude)
-------------------------------------------------------

::
    
    gl.labels['x'].positioner = line_near(x=45, trans=ax.transData)
    gl.labels['y'].positioner = line_near(y=0, trans=ax.transData)
    
    # will only make sensible plots for circular patches, though should still work for others.
    gl.labels['y'].positioner = on_boundary()
    
    
    gl.labels['y'].positioners = [line_near(y=0, trans=ax.transAxes), line_near(y=1, trans=ax.transAxes)]
    
    
    gl.labels['y'].positioner = longest_straight_line(x=0, y=0)
    
    # XXX For bonus points. I don't think there is a direct need for this though.
    gl.labels['y'].positioners = [longest_straight_line(x=0, trans=ax.transAxes)]
    

A mechanism should exist for defaulting these for various projections.


