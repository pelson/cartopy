class WriteOnlyWrappers(type):
    def __new__(cls, classname, bases, class_dict):
        write_only_properties = class_dict['_write_only_properties']
        target_objects = class_dict['_write_only_property_targets']
#        def draw(self, *args, **kwargs):
#            if self.visible is False:
#                print 'draw **not** called with visible={}'.format(self.visible)
#                return
#            else:
#                return draw_method(self, *args, **kwargs)
#        class_dict['draw'] = draw
           
        return  type.__new__(cls, classname, bases, class_dict)
    
class Gridline1D(object):
    def __init__(self):
        self.visible = False
    
class Gridlines2D(object):
    __metaclass__ = WriteOnlyWrappers
    _write_only_properties = [('visible', 'visible')]
    _write_only_property_targets = ['x', 'y']
    
    def __init__(self):
        self.x = Gridline1D()
        self.y = Gridline1D() 
        
g = Gridlines2D()

g.visible = False