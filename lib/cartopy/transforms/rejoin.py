import numpy as np

class IntersectionPoint(object):
    def __init__(self, xy, prev_intersection=None, next_intersection=None,
                 is_entry=False, twinned_intersection=None, vertices=None,
                 visited=False):
        self.xy = xy
        self.prev_intersection = prev_intersection
        self.next_intersection = next_intersection
        self.is_entry = is_entry
        self.twinned_intersection = twinned_intersection
        self.vertices = vertices
        self.visited = False

        if twinned_intersection is not None:
            # Link up the two intersections.
            twinned_intersection.twinned_intersection = self

    def __repr__(self):
        def t_or_f(boolean):
            return 'T' if boolean else 'F'
        return '<IP: {}; entry: {}; subject: {}>'.format(self.xy, t_or_f(self.is_entry),
                                                         t_or_f(self.vertices is not None))

    def set_next_intersection(self, next_intersection):
        # Update the linked-list.
        self.next_intersection = next_intersection
        next_intersection.prev_intersection = self


class Cutter(object):
    def __init__(self, polygon, sort_fn):
        self.polygon = polygon
        self.sort_fn = sort_fn

    def attach_segments(self, segments, clip_starts_inside_polygon, interpolation_fn):
        # Phase 1. Get the intersection (i.e. edge) points in two
        # doubly linked lists.
        subject, clip, rings = self.classify_end_points(segments)

        # Phase 2. Sort the intersection points and link them
        # together into a doubly linked list. Alternate the
        # clip intersection entry/exit flag.
        self.sort_and_link(subject, clip, clip_starts_inside_polygon)

        # Phase 3. Construct the resulting geometries.
        polys = self.join_intersections(subject, clip, interpolation_fn)

        return polys + rings

    def sort_and_link(self, subject, clip, clip_starts_inside_polygon):
        # Update the lists **in place**.
        subject.sort(key=self.sort_fn)
        clip.sort(key=self.sort_fn)
        prev = subject[-1]
        for next_intersection in subject:
            prev.set_next_intersection(next_intersection)
            prev = next_intersection

        prev = clip[-1]
        is_entry = clip_starts_inside_polygon
        for next_intersection in clip:
            prev.set_next_intersection(next_intersection)
            next_intersection.is_entry = is_entry = not is_entry
            prev = next_intersection

    def join_intersections(self, subject, clip, interpolation_fn):
        polygons = []
        start = subject[0]
        while True:
            current = start
            is_subject = True
            while current.visited:
                current = current.next_intersection
                if current is start:
                    return polygons

            points = current.vertices
            poly = []
            current_visited = False
            while not current_visited:
                current.visited = current.twinned_intersection.visited = True
                if current.is_entry:
                    if is_subject:
                        poly.extend(points)
                    else:
                        poly.extend(interpolation_fn(current.xy, current.next_intersection.xy, direction=1))
                    current = current.next_intersection
                else:
                    if is_subject:
                        points = current.prev_intersection.vertices
                        poly.extend(points[::-1])
                    else:
                        print 'back interpolate'
                        poly.extend(interpolation_fn(current.xy, current.prev_intersection.xy, direction=-1))
                    current = current.prev_intersection
                current = current.twinned_intersection
                points = current.vertices
                is_subject = not is_subject
                current_visited = current.visited
            if np.all(poly[0] != poly[-1]):
                poly.append(poly[0])
            polygons.append(poly)

    def classify_end_points(self, segments):
        subject = []
        clip = []
        rings = []
        for segment in segments:
            # Remove the geometries which are not clipped.
            if np.all(segment[0] == segment[-1]):
                rings.append(segment)
                continue

            i_0 = IntersectionPoint(segment[0], is_entry=True, vertices=segment)
            i_0_twin = IntersectionPoint(segment[0], is_entry=False,
                                         twinned_intersection=i_0)

            i_n = IntersectionPoint(segment[-1], is_entry=False, vertices=segment)
            i_n_twin = IntersectionPoint(segment[-1], is_entry=True,
                                         twinned_intersection=i_n)

            subject.extend([i_0, i_n])
            clip.extend([i_0_twin, i_n_twin])

        return subject, clip, rings


def interpolate_spherical_edge(p0=None, p1=None, direction=1):
    pi = 180
    if p0 is None:
        phi = direction * 90
        r = [[-pi, phi],
             [0, phi],
             [pi, phi],
             [pi, 0],
             [pi, -phi],
             [0, -phi],
             [-pi, -phi],
             [-pi, 0],
             [-pi, phi],
             ]
    elif not np.allclose(p0[0], p1[0]):
        s = pi if p0[0] < p1[0] else -pi;
        phi = direction * s / 2.;

        r = [[-s, phi],
             [0, phi],
             [s, phi]]
    else:
        r = [p1]
    return r


#def interpolate_spherical_edge_to_spherical_edge(p0, p1):
#    if p0[0] not in [-180, 180] or p0[1] not in [-90, 90]:
#        raise ValueError('PO not an edge point.')
#
#    if p1[0] not in [-180, 180] or p1[1] not in [-90, 90]:
#        raise ValueError('P1 not an edge point.')
#
#    result = [p0]
#    p_next = p0
#
#    # XXX Float worries? 
#    while p0 != p1:
#        if p0[0] < 0:
#            
#
#    while True:
#        if p0[0] == p1[0]:
#            if p0[1] == p1[0]



def draw_polys(polys):
    import matplotlib.pyplot as plt

    import matplotlib.path as mpath
    from matplotlib.patches import PathPatch

    ax = plt.axes()
    ax.margins(0.1)

    for poly in polys:
        paths = []
        paths.append(mpath.Path(poly))
        path = mpath.Path.make_compound_path(*paths)
        ax.add_patch(PathPatch(path, alpha=0.5, facecolor='green',
                               edgecolor='red', lw=3))

    ax.autoscale_view()
    plt.show()


if __name__ == '__main__':
    segments = [
                [(180, 80), (160, 60), (180, 40)],
                [(-180, 40), (-160, 60), (-180, 80)]
                ]
    clip_start_inside = True

    segments = [
                [(180, 80), (160, 60), (180, 40)],
                [(-180, 40), (-160, 60), (-180, 80)],
#                [(-179, -70), (-170, -70), (-170, -80), (-179, -80), (-179, -70)][::-1], # HOLE: Nothing done with this yet
#                [(40, 90), (40, 0), (55.001, 0), (55.001, 90)], # INTERRUPT: Interpolation needs fixing for this case.
#                [(60, -90), (60, 0), (85.001, 0), (85.001, -90)]
                ]
    clip_start_inside = True

    import numpy as np

    # Sort clockwise from (-180, 0)
    edge_sort_quick = lambda (x, y): -np.arctan2(np.deg2rad(y), np.deg2rad(x))
    def edge_sort(intersection_point):
        return edge_sort_quick(intersection_point.xy)

    ends = [[seg[0], seg[-1]] for seg in segments]
    print sorted([item for sublist in ends for item in sublist],
                 key=edge_sort_quick)


#    clip_start_inside = d3_geo_pointInPolygon(rotatedClipStart, polygon)

    polys = Cutter(None, edge_sort).attach_segments(segments, clip_start_inside, interpolate_spherical_edge)
    for p in polys:
        print p
    print len(polys)
    draw_polys(polys)

