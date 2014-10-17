from nose.tools import assert_equal

import shapely.geometry as sgeom

def fix_topology(polygons):
    for polygon in polygons:
        if polygon.contains(sgeom.Point(90, 0)):
            if polygon




def tests():
    box = sgeom.box(-180, -90, 180, 90)
    assert_equal(fix_topology([box]), False)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-s'], exit=False)