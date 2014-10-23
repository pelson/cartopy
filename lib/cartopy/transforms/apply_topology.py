import shapely

print shapely
import cartopy.transforms.topology as topology


def geom_apply_topology(segments, topo, closed=False):
    ring = []
    rings = [ring]
#    for p0, p1 in zip(segments[:-1], segments[1:]):
    n = len(segments)
    for i in range(-1, n -  (not closed)):
        print i % n, (i+ 1) % n, n
        p0, p1 = segments[i % n], segments[(i + 1) % n]
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
        print 'Closing'
        # XXX Have I just broken the ordering?
        rings[-1].extend(rings.pop(0))

    return rings



class SphericalTopologyGeometry(object):
    def __init__(self, geometry, xy_to_spherical):
        """
        Parameters
        ==========
        geometry 
            the spherical geometry
        xy_to_spherical
            a fn, called with ``fn(x, y)`` to return the longitude and latitude
            of a point in the CS of the geometry. 
        vertex_intersection_fn
            a fn, called with ``fn(s0, s1, i0, i1)`` in spherical coordinates which
            computes the intersection point
        """
        pass

    @classmethod
    def from_geometry(crs, geometry, source_crs):
        spherical_geometry = []
        # Remove edge points and sort out the winding number.
#        spherical_geometry = remove_edge()
        # Join together points which lie on the antimeridian.
#        spherical_geometry = rejoin.join()
        return crs(spherical_geometry, source_crs.as_geodetic().transform_point)

    def to_target_geomerty(self, target_crs, vertex_interp_fn, antimeridian_vertex_intersect_fn):
        # XXX We pass a target_crs through as it has topology.
        xy_to_target_fn = target_crs.transform_point

        result = []
        # Cut at vertices which cross the antimeridian.
#        result = ... do the cutting
        # Merge the cuts together.
#        result = rejoin.rejoin(result)

        from cartopy.transforms.geom_interpolate import TargetGeometry
        return TargetGeometry(result, xy_to_target_fn, vertex_interp_fn)




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
    