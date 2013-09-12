import cartopy.mpl.qgis as q
reload(q)

from cartopy.mpl.qgis import new_layer, new_layer_non_interactive



def run_script(app):
    drawer, ax = new_layer_non_interactive(layer_name='Iris layer')

    import iris
    import iris.plot as iplt
    
    cube = iris.load_cube('/home/user/rotated_pole.nc')
    iplt.pcolormesh(cube)
    
    drawer()





def run_script_interactive(app):
#     fname = '/tmp/20130912_1002490ZId64/20130912_100249.png'
#     from cartopy.mpl.qgis import add_layer
#     layer = add_layer(fname)
#     return
    import os
    
    import datetime
    dt = datetime.datetime.now()
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix=dt.strftime("%Y%m%d_%H%M%S"))
    
    ax = new_layer(tmp_dir)
    ax.coastlines(linewidth=2)
    ax.stock_img()
    
    import matplotlib.pyplot as plt
    fig = plt.gcf()
    plt.savefig(fig._qgis_fname, transparent=True, dpi=fig.dpi)
#     import iris
#     fname = iris.sample_data_path('rotated_pole.nc')
#     cube = iris.load_cube(fname)
#     import iris.plot as iplt
#     iplt.contourf(cube)
