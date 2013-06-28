import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class

class PropHelper():
    def color(self, name = 'Background Color', default = (0, 0, 0)):
        return FloatVectorProperty(name = name, description = '', size = 3,min = 0, max = 1, default = default, subtype = 'COLOR')
    def rays(self):
        return IntProperty(name = 'Rays', description = 'The number of rays', min = 8, max = 8192, default = 128)
    def bias(self, default = 0.08):
        return FloatProperty(name = 'Bias', description = '', default = default, min = 0, max = 1, step = 0.00005, precision = 5)
    def spread_angle(self, default = 88):
        return FloatProperty(name = 'Spread angle', description = '', default = default, min = 0.5, max = 179.5, step = 1)
    def limit_ray_distance(self, default = False):
        return BoolProperty(name = 'Limit ray distance', description = '', default = default)
    def swizzle(self, axis = 'X'):
        return EnumProperty(name = ('Swizzle ' + axis), description = '', default = (axis + '+'), items = (('X+', 'X+', ''),
                                                                                           ('X-', 'X-', ''),
                                                                                           ('Y+', 'Y+', ''),
                                                                                           ('Y-', 'Y-', ''),
                                                                                           ('Z+', 'Z+', ''),
                                                                                           ('Z-', 'Z-', ''),
                                                                                           ))
    def tangent_space(self, default = True):
        return BoolProperty(name = 'Tangent space', description = '', default = default)
    def distribution(self, default = 'Uniform'):
        return EnumProperty(name = 'Distribution',
                            description = '',
                            default = default,
                            items = (('Uniform', 'Uniform', ''),
                                     ('Cosine', 'Cosine', ''),
                                     ('CosineSq', 'CosineSq', ''),
                                     )
                            )
    def jitter(self):
        return BoolProperty(name = 'Jitter', description = '', default = False)
    def normalization(self):
        return EnumProperty(name = 'Normalization',
                            description = '',
                            default = 'Interactive',
                            items = (('Manual', 'Manual normalization', ''),
                                     ('Interactive', 'Interactive normalization', ''),
                                     ('Raw', 'Do not normalize, output raw values', ''),
                                     )
                            )

class MapType(bpy.types.PropertyGroup):
    propHelper = PropHelper()

class NORMAL(MapType):
    bgcolor = MapType.propHelper.color(default = (0.5, 0.5, 1))
    
    swizzle_x = MapType.propHelper.swizzle(axis = 'X')
    swizzle_y = MapType.propHelper.swizzle(axis = 'Y')
    swizzle_z = MapType.propHelper.swizzle(axis = 'Z')
    tangentspace = MapType.propHelper.tangent_space()
    
class HEIGHT(MapType):
    bgcolor = MapType.propHelper.color(default = (0, 0, 0))
    min = FloatProperty(name = 'Minimum', description = '', default = -10, precision = 5)
    max = FloatProperty(name = 'Maximum', description = '', default = 10, precision = 5)
    normalization = MapType.propHelper.normalization()

class AMBIENT_OCCLUSION(MapType):
    bgcolor = MapType.propHelper.color(default = (1, 1, 1))
    
    rays = MapType.propHelper.rays()
    bias = MapType.propHelper.bias()
    spread_angle = MapType.propHelper.spread_angle(default = 162)
    limit_ray_distance = MapType.propHelper.limit_ray_distance()
    distribution = MapType.propHelper.distribution()
    jitter = MapType.propHelper.jitter()
    color_occluded = MapType.propHelper.color(name = 'Occluded Color', default = (0, 0, 0))
    color_unoccluded = MapType.propHelper.color(name = 'Unoccluded Color', default = (1, 1, 1))
    atten1 = FloatProperty(name = 'Attenuation 1', description = '', default = 1, min = 0, max = 1000, step = 1, precision = 5)
    atten2 = FloatProperty(name = 'Attenuation 2', description = '', default = 0, min = 0, max = 1000, step = 1, precision = 5)
    atten3 = FloatProperty(name = 'Attenuation 3', description = '', default = 0, min = 0, max = 1000, step = 1, precision = 5)
    ignore_backfaces = BoolProperty(name = 'Ignore backface hits', description = '', default = False)
    allow_full_occlusion = BoolProperty(name = 'Allow 100% occlusion', description = '', default = True)
    
class BENT_NORMAL(MapType):
    bgcolor = MapType.propHelper.color(default  = (0.5, 0.5, 1))
    
    rays = MapType.propHelper.rays()
    bias = MapType.propHelper.bias()
    spread_angle = MapType.propHelper.spread_angle(default = 162)
    limit_ray_distance = MapType.propHelper.limit_ray_distance()
    distribution = MapType.propHelper.distribution()
    jitter = MapType.propHelper.jitter()
    swizzle_x = MapType.propHelper.swizzle(axis = 'X')
    swizzle_y = MapType.propHelper.swizzle(axis = 'Y')
    swizzle_z = MapType.propHelper.swizzle(axis = 'Z')
    tangentspace = MapType.propHelper.tangent_space(default = False)
    
class PRTPN(MapType):
    bgcolor = MapType.propHelper.color(default  = (0, 0, 0))
    
    rays = MapType.propHelper.rays()
    bias = MapType.propHelper.bias()
    spread_angle = MapType.propHelper.spread_angle(default = 179.50)
    limit_ray_distance = MapType.propHelper.limit_ray_distance()
    jitter = MapType.propHelper.jitter()
    prt_color_normalize = BoolProperty(name = 'PRT Color Normalize', description = '', default = True)
    threshold = FloatProperty(name = 'Threshold', description = '', default = 0.005, min = 0, max = 1, precision = 5)
    
class CONVEXITY(MapType):
    bgcolor = MapType.propHelper.color(default  = (1, 1, 1))
    
    convexity_scale = FloatProperty(name = 'Convexity Scale', description = '', default = 1, min = 0, max = 1, precision = 3)


class THICKNESS(MapType):
    # Has no properties
    pass

class PROXIMITY(MapType):
    bgcolor = MapType.propHelper.color(default  = (1, 1, 1))
    
    rays = MapType.propHelper.rays()
    spread_angle = MapType.propHelper.spread_angle(default = 80)
    limit_ray_distance = MapType.propHelper.limit_ray_distance(default = True)
    
class CAVITY(MapType):
    bgcolor = MapType.propHelper.color(default  = (1, 1, 1))
    
    rays = MapType.propHelper.rays()
    jitter = MapType.propHelper.jitter()
    radius = FloatProperty(name = 'Radius', description = '', default = 0.5, min = 0, precision = 6)
    contrast = FloatProperty(name = 'Contrast', description = '', default = 1.25, min = 0.001, max = 8, precision = 3)
    steps = IntProperty(name = 'Steps', description = '', default = 4, min = 4, max = 128)
    
class WIREFRAME_RAY_FAILS(MapType):
    bgcolor = MapType.propHelper.color(default  = (0, 0, 0))
    
    render_wireframe = BoolProperty(name = 'Render wireframe', description = '', default = True)
    color_wire = MapType.propHelper.color(name = 'Wire Color', default  = (1, 1, 1))
    color_cw = MapType.propHelper.color(name = 'CW Color', default  = (0, 0, 1))
    color_seam = MapType.propHelper.color(name = 'Seam Color', default  = (0, 1, 0))
    
    render_ray_fails = BoolProperty(name = 'Render ray fails', description = '', default = True)
    color_rayfail = MapType.propHelper.color(name = 'Ray fail', default  = (1, 0, 0))
    
class DIRECTION(MapType):
    bgcolor = MapType.propHelper.color(default  = (0, 0, 0))
    
    swizzle_x = MapType.propHelper.swizzle(axis = 'X')
    swizzle_y = MapType.propHelper.swizzle(axis = 'Y')
    swizzle_z = MapType.propHelper.swizzle(axis = 'Z')
    tangentspace = MapType.propHelper.tangent_space(default = False)
    normalization = MapType.propHelper.normalization()
    min = FloatProperty(name = 'Minimum', description = '', default = -10, precision = 5)
    max = FloatProperty(name = 'Maximum', description = '', default = 10, precision = 5)
    
class RADIOSITY_NORMAL(MapType):
    bgcolor = MapType.propHelper.color(default  = (0, 0, 0))
    
    rays = MapType.propHelper.rays()
    encode_occlusion = BoolProperty(name = 'Encode occlusion', description = '', default = True)
    bias = MapType.propHelper.bias()
    spread_angle = MapType.propHelper.spread_angle(default = 162)
    limit_ray_distance = MapType.propHelper.limit_ray_distance()
    jitter = MapType.propHelper.jitter()
    distribution = MapType.propHelper.distribution()
    atten1 = FloatProperty(name = 'Attenuation 1', description = '', default = 1, min = 0, max = 1000, step = 1, precision = 5)
    atten2 = FloatProperty(name = 'Attenuation 2', description = '', default = 0, min = 0, max = 1000, step = 1, precision = 5)
    atten3 = FloatProperty(name = 'Attenuation 3', description = '', default = 0, min = 0, max = 1000, step = 1, precision = 5)
    
    coordinate_system = EnumProperty(name = 'Coordinate System',
                                     description = '',
                                     default = 'ALiB',
                                     items = (('ALiB', 'Ali B', ''),
                                              ('OpenGL', 'OpenGL', ''),
                                              ('Direct3D', 'Direct 3D', ''),
                                              )
                                     )
    
    contrast = FloatProperty(name = 'Contrast', description = '', default = 1, min = 0.05, max = 50, precision = 5)
    allow_full_occlusion = BoolProperty(name = 'Allow pure occlusion', description = '', default = False)
    
class VERTEX_COLOR(MapType):
    bgcolor = MapType.propHelper.color(default  = (1, 1, 1))
    
class CURVATURE(MapType):
    bgcolor = MapType.propHelper.color(default  = (0, 0, 0))
    
    rays = MapType.propHelper.rays()
    jitter = MapType.propHelper.jitter()
    spread_angle = MapType.propHelper.spread_angle(default = 162)
    bias = MapType.propHelper.bias(default = 0.0001)
    distribution = MapType.propHelper.distribution(default = 'Cosine')
    algorithm = EnumProperty(name = 'Algorithm', description = '', default = 'Average', items = (('Average', 'Average', ''), ('Gaussian', 'Gaussian', '')))
    search_distance = FloatProperty(name = 'Search distance', description = '', default = 1, min = 0, max = 10000000, precision = 5)
    tone_mapping = EnumProperty(name = 'Tone mapping', description = '', default = '3Col', items = (('3Col', 'Three colors', ''), ('2Col', 'Two colors', ''), ('Monocrome', 'Monochrome', '')))
    smoothing = BoolProperty(name = 'Smoothing', description = '', default = True)
    
class DERIVATIVE(MapType):
    bgcolor = MapType.propHelper.color(default  = (0.5, 0.5, 0))

# Register all classes
register_class(NORMAL)
register_class(HEIGHT)
register_class(AMBIENT_OCCLUSION)
register_class(BENT_NORMAL)
register_class(PRTPN)
register_class(CONVEXITY)
register_class(THICKNESS)
register_class(PROXIMITY)
register_class(CAVITY)
register_class(WIREFRAME_RAY_FAILS)
register_class(DIRECTION)
register_class(RADIOSITY_NORMAL)
register_class(VERTEX_COLOR)
register_class(CURVATURE)
register_class(DERIVATIVE)

  
