# import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import shapely.geometry as sgeom


def continent(name):
    import cartopy.io.shapereader as shpreader

    shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_0_countries')
    reader = shpreader.Reader(shpfilename)
    countries = reader.records()
    shapes = []
    for country in countries:
        if country.attributes['continent'] == name:
            shapes.append(country.geometry)
    
    from shapely.ops import cascaded_union
    geom = cascaded_union(shapes)
    return geom


import cartopy.mpl.patch as cpatch

# LHS, RHS = ccrs.PlateCarree(), ccrs.Orthographic(0, -45)

geom = continent('Antarctica')

import matplotlib.path as mpath
path = mpath.Path.make_compound_path(*cpatch.geos_to_path(geom))
import matplotlib.patches as mpatches
fig = plt.figure(figsize=(9, 4))


import matplotlib.patheffects as path_effects
effect = [path_effects.withStroke(linewidth=5, foreground='black')]


# ax1.add_patch(mpatches.PathPatch(path, facecolor='gray',
#                                  alpha=0.8, edgecolor='black'))

import numpy as np

# print path.vertices.shape
# for vertex in path.vertices:
#     print vertex, np.abs(np.abs(vertex[0]) - 180) < 0.4
#     


# bad = np.logical_or(close_to(path.vertices[:, 0], 180.0, 0.4),
#                     close_to(path.vertices[:, 1], 90.0, 0.4))
# 
# # print np.sum(bad), path.vertices[:, 0].max()# == 180.0
# # bad = bad | np.close(path.vertices[:, 1], -90.0)
# # print bad
# print bad.shape
# codes = path.codes[~bad]
# codes[codes == mpath.Path.CLOSEPOLY] = mpath.Path.MOVETO
# verts = path.vertices[~bad, :]
# # print path.vertices[:, 0].min()
# # print np.sum(bad)
# path = mpath.Path(verts, codes, closed=False)





ax1 = plt.subplot(1, 2, 1)

from cartopy.transforms.pc_to_spherical import pc_to_spherical


def close_to(arr, val, eps):
    r = np.abs(val - arr)
    return r < eps
# 
# # exit()
# # print path.vertices

xs = path.vertices[:, 0] 
ys = path.vertices[:, 1]

# Sadly the coordinate values don't equate exactly to 180 -
# they *print* that way though,
# so they are seriously close!
xs[close_to(xs, 180, 0.1)] = 180
xs[close_to(xs, -180, 0.1)] = -180
ys[close_to(ys, -90, 0.1)] = -90

segments = []

for v0, code in path.iter_segments():
    if code == mpath.Path.MOVETO:
        segment = [v0]
        segments.append(segment)
    else:
        segment.append(v0)

rings = pc_to_spherical(segments)


joins = []
for ring in rings:
    # Remove the link backs for now.
    new_ring = []
    n = len(ring)
    for i in range(n):
        vert = ring[i]
        if vert is not Ellipsis:
            new_ring.append(vert)
        else:
            joins.append([ring[i - 1], ring[(i + 1) % n]])
    ring = np.array(new_ring)
    x, y = zip(*ring)
    ax1.plot(x, y, lw=3, color='gray', alpha=0.8)


from matplotlib.ticker import MaxNLocator

ax1.xaxis.set_major_locator(MaxNLocator(4))
ax1.yaxis.set_major_locator(MaxNLocator(4))

fig.subplots_adjust(left=0.1, right=0.95, bottom=0.2)


ax1.text(0, -89.5, 'New antimeridian', ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='wheat'))

for join in joins:
    p0, p1 = sorted(tuple(point) for point in join)
    ax1.plot([p0[0], p0[0] - 40], [p0[1], p0[1]], lw=2, color='blue')
    ax1.plot([p1[0], p1[0] + 40], [p1[1], p1[1]], lw=2, color='blue')
    ax1.plot([p0[0], p1[0]], [p0[1], p1[1]], 'ob')

ax1.axvline(0, ls=':', color='black')

ax1.margins(0.1)
ax1.autoscale_view(tight=True)
ax1.set_ylim(bottom=-93)


ax2 = plt.subplot(1, 2, 2, sharex=ax1, sharey=ax1)


rings

# plt.gcf().canvas._master.geometry('336x852+952+22')
plt.show()