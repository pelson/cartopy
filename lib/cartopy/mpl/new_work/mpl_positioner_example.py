from __future__ import division

import numpy as np
import matplotlib.pyplot as plt

from positioner import where_on_line

ax = plt.axes()

x = np.linspace(0, np.pi * 2, 1000)
line, = plt.plot(np.sin(x ** 1.6) * x)

xa, ya = where_on_line(line, x=0.75, xy_trans=ax.transAxes)
x, y = (ax.transAxes - ax.transData).transform_point([xa, ya])
plt.plot(x, y, 'ob')
plt.axvline(x, linestyle=':')

plt.show()
