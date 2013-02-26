from __future__ import division

import numpy as np

#import matplotlib.lines as mlines
#import matplotlib.path as mpath
#import matplotlib.pyplot as plt

#ax = plt.axes()
#
#l = mlines.Line2D([0, 0, 2, 3, 3, 2], [10, 20, 30, 40, 50, 20], transform=ax.transData)
#
#ax.add_line(l)
#ax.set_ylim([0, 70])
#ax.set_xlim([-1, 4])
#
#
#p = l.get_path()


        

#xy = where_on_line(l, x=0.75, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, x=0.25, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, x=0.5, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, y=0.5, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
#
#xy = where_on_line(l, y=0.25, xy_trans=ax.transAxes)
#ax.plot(xy[0], xy[1], 'o', transform=ax.transAxes)


#print where_on_line(l, x=1, xy_trans=ax.transData)
#print where_on_line(l, x=0, xy_trans=ax.transData)
#print where_on_line(l, x=3, xy_trans=ax.transData)
#print where_on_line(l, x=5, xy_trans=ax.transData)
#print where_on_line(l, x=2.5, xy_trans=ax.transData)
#
#
#print where_on_line(l, y=0, xy_trans=ax.transData)
#print where_on_line(l, y=10, xy_trans=ax.transData)
#print where_on_line(l, y=25, xy_trans=ax.transData)
#print where_on_line(l, y=50, xy_trans=ax.transData)
#print where_on_line(l, y=55, xy_trans=ax.transData)


#
#import matplotlib.patches as mpatches
#import matplotlib.path as mpaths
#import matplotlib.lines as mlines
#import matplotlib.pyplot as plt
##
##ax = plt.axes()
##ax.set_xlim([5, 15])
##ax.set_ylim([-15, -5])
##p = mpatches.CirclePolygon([10, -10], 3, resolution=15, alpha=0.5, facecolor='coral')
##ax.add_patch(p)
##
##patch_line = mlines.Line2D([0], [0], transform=ax.transData)
##patch_path = p.get_path()
##patch_path = (p.get_transform() - ax.transData).transform_path(patch_path)
##condition = patch_path.vertices[:, 0] != np.nan
##patch_line.set_xdata(patch_path.vertices[condition, 0])
##patch_line.set_ydata(patch_path.vertices[condition, 1])
##ax.add_line(patch_line)
##
##
##print where_on_line(patch_line, x=10)
##
##print where_on_line(patch_line, y=-10)
##print where_on_line(patch_line, y=-7)
##
##
##
##line = mlines.Line2D([-12, -11, -10, -10, -10, -14], 
##                     [7, 8, 8, 7, 6, 9],
##                     transform=ax.transData)
##ax.add_line(line)
##
##
##print where_on_line(line, x=-10)
##
##
##
##line = mlines.Line2D([7, 8, 8, 6, 9], 
##                     [-12, -11, -10, -10, -14],
##                     transform=ax.transData)
##ax.add_line(line)
##
##
##print where_on_line(line, y=-10)
###plt.show()
##
##
#
#ax = plt.axes()
## make sensible limits for the axes
#ax.set_ylim([0, 70])
#ax.set_xlim([-1, 4])
#
#line = mlines.Line2D([0, 0, 2, 3, 3, 2], 
#                          [10, 20, 30, 40, 50, 20],
#                          transform=ax.transData) 
#ax.add_line(line)
#xy = where_on_line(line, y=0.25, xy_trans=ax.transAxes)
#print xy
#plt.plot(xy[0], xy[1], 'o', transform=ax.transAxes)
##
#plt.show()
