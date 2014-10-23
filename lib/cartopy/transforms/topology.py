"""
Algorithm for arbitrary geometry/path transformation from CRS to CRS.

 - Identify topology of source data to spherical
 - Identify topology of target CRS from spherical
 - Convert source geometry to pseudo-spherical
 - Convert pseudo-spherical geometry to pseudo-target geometry (preserving the undefined edges)
 - Apply interpolation to the pseudo-target geometry to form real geometries at arbitrary precision.

"""


class ProjectedLineString(list):
    def __repr__(self):
        r = super(ProjectedLineString, self).__repr__()
        return 'PLS({})'.format(r)

class ProjectedPoint(list):
    def __repr__(self):
        r = super(ProjectedPoint, self).__repr__()
        return 'NativeP({})'.format(r)


class TopologyTransformation(object):
    def forward(self, p0, p1self_coordinates_to_p0p1_fn, p0p1_cs_intersection_fn):
        """
        Takes the segment to the manifold that this
        transformation represents.

        Let any follow-up function deal with whether the cut is on the
        "right side" of the projected cs.

        """
        raise NotImplementedError()

    def prep(self, self_coordinates_to_p0p1_fn):
        return None

    def cut_spherical(self, segments, f1, f2):
        ring = [segments[0]]
        rings = [ring]
        prep = self.prep(f1)
        for i in range(len(segments) - 1):
            p0, p1 = segments[i], segments[i + 1]
            r = self.forward(prep, p0, p1, f1, f2)
            if len(r) == 1:
                ring.extend(r[0])
            elif len(r) == 2:
                # Cut, and start a new segment.
                ring.extend(r[0])
                ring = list(r[1])
                rings.append(ring)
            elif len(r) == 3:
                # Cut, insert a segment, and start a new one.
                # XXX The middle-segment should be in the coordinate system of this topology.
                ring.extend(r[0])
                ring = r[2]
                rings.extend([r[1], ring])
        return rings

    def cut_multisegments(self, msegments, f1, f2):
        result = []
        for segments in msegments:
            print 'Cutting ', segments
            if isinstance(segments, ProjectedLineString):
                result.append(segments)
                print 'Skipping', segments
            else:
                r = self.cut_spherical(segments, f1, f2)
                print 'R;', r
                result.extend(r)
            print
        return result


class PointToLine(TopologyTransformation):
    def __init__(self, p0, line):
        self.p0 = ProjectedPoint(p0)
        self.line = ProjectedLineString(line)

    def prep(self, self_coordinates_to_p0p1_fn):
        return self_coordinates_to_p0p1_fn(*self.p0)

    def forward(self, prep_result, p0, p1, self_coordinates_to_p0p1_fn, p0p1_cs_intersection_fn):
        point_in_target = prep_result
        intersects = p0p1_cs_intersection_fn(p0, p1, point_in_target)
        if intersects:
            return [[self.p0], self.line, [self.p0, p1]]
        else:
            return [[p1]]


class Antimeridian(TopologyTransformation):
#    def __init__(self):
#        self.plus_minus = 1e-8

    def prep(self, self_coordinates_to_p0p1_fn):
        """
        Return the antimeridian in the target coordinate system.

        """
        eps = 1e-13
        nearly_polar = -180 + eps, 180 - eps

        am_in_ll = [[-nearly_polar[0], -nearly_polar[1]],
                    [-nearly_polar[0], 0],
                    [-nearly_polar[0], nearly_polar[1]]]
        return [self_coordinates_to_p0p1_fn(*vert) for vert in am_in_ll]

    def forward(self, prep, p0, p1, self_coordinates_to_p0p1_fn, p0p1_cs_intersection_fn):
        am_vertices = prep
        n = len(am_vertices)

        # At no point do we insert p0. That is done for us.
        ring = []
        result = [ring]
        for i in range(n - 1):
            am0, am1 = am_vertices[i], am_vertices[i + 1]
            intersect = p0p1_cs_intersection_fn(p0, p1, am0, am1,
                                                inclusive_lh=False)

            if intersect is not None:
                ring.append(intersect)
                ring = [intersect, p1]
                result.append(ring)
                break
        if not ring:
            ring.append(p1)
        return result

#    
#    def inverse(self, p0, p1):
#        # TODO: Use a spherical (i.e. great circle) intersection algorithm.
#        import numpy as np
#        # dtype to deal with a shapely bug.
#        c = np.array([p0, p1], dtype=float)
#        ls = sgeom.LineString(c)
#        rline = sgeom.LineString(self.replacement_line)
#        if rline.intersects(ls):
#            intersection = ls.intersection(rline)
#            if isinstance(intersection, sgeom.Point):
#                raise NotImplementedError()
#            elif isinstance(intersection, sgeom.LineString):
#                # XXX TODO: verify that the segment is a subset of the cut line.
#                return ['PLACEHOLDER']
#        else:
#            return None


def simple_spherical_cases():
    from nose.tools import assert_equal

    def to_list(rings):
        return [map(list, ring) for ring in rings]

    am = Antimeridian()

    from cartopy.transforms.great_circle_intersection import intersect, gc_intersect_point

    from cartopy.transforms.euler_angles import UM_rotated_pole_inverse, UM_rotated_pole
    rot_to_ll = UM_rotated_pole_inverse(-180, 60)

    segments = [[-180, 45], [-180, 85]]
    r = am.cut_spherical(segments, rot_to_ll, intersect)
    assert_equal(r, [[[-180, 45], [-180, 85]]])

    segments = [[-170, 45], [170, 45]]
    r = am.cut_spherical(segments, rot_to_ll, intersect)
    assert_equal(to_list(r), [[[-170, 45], [-177.11473115547395, 45.402213450089143]],
                              [[-177.11473115547395, 45.402213450089143], [170, 45]]])


    # Single point intersection.
    # The new line is in the target coordinate system. And the original
    # coordinate is also in that cs. 
    npole = PointToLine([0, 90], [[-180, 90], [180, 90]])
    segments = [[-170, 40], [170, 60]]
    r = npole.cut_spherical(segments, rot_to_ll, gc_intersect_point)
    assert_equal(to_list(r), [[[-170, 40], [170, 60]]])

    rot_to_ll = UM_rotated_pole_inverse(-180, 0)

    npole = PointToLine([0, 90], [[-180, 90], [180, 90]])
    segments = [[180, 0], [40, 40]]
    r = npole.cut_spherical(segments, rot_to_ll, gc_intersect_point)
    assert_equal(to_list(r), [[[180, 0], [180, 7.016709298534876e-15]],
                              [[-180, 90], [180, 90]],
                              [[180.0, 7.016709298534876e-15], [40, 40]]])


def show_rp_cutting():
    from cartopy.transforms.great_circle_intersection import intersect, gc_intersect_point
    from cartopy.transforms.euler_angles import UM_rotated_pole, UM_rotated_pole_inverse
    ll_to_rot = UM_rotated_pole(-180, 60)
    rot_to_ll = UM_rotated_pole_inverse(-180, 60)

    import numpy as np
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    ax = plt.subplot(2, 1, 1, projection=ccrs.PlateCarree())
    rp = ccrs.RotatedPole(-180, 30)
    rgeod = ccrs.RotatedGeodetic(-180, 30)
    geod = ccrs.Geodetic()
    ax2 = plt.subplot(2, 1, 2, projection=rp)

    npole = PointToLine([0, 90], [[-180, 90], [180, 90]])
    am = Antimeridian()
    segments = [[-180, -90], [-180, 0], [-180, 90]]
    segments_result = am.cut_spherical(segments, ll_to_rot, intersect)

    segments_result = npole.cut_multisegments(segments_result, rot_to_ll, gc_intersect_point)

    def project_segments(msegments, source, target):
        result = []
        for segments in segments_result:
            if isinstance(segments, ProjectedLineString):
                result.append(segments)
            else:
                new_segments = [target.transform_point(point[0], point[1], source)
                                if not isinstance(point, ProjectedPoint) else
                                point
                                for point in segments]
                result.append(new_segments)
        return result

    r = project_segments(segments_result, geod, rgeod)

    for segments in r:
        x, y = np.array(segments).T
        x1, y1, _ = ax.projection.transform_points(rp, x, y).T
        ax.plot(x1, y1, 'ob-', lw=4, alpha=0.5)
        x1, y1, _ = ax2.projection.transform_points(rp, x, y).T
        ax2.plot(x1, y1, 'ob-', lw=4, alpha=0.5)
    ax.coastlines()
    ax.gridlines(rp)
    ax.set_global()

    ax2.set_global()
    ax2.coastlines()
    ax2.gridlines()

    plt.show()


if __name__ == '__main__':
#    simple_spherical_cases()
    show_rp_cutting()

#    r = move_spherical_segment([[170, 60], [180, 60]])
#    r = move_spherical_segment([[180, 60], [-170, 60]])