import cartopy.transforms.topology
import cartopy.transforms.great_circle_intersection as geodesy


# If cartesian, transform the antimeridian to projected space (That makes sense, right?!)
# If spherical, 


def cut_antimeridian_crossing_ring(ring, xy_to_projected, xy_intersect_fn):
#     import cartopy.transforms.great_circle_intersection
    n = len(ring)
    counter = iter(range(n))
    i, p0 = 0, Ellipsis
    while p0 is Ellipsis:
        i -= 1
        p0 = ring[i]

    for p1 in ring:
        if p1 is Ellipsis:
            print 'BAA'
#             intersection_fn = spherical_intersects
        else:
            xy_intersect_fn(p0, p1)
            
            intersection_fn = xy_intersect_fn
            p0 = p1


class Topology(object):
    pass



class Antimeridian(object):
    def forward(self, vertices):
        """Cut the given spherical vertices based on whether they cross the antimeridian."""
        n = len(vertices)
        
        ring = [vertices[0]]
        result = [ring]
        counter = iter(range(n - 1))
        for i in counter:
            p0, p1 = vertices[i], vertices[i + 1]
            
            intersect = geodesy.intersect(p0, p1, [-180, -90], [-180, 0])
            if intersect is None:
                intersect = geodesy.intersect(p0, p1, [-180, 0], [-180, 90])
            if intersect is not None:
                # XXX Assert that the intersection point is one of the actual points?
                import numpy as np
                if np.all(np.array(p1) == np.array(intersect)):
                    continue
                ring.append(intersect)
                ring = [intersect, p1]
#                 next(counter, None)
                result.append(ring)
            else:
                ring.append(p1)
        return result


if __name__ == '__main__':
    # AIM: To convert a antimeridian line (in a spherical topolgy and with spherical interpolation) to PlateCarree and/or Robinson
#     print cut_spherical([[-180, -90], [-180, 0], [-180, 90]], topology)
    print Antimeridian().forward([(-160, 20), (-180, 10), (160, 20)])
    print Antimeridian().forward([(-180, 10), (160, 20)])
    print Antimeridian().forward([(180, 10), (-160, 20)])
    
    # AIM: To convert a spherical line to PlateCarree and/or Robinson, but the coordinates and interpolation is cartesian.
    exit()
    def rotate(degrees):
        def fn(x, y):
            return ((x + degrees) + 360) % 360 - 180
    
    # A simple ring containing the south pole.
    segments = [(-180, 30), (180, 30), Ellipsis]
    print cut_antimeridian_crossing_ring(segments, None, rotate(0))
    
    
    
    