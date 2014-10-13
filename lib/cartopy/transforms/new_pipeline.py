# from . import topology
import shapely

print shapely
import cartopy.transforms.topology as topology


def geom_apply_topology(segments, topo):
    ring = [segments[0]]
    rings = [ring]
    for p0, p1 in zip(segments[:-1], segments[1:]):
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
    return rings


if __name__ == '__main__':
    topo = [topology.CutLine([[180, -90], [180, 90]])]
    
    print geom_apply_topology([[0, 10], [170, 20], [190, 10], [150, 40]],
                              topo)