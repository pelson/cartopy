# from . import topology
import shapely

print shapely
import cartopy.transforms.topology as topology


def geom_apply_topology(segments, topo, closed=False):
    ring = [segments[0]]
    rings = [ring]
#    for p0, p1 in zip(segments[:-1], segments[1:]):
    n = len(segments)
    for i in range(-1, n + closed - 1):
        p0, p1 = segments[i], segments[(i + 1) % n]
        result = topology.handle_segment(p0, p1, topo)
        if result is None:
            ring.append(p1)
        elif len(result) > 1:
            # Add all but the first item in the first returned segment.
            ring.extend(result[0][1:])
            # Unless a topology handler returns more than 2 segments
            # this for loop will never trigger... maybe delete.
            for new_section in result[1:-1]:
                rings.append(new_section)
            ring = result[-1]
            rings.append(ring)
        else:
            raise ValueError('Some topos should be able to return'
                             ' a single value...')
    if closed and rings[0][0] == rings[-1][-1]:
        # XXX Have I just broken the ordering?
        rings[-1].extend(rings.pop(0))
    
    return rings





if __name__ == '__main__':
    topo = [topology.CutLine([[180, -90], [180, 90]])]
    
    print geom_apply_topology([[0, 10], [170, 20], [190, 10], [150, 40]],
                              topo)
    
    topo = [topology.CutLine([[0, -90], [0, 90]])]
    segments = [(-50, 20), (50, 20), (50, -20), (50, -20)]
    geoms = geom_apply_topology(segments, topo, closed=True)
    
    from cartopy.transforms.rejoin import draw_polys
    print geoms
    draw_polys(geoms) 
    