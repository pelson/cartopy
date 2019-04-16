Topology transformations for R3=>R2 projections
===============================================

.. toctree::
   
    cartopy_geometry_pipeline


Band in PC => Two bands in PC180
================================

.. plot::
    
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(), ccrs.PlateCarree(central_longitude=180)
    geom = sgeom.box(-90, -40, 90, 40)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()

Two bands in PC => Bands in PC180
==================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(), ccrs.PlateCarree(central_longitude=180)
    geom = sgeom.MultiPolygon([sgeom.box(-180, -40, -90, 40),
                               sgeom.box(90, -40, 180, 40)])
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()


Band in PC => Doghnut in NPS
============================

.. plot::
    
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(), ccrs.NorthPolarStereo()
    geom = sgeom.box(-180, -40, 180, 40)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()


Band in PC => Full exterior in NPS
==================================

.. plot::
    
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(), ccrs.NorthPolarStereo()
    geom = sgeom.box(-180, -90, 180, -20)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()


Circle in NPS => Band in PC
===========================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.NorthPolarStereo(), ccrs.PlateCarree()
    geom = sgeom.Point(0, 0).buffer(10000000)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()
  
  
Doughnut in NPS => Band in PC
=============================
.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.NorthPolarStereo(), ccrs.PlateCarree()
    geom = sgeom.Point(0, 0).buffer(10000000).symmetric_difference(sgeom.Point(0, 0).buffer(5000000))
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()


Point in NPS -> Line in PC (currently fails)
============================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.NorthPolarStereo(), ccrs.PlateCarree()
    geom = sgeom.Point(0, 0)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, color='blue', alpha=0.8, linewidth=50)
    
    plt.show()


Band PC -> Two polys in Tmerc (fails currently)
===============================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(central_longitude=180), ccrs.TransverseMercator()
    geom = sgeom.box(-90, -40, 90, 40)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()

    
Circle in NPS => Circle in Tmerc (fails)
========================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.NorthPolarStereo(), ccrs.TransverseMercator()
    geom = sgeom.Point(0, 0).buffer(10000000)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()


Circle in NPS => Doughnut in SPS
================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.NorthPolarStereo(), ccrs.SouthPolarStereo()
    geom = sgeom.Point(0, 0).buffer(10000000)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()    


Circle in NPS => Top fill Rob
=============================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.NorthPolarStereo(), ccrs.Robinson()
    geom = sgeom.Point(0, 0).buffer(10000000)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()
    
    
Circle in SPS => Bottom fill Rob
================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.SouthPolarStereo(), ccrs.Robinson()
    geom = sgeom.Point(0, 0).buffer(10000000)
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()
    
Filled PC => Filled Rob
=======================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(), ccrs.Robinson()
    geom = sgeom.box(-180, -90, 180, 90).symmetric_difference(sgeom.box(-90, -40, 90, 40))
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()  


Double poly PC => Double poly NPS
=================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(), ccrs.NorthPolarStereo()
    geom = sgeom.MultiPolygon([sgeom.box(-90, 50, -10, 90),
                               sgeom.box(90, 50, 170, 90)])
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()

    
Doughnut PC => Open Doughnut in Orthographic
=============================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(central_longitude=-20), ccrs.Orthographic()
    geom = sgeom.box(-100, -70, 70, 40).symmetric_difference(sgeom.box(-80, -50, 50, 20))
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show() 

    
Doughnut PC => Double Doughnut in Orthographic (fails currently)
=================================================================

.. plot::

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely.geometry as sgeom
    
    
    LHS, RHS = ccrs.PlateCarree(), ccrs.Orthographic()
    geom = sgeom.box(-175, -70, 140, 70).symmetric_difference(sgeom.box(-150, -50, 110, 50))
    
    
    fig = plt.figure(figsize=(7, 2))
    
    ax1 = plt.subplot(1, 2, 1, projection=LHS)
    ax2 = plt.subplot(1, 2, 2, projection=RHS)
    
    ax1.coastlines(color='gray', alpha=0.4)
    ax2.coastlines(color='gray', alpha=0.4)
    
    ax1.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    ax2.add_geometries([geom], LHS, facecolor='blue', alpha=0.8)
    
    plt.show()     