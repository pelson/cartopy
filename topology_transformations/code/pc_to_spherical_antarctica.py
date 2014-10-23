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

ax1 = plt.subplot(1, 2, 1)
ax1.add_patch(mpatches.PathPatch(path, facecolor='gray',
                                 alpha=0.8, edgecolor='black'))

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


ax2 = plt.subplot(1, 2, 2, sharex=ax1, sharey=ax1)

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

for ring in rings:
    # Remove the link backs for now.
    ring = [vert for vert in ring if vert is not Ellipsis]
    ring = np.array(ring)
    x, y = zip(*ring)
    ax2.plot(x, y, lw=3, color='gray', alpha=0.8)


from matplotlib.ticker import MaxNLocator

ax1.xaxis.set_major_locator(MaxNLocator(4))
ax1.yaxis.set_major_locator(MaxNLocator(4))

ax1.margins(0.1)
ax1.autoscale_view(tight=True)
fig.subplots_adjust(left=0.1, right=0.95, bottom=0.2)


ax2.annotate("",
            xytext=(180, -85), xycoords='data',
            xy=(20, -90), textcoords='data',
            arrowprops=dict(arrowstyle="simple",
                            color="black",
                            connectionstyle="arc3,rad=-0.15",
                            ),
             va='top', ha='center',
            )
ax2.annotate("",
            xy=(-180, -85), xycoords='data',
            xytext=(-20, -90), textcoords='data',
            va='top', ha='center',
            arrowprops=dict(
                            arrowstyle="simple",
                            color="black",
                            connectionstyle="arc3,rad=-0.15",
                            ),
            )
ax2.text(0, -89.5, 'Join', ha='center', va='top')

# plt.gcf().canvas._master.geometry('336x852+952+22')
plt.show()