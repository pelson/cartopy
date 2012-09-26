import matplotlib.pyplot as plt
from matplotlib.pyplot import xticks

import numpy




def add_ticks(path, source_transform, target_transform):

    line_to_desired = source_transform - target_transform

    coords = path.interpolated(150).vertices

    transformed = line_to_desired.transform(coords)
#    plt.plot(transformed[:, 0], transformed[:, 1], 'ro')

    import matplotlib.ticker as mticker
    ticker = mticker.MaxNLocator(5)
    # option to do regularly spaced ticks on the line instead.
    xticks = ticker.tick_values(transformed[..., 0].min(), transformed[..., 0].max())
    yticks = ticker.tick_values(transformed[..., 1].min(), transformed[..., 1].max())


    rng = transformed[..., 1].min(), transformed[..., 1].max()

    print xticks
    print yticks

    for tick in yticks:
        if not (rng[0] <= tick <= rng[1]):
            continue
#        print numpy.array([[0, 1]]) * tick
        step = transformed - numpy.array([[0, tick]])
        gt_0 = step[..., 1] >= 0
        sign_change = numpy.roll(gt_0, 1) - gt_0
        sign_change[0] = 0

        for mark in numpy.where(sign_change)[0]:
            print 'mark:', mark, tick
            plt.plot(transformed[mark, 0], transformed[mark, 1], 'bo', transform=target_transform)
            plt.text(transformed[mark, 0], transformed[mark, 1], '%s' % tick, transform=target_transform)

#        print sign_change
#        print transformed[..., 1].min(), transformed[..., 1].max()
#        print tick
#        print transformed
#        print step
#        break




if __name__ == '__main__':
    
    # NOT ME. YOU SHOULD DELME....
    
    ax = plt.axes(projection='polar')
    ax = plt.gca()
    r = plt.plot(range(10), range(10))

    add_ticks(r[0].get_path(), r[0].get_transform(), ax.transData)

#    r = plt.plot([0.25, 0.75], [0.3, 0.6], transform=ax.transAxes)
#    line = r[0]


    import matplotlib.path as mpath
    import matplotlib.patches as mpatches

#    path = mpath.Path(zip([0.15, 0.275, 0.7], [0.3, 0.35, 0.8]))
#    patch = mpatches.PathPatch(path, transform=ax.transAxes, facecolor='none')
#    ax.add_patch(patch)
#
#    add_ticks(patch.get_path(), patch.get_transform(), ax.transData)


#    print line_to_desired.transform(coords)


    plt.draw()
    plt.show()