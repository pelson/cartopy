import _clipper


def main():
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    
    
    path = Path([[0, 0], [1, 1], [1, -1], [-1, 1.1], [-1, -1]])
    
    print _clipper.simplify_mpl_vertices(path.vertices)
    
    
    
    
    
    #ax = plt.gca()
    #ax.add_patch(PathPatch(path),)
    #plt.show()