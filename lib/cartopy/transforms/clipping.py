class InterpolationPair(object):
    def __init__(self, p0, p1, transform):
        self.p0 = p0
        self.p1 = p1
        self.transform = transform
    
    def interpolate(self, t):
        # XXX Would do great circle here.
        tp0 = self.transform(self.p0)
        tp1 = self.transform(self.p1)
        sp0, sp1 = self.p0, self.p1
        
        x = sp0[0] + (sp1[0] - sp0[0]) * t
        y = sp0[1] + (sp1[1] - sp0[1]) * t
        
        tp_new = self.transform((x, y))
        d0 = ((tp0[0] - tp_new[0]) ** 2 + (tp0[1] - tp_new[1]) ** 2) ** 0.5
        d1 = ((tp1[0] - tp_new[0]) ** 2 + (tp1[1] - tp_new[1]) ** 2) ** 0.5
        
#         print 'Inter:', sp0, sp1, t, (sp0[0] - sp1[0]) * t, x, y, d0, d1
        return (x, y), (d0, d1)
    
    def distance(self):
        return ((self.p0[0] - self.p1[0]) ** 2 + (self.p0[1] - self.p1[1]) ** 2) ** 0.5

def project_pair(pair, results, t_value=0.5, depth=0):
#     print pair.distance(), t_value, pair.interpolate(t_value)
    new_p, distances = pair.interpolate(t_value)
    
#     result = tuple()
    
    if depth < 4:
        delta = 0.5 ** (depth + 2)
        next_t = [t_value - delta, t_value + delta]
        print 'depth: {}; distances: {}; current t: {}; will try: {};'.format(depth, distances, t_value, next_t)
        for side, dist, new_t in zip(['lhs', 'rhs'], distances, next_t):
            if dist > 5:
                
                result = project_pair(pair, results, new_t, depth=depth+1)
                
                print '    d: {}; s: {}; t: {}; dist: {};, new_p: {}'.format(depth, side, new_t, dist, new_p)
            else:
                results.append(new_t)
#                 return (new_p, )

import numpy as np

def t_cut_point(pair, results, max_distance, t_value=0.5, depth=0):
    new_p, distances = pair.interpolate(t_value)
    
    if depth > 10:
        raise ValueError()
    
    delta = 0.5 ** (depth + 2)
    next_t = [t_value - delta, t_value + delta]
    
    for side, dist, new_t in zip(['lhs', 'rhs'], distances, next_t):
        if dist > 5:
            
            result = project_pair(pair, results, new_t, depth=depth+1)
            
            print '    d: {}; s: {}; t: {}; dist: {};, new_p: {}'.format(depth, side, new_t, dist, new_p)
        else:
            results.append(new_t)
#                 return (new_p, )


def project(geom, transform):
    for i in range(len(geom) - 1):
        p0, p1 = geom[i:i+2]
        pair = InterpolationPair(p0, p1, transform)
        a = []
        print t_cut_point(pair, a, np.array([[]]))
        print a

if __name__ == '__main__':
    
    project([[170, 40], [190, 20]], transform=lambda (x, y): (x % 180, y))