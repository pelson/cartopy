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
    Control how the gridlines are drawn (top vs bottom), T, F
    
    Draw hook for gridline drawing notification, F, F
    Draw labels for other projections (such as rotated pole), F, F
    Control whether the gridlines & labels are re-drawn in interactive mode, F, F
    

 
Controlling the style of the gridlines
--------------------------------------

The gridlines draw are instances of matplotlib's :class:`~matplotlib.collections.Collection`.
It is possible to control the keywords used in the creation of the collection instance:
::

    gl.gridlines.style(edgecolor='red', alpha=0.3, linewidth=4)
    
The style method is additive (or updative) only. If you want to access the dictionary, you must access
the x and y gridlines' style dictionaries independently, e.g.:

    gl.gridlines.x.style_dict.pop('edgecolor')

 
Toggling gridlines and labels independently
-------------------------------------------

It is often desirable to draw gridlines or tick labels without drawing the
other. The :py:class:`~cartopy.mpl.gridliner.Gridliner` class supports this
by using the appropriate :py:class:`~cartopy.mpl.gridliner.Gridliner.gridlines` or
:py:class:`~cartopy.mpl.gridliner.Gridliner.labels` methods.

For example, to make the x gridlines invisible::

    gl.gridlines.x.visible = False
    
Or for all gridlines to be disabled::

    gl.gridlines.visible = False
 
For 'x' labels to be disabled::

    gl.labels.x.visible = False
    
Or for all labels::

    gl.labels.visible = False
 
Some gridliners have more than one set of labels (e.g. on both the left and right hand side of a map). 
To individually control these, indexing can be done::

    gl.labels.x[1].visible = False
    
Or even::

    gl.labels.x.pop(1)

Advanced: Adding new labels can be done by appending a Labeller1D instance::

    gl.labels.x.append(Labeller1D(...))
    
    
Controlling which gridlines & labels are drawn
----------------------------------------------


A convenience is supplied to define which ticks to draw::

    gl.set_xticks([0, 1, 3])
    gl.set_yticks([0, 1, 3])

Though for more control, , it is encouraged to use 
locators (for fixed ticks see :class:`matplotlib.ticker.FixedLocator`).


To control the gridlines and labels which are drawn`::
    
    gl.xlocator = degree_locator
    
    gl.ylocator = degree_locator
    
One can control the label values independently of the
gridlines themselves::

    gl.labels.y.locator = degree_locator
    

Format the labels which are drawn
---------------------------------

To control the label text for a tick, formatters are used::

    gl.labels.formatter = degree_formatter

    gl.labels.y.formatter = degree_formatter
    
    
Control where the labels are drawn (normally longitude)
-------------------------------------------------------

::
    
    gl.labels.x.positioner = line_near(x=45, trans=ax.transData)
    gl.labels.y.positioner = line_near(y=0, trans=ax.transData)
    
    # will only make sensible plots for circular patches, though should still work for others.
    gl.labels.y.positioner = on_boundary()
    
    
    gl.labels.y[0].positioner = line_near(y=0, trans=ax.transAxes) 
    gl.labels.y[1].positioner = line_near(y=1, trans=ax.transAxes)
    
    
    gl.labels.y.positioner = longest_straight_line(x=0, y=0)
    
    # XXX For bonus points. I don't think there is a direct need for this though.
    gl.labels.y.positioner = longest_straight_line(x=0, trans=ax.transAxes)
    

A mechanism should exist for defaulting these for various projections.


