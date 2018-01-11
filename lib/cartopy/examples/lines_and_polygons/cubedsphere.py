"""
(X,Y,Z) are the global Cartesian coordinates

To construct the cubed-sphere we assume the sphere sits inside the cube (rather than cube inside the sphere).
x,y denote the coordinates on a face of a cube with -R<x,y<R where (R is the radius of the sphere - I don't believe this bit)
The distance to a face is denoted by r.

alpha,beta are the angles such that x=R tan(alpha), y=R tan(beta)

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cartopy.crs as ccrs
import cartopy.feature


def geocentric_to_ll(X, Y, Z):
  """
  Transforms Cartesian (X,Y,Z) position to llr (lon,lat,radius) with latitude in range -pi/2 and pi/2

  """
  radius = np.sqrt(X**2 + Y**2 + Z**2)
  lat = np.arcsin(Z / radius) 
  lon = np.mod(np.arctan2(Y, X), 2*np.pi)
  return np.array([lon, lat])


def alphabeta_to_ll(alpha,beta):
  """(alpha,beta) maps to lon,lat"""  
  x = np.tan(alpha)
  y = np.tan(beta)
  r = np.sqrt(1 + x**2 + y**2)
  [X, Y, Z] = geocubic_to_geocentric(x, y) 
  lon, lat = geocentric_to_ll(X,Y,Z)
  return lon, lat


def geocubic_to_geocentric(x, y):
    r = np.sqrt(1 + x**2 + y**2)
    return np.array([1/r, x/r, y/r])


def main():
    resolution = 20
    figsize=(5, 5)
    plt.figure(figsize=figsize)
    ax1 = plt.axes(projection=ccrs.Orthographic(0, 60))
    #ax1.add_feature(cartopy.feature.OCEAN, zorder=0)
    #ax1.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')
    ax1.set_global()

    plt.figure(figsize=figsize)
    ax2= plt.axes(projection=ccrs.Orthographic(180, 40))
    ax2= plt.axes(projection=ccrs.PlateCarree())

    #ax2.add_feature(cartopy.feature.OCEAN, zorder=0)
    #ax2.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')
    ax2.set_global()

    equi_ang_points = np.linspace(-np.pi/4.,np.pi/4,resolution)

    R, n = 1, resolution
    #n = 2
    a_r = np.pi/4
    xs, ys = np.meshgrid(np.linspace(-a_r, a_r, n), np.linspace(-a_r, a_r, n))
    r = alphabeta_to_ll(xs, ys)
    r = np.array(r)
    print(r[0, 0])
    degrees_lon = np.rad2deg(np.unwrap(r[0],discont=np.pi))
    print(degrees_lon[0])
    degrees_lat = np.rad2deg(np.unwrap(r[1],discont=np.pi))

    degrees_lon -= 180

    for ax in [ax1, ax2]:
        kwargs = {'edgecolor': 'gray', 'antialiased': False}
        kwargs = {'antialiased': False, 'facecolor': 'none', 'edgecolor': 'gray', 'alpha': 0.2, 'linewidth': 0.2, 'antialiased': True}
        ax.pcolormesh(degrees_lon, degrees_lat, degrees_lat * degrees_lon, transform=ccrs.PlateCarree(), **kwargs)
        ax.pcolormesh(degrees_lon, degrees_lat, degrees_lat * degrees_lon, transform=ccrs.PlateCarree(central_longitude=180), **kwargs)
        ax.pcolormesh(degrees_lon, degrees_lat, degrees_lat * degrees_lon, transform=ccrs.RotatedPole(pole_latitude=0), **kwargs)
        ax.pcolormesh(degrees_lon, degrees_lat, degrees_lat * degrees_lon, transform=ccrs.PlateCarree(central_longitude=90), **kwargs)
        ax.pcolormesh(degrees_lon, degrees_lat, degrees_lat * degrees_lon, transform=ccrs.PlateCarree(central_longitude=270), **kwargs)
        ax.pcolormesh(degrees_lon, degrees_lat, degrees_lat * degrees_lon, transform=ccrs.RotatedPole(pole_latitude=-180, pole_longitude=0), **kwargs)

    plt.show()


if __name__ == '__main__':
    main()
