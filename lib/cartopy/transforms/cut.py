import cartopy.transforms.topology
import cartopy.transforms.great_circle_intersection as geodesy
import numpy as np

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


from pc_to_spherical import spherical_equal
def wrap_lon(lon):
    return (lon + 360 * 10 + 180) % 360 - 180

def lon_equal(lon0, lon1):
    return (lon0 + 720) % 360 == (lon1 + 720) % 360

class Antimeridian(object):
    def cut_spherical(self, vertices, epsilon=1):
        """
        Cut the given spherical vertices based on whether they cross the antimeridian.

        Remember, this is testing great circle intersections so both sides of
        an intersection point will have the same coordinate (i.e. no epsilon or +-360 etc).
        Is this useful though? We still need to worry about the coordinate value for now. So add and subtract the epsilon.

        """
        vertices = np.array(vertices)
        n = len(vertices)

        ring = [vertices[0]]
        result = [ring]
        for i in range(n - 1):
            p0, p1 = vertices[i], vertices[i + 1]

            # This is a great circle, so we can wrap the longitudes without issue.
#            if not -180 <= p0[0] < 180:
#                p0[0] = wrap_lon(p0[0])
#            if not -180 <= p1[0] < 180:
#                p1[0] = wrap_lon(p1[0])

            p1_on_antimeridian = p1[0] == -180
            p0_on_antimeridian = p0[0] == -180

#            if np.abs(p0[0] - p1[0]) > 180:
#                print 'GREATER'
#                p0[0] = wrap_lon(p0[0] + 360)
            

#            if p0_on_antimeridian and p1_on_antimeridian:
#                ring.append(p1)
#            elif p1_on_antimeridian:
#                continue
#            elif p0_on_antimeridian:
#                ring.append(p1)
#                continue

            intersect = geodesy.intersect(p0, p1, [-180, -90], [-180, 0])
            if intersect is None:
                intersect = geodesy.intersect(p0, p1, [-180, 0], [-180, 90])

            if intersect is not None:
#                intersect[0] = wrap_lon(intersect[0])
#                print 'I:', intersect, p0, intersect, spherical_equal(p0, intersect), `p0[1]`, `intersect[1]`
                # XXX Assert that the intersection point is one of the actual points?
#                if p1[0] == intersect[0]:
#                    continue

                if lon_equal(intersect[0], p0[0]):
#                    ring.pop(-1)
                    # Preserve the latitude exactly.
#                    ring.append([intersect[0], p0[1]])
#                    print 'P0 & Intersect lon equal', p1
                    ring.append(p1)
                else:
                    delta = epsilon
                    if p0[0] > p1[0]:
                        delta = -epsilon
                    # NOTE: We don't need to add an epsilon here - we are talking about great circles.

                    ring.append(intersect - [delta, 0])
                    if lon_equal(p1[0], intersect[0]):
                        # Preserve the latitude exactly.
                        ring = [[p1[0] + delta, p1[1]]]
#                        print 'P1 & Intersect lon equal', ring[0]
                    else:
                        ring = [intersect + [delta, 0], p1]
                    result.append(ring)
            else:
                ring.append(p1)
        return result


def test_Antimeridian_cut_spherical():
    def to_list(rings):
        return [map(list, ring) for ring in rings]
    from nose.tools import assert_equal

    r = Antimeridian().cut_spherical([(-160, 20), (-180, 10), (160, 20)], epsilon=0.5)
    expected = [[[-160, 20], [-179.5, 10.]], [[-180.5, 10], [160, 20]]]
    assert_equal(expected, to_list(r))

#    r = Antimeridian().cut_spherical([(-180, 10), (160, 20)], epsilon=0.5) # Should only produce one segment...
#    expected = [[[180, 10], [160, 20]]]
#    assert_equal(expected, to_list(r))

#    r = Antimeridian().cut_spherical([(180, 10), (-160, 20)], epsilon=0.5) # Should only produce one segment...
#    expected = [[[-180, 10], [-160, 20]]]
#    assert_equal(expected, to_list(r))

    r = Antimeridian().cut_spherical([(180, -90), (180, 0)], epsilon=0.5)
    expected = [[[180, -90], [180, 0]]]
    assert_equal(expected, to_list(r))


if __name__ == '__main__':
    # AIM: To convert a antimeridian line (in a spherical topolgy and with spherical interpolation) to PlateCarree and/or Robinson

    # NOW cut the antimeridian from target to the topology of source (e.g. PC180 -> PC no result, but RP -> PC may result in two "antimeridian" lines)
    test_Antimeridian_cut_spherical()

    # let's use an example where the source is RP with the n pole at (180, 60) and the target is PC
    target_am = [(-180, -90), (-180, 0), (-180, 90)]
    target_am_unrotated = [vert - np.array([-180, 60]) for vert in target_am]
    print target_am_unrotated
    print Antimeridian().cut_spherical(target_am_unrotated)


    # NOW interpolate the antimeridian to a sufficient resolution in the source CS.


    # NOW Use the interpolated antimeridian to cut the source geometry (which has a spherical topology)

    # NOW Re-join the cut source geometry to the edges of the target

    # Now interpolate the result. 



    # AIM: To convert a spherical line to PlateCarree and/or Robinson, but the coordinates and interpolation is cartesian.
    exit()
    def rotate(degrees):
        def fn(x, y):
            return ((x + degrees) + 360) % 360 - 180

    # A simple ring containing the south pole.
    segments = [(-180, 30), (180, 30), Ellipsis]
    print cut_antimeridian_crossing_ring(segments, None, rotate(0))
