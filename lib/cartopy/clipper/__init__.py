import _clipper
from _clipper import simplify_mpl_path


def main():
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    
    
    path = Path([[0, 0], [1, 1], [1, -1], [-1, 1.1], [-1, -1]])
    
    path = Path([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0], [0.5, 0.5], [1.5, 1], [3, 0.5], [1.5, 0]],
                codes=[1, 2, 2, 2, 2, 1, 2, 2, 2])
    
    path = path.cleaned(remove_nans=True, simplify=True, curves=False)

    vertices = _clipper.simplify_mpl_path(path, scale_factor=10**7)
    print vertices
    
    ax = plt.gca()
    for i, geom in enumerate(vertices):
        ax.add_patch(PathPatch(Path(geom), alpha=0.5))
    
    plt.xlim(-0.5, 4.5)
    plt.ylim(-0.5, 1.5)
    
    plt.show()
    

if __name__ == '__main__':
    main()
