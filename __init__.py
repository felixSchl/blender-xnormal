bl_info = {
           'name': 'xNormal Integration',
           'author': 'Felix Schlitter',
           'version': (0, 1, 4),
           'blender': (2, 6, 3),
           'category': 'Render',
           'description': 'Bake maps using xNormal',
           'warning': 'Alpha',
           'wiki_url': 'www.felixSchlitter.com/node/32',
           'tracker_url': ''
           }

if "bpy" in locals():
    import imp
    imp.reload(MapTypeSettings)
else:
    from . import MapTypeSettings

import bpy
from bpy.props import *
from bpy.types import Panel, Operator, AddonPreferences
from bpy.utils import register_class, unregister_class
import os
import math


def getPrefs(ctx):
    return ctx.user_preferences.addons[__name__].preferences


def bool2str(boolean):
    if boolean:
        return "true"
    else:
        return "false"
    

def ensure_dir(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            return True
        except:
            return False


class BakeXNormalPreferences(AddonPreferences):
    bl_idname = __name__
    path_to_xNormal = StringProperty(name = 'Path to xNormal',
                                     description = 'The full path to the xNormal executable',
                                     default = '',
                                     subtype = 'FILE_PATH'
                                     )

    def draw(self, ctx):
        l = self.layout
        l.prop(self, "path_to_xNormal")


class BakeXNormalSettings(bpy.types.PropertyGroup):
    
    maptype = EnumProperty(name = 'Map type',
                           description = 'The type of map to bake',
                           default = 'NORMAL',
                           items = (('NORMAL', 'Normal Map', ''),
                                    ('HEIGHT', 'Height Map', ''),
                                    ('BAKE_BASE_TEXTURE', 'Bake Base Texture', ''),
                                    ('AMBIENT_OCCLUSION', 'Ambient Occlusion Map', ''),
                                    ('BENT_NORMAL', 'Bent normal Map', ''),
                                    ('PRTPN', 'PRTpn Map', ''),
                                    ('CONVEXITY', 'Convexity Map', ''),
                                    ('THICKNESS', 'Thickness Map', ''),
                                    ('PROXIMITY', 'Proximity Map', ''),
                                    ('CAVITY', 'Cavity Map', ''),
                                    ('WIREFRAME_RAY_FAILS', 'Wireframe and ray fails', ''),
                                    ('DIRECTION', 'Direction Map', ''),
                                    ('RADIOSITY_NORMAL', 'Radiosity Map', ''),
                                    ('VERTEX_COLOR', 'Vertex Colors', ''),
                                    ('CURVATURE', 'Curvature Map', ''),
                                    ('DERIVATIVE', 'Derivate Map', ''),
                                    ),
                           )

    selected_to_active = BoolProperty(name = 'Selected to active',
                                      description = 'Last selected object is the low poly model',
                                      default = True)
    
    # Constant size options
    sizes = (('16',     '16', ''),
             ('32',     '32', ''),
             ('64',     '64', ''),
             ('128',   '128', ''),
             ('256',   '256', ''),
             ('512',   '512', ''),
             ('1024', '1024', ''),
             ('2048', '2048', ''),
             ('4096', '4096', ''),
             ('8192', '8192', '')
             )
    
    # Size
    width = EnumProperty(name = 'Width',
                         description = 'The width of the rendered map',
                         default = '512',
                         items = sizes
                         )
    
    height = EnumProperty(name = 'Height',
                          description = 'The height of the rendered map',
                          default = '512',
                          items = sizes
                          )
    
    # Padding
    padding = IntProperty(name = 'Padding',
                          description = 'Padding around the rendered map',
                          default = 16,
                          min = 0,
                          max = 128
                          )
    # Bucket Size
    bucket_size = EnumProperty(name = 'Bucket Size',
                               description = '',
                               default = '32',
                               items = (('16',   '16', ''),
                                        ('32',   '32', ''),
                                        ('64',   '64', ''),
                                        ('128', '128', ''),
                                        ('256', '256', ''),
                                        ('512', '512', ''),
                                        )
                               )
    
    # Closest hit if ray fails
    use_closest_hit = BoolProperty(name = 'Closest hit if ray fails',
                                   description = 'Closest hit if ray fails',
                                   default = True, 
                                   )
    
    # Discard back-faces hits
    discard_back_faces = BoolProperty(name = 'Discard back-faces hits',
                                      description = 'Discard back-faces hits',
                                      default = True, 
                                      )
    
    # Anti aliasing
    anti_aliasing = EnumProperty(name = 'Antialiasing',
                                 description = '',
                                 default = '1',
                                 items = (('1',   '1x', '', 0),
                                          ('2',   '2x', '', 1),
                                          ('4',   '4x', '', 2)
                                          )
                                 )

    import tempfile
    homedir = tempfile.gettempdir()
    meshdir = os.path.join(homedir, 'xnormal_meshes')
    lowdir = os.path.join(meshdir, 'low.obj')
    cagedir = os.path.join(meshdir, 'cage.obj')
    highdir = os.path.join(meshdir, 'high.obj')
    outdir = os.path.join(meshdir, 'out.tga')

    # Output
    output = StringProperty(name = 'Output path',
                            description = 'The path of the output image. The given extension determines the file type!',
                            default = outdir,
                            subtype = 'FILE_PATH'
                            )
    
    # Low-specific options
    low_match_uvs = BoolProperty(name = 'Match UVs', description = '', default = False)
    low_offset_u = IntProperty(name = 'U Offset', description = '', default = 0)
    low_offset_v = IntProperty(name = 'V Offset', description = '', default = 0)
    low_normals = EnumProperty(name = 'Smooth normals', description = '', default = 'UseExportedNormals', items = (('UseExportedNormals', 'Exported normals', ''),
                                                                                                         ('AverageNormals', 'Average normals', ''),
                                                                                                         ('HardenNormals', 'Harden normals', ''),
                                                                                                         )
                               )
    low_scale = FloatProperty(name = 'Scale', description = '', default = 1, min = 1, precision = 1)
    
    # @todo: max ray distance front
    # @todo: max ray distance rear
    low_path = StringProperty(name = 'Path to low mesh',
                              description = 'The full path to the low mesh',
                              default = lowdir,
                              subtype = 'FILE_PATH'
                              )
    
    use_cage = BoolProperty(name = 'Use a cage Mesh', description = '', default = False)
    cage_path = StringProperty(name = 'Path to cage mesh',
                              description = 'The full path to the cage mesh',
                              default = cagedir,
                              subtype = 'FILE_PATH'
                              )
    
    
    # High-specific options
    high_ignore_per_vertex_color = BoolProperty(name = 'Ignore per-vertex-color', description = '', default = True)
    high_path = StringProperty(name = 'Path to high mesh',
                               description = 'The full path to the high mesh',
                               default = highdir,
                               subtype = 'FILE_PATH'
                               )
    high_normals = EnumProperty(name = 'Smooth normals', description = '', default = 'AverageNormals', items = (('UseExportedNormals', 'Exported normals', ''),
                                                                                                        ('AverageNormals', 'Average normals', ''),
                                                                                                        ('HardenNormals', 'Harden normals', ''),
                                                                                                        )
                                )
    high_scale = FloatProperty(name = 'Scale', description = '', default = 1, min = 1, precision = 1)
                                  
    # MapType specific settings
    NORMAL_settings = PointerProperty(type = MapTypeSettings.NORMAL)
    HEIGHT_settings = PointerProperty(type = MapTypeSettings.HEIGHT)
    AMBIENT_OCCLUSION_settings = PointerProperty(type = MapTypeSettings.AMBIENT_OCCLUSION)
    BENT_NORMAL_settings = PointerProperty(type = MapTypeSettings.BENT_NORMAL)
    PRTPN_settings = PointerProperty(type = MapTypeSettings.PRTPN)
    CONVEXITY_settings = PointerProperty(type = MapTypeSettings.CONVEXITY)
    THICKNESS_settings = PointerProperty(type = MapTypeSettings.THICKNESS)
    PROXIMITY_settings = PointerProperty(type = MapTypeSettings.PROXIMITY)
    CAVITY_settings = PointerProperty(type = MapTypeSettings.CAVITY)
    WIREFRAME_RAY_FAILS_settings = PointerProperty(type = MapTypeSettings.WIREFRAME_RAY_FAILS)
    DIRECTION_settings = PointerProperty(type = MapTypeSettings.DIRECTION)
    RADIOSITY_NORMAL_settings = PointerProperty(type = MapTypeSettings.RADIOSITY_NORMAL)
    VERTEX_COLOR_settings = PointerProperty(type = MapTypeSettings.VERTEX_COLOR)
    CURVATURE_settings = PointerProperty(type = MapTypeSettings.CURVATURE)
    DERIVATIVE_settings = PointerProperty(type = MapTypeSettings.DERIVATIVE)
    
register_class(BakeXNormalSettings)
bpy.types.Scene.xnormal_settings = PointerProperty(type = BakeXNormalSettings)


class OBJECT_OP_open_bake_dir(bpy.types.Operator):
    bl_idname = 'object.open_bake_dir'
    bl_label = 'Open bakes directory'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        output = bpy.context.scene.xnormal_settings.output
        directory, filename = os.path.split(output)
        os.system('explorer.exe ' + directory)
        return {'FINISHED'}


class Export_for_xnormal(Operator): 
    bl_label = 'Export for xNormal'
    bl_description = 'Exports selected objects for use in xNormal baker'
    
    filepath = ''
    
    def execute(self, context):
        
        # Make sure the target directory exists
        directory, filename = os.path.split(self.filepath)
        ensure_dir(directory)
            
        bpy.ops.export_scene.obj(
                                 filepath = self.filepath,
                                 use_selection = True,
                                 use_apply_modifiers = True,
                                 use_edges = True,
                                 use_normals = True,
                                 use_uvs = True,
                                 use_materials = False,
                                 use_triangles = False,
                                 use_nurbs = False,
                                 use_vertex_groups = False,
                                 group_by_object = True,
                                 keep_vertex_order = True,
                                 )
        return {'FINISHED'}


class OBJECT_OT_export_for_xnormal_low(Export_for_xnormal):
    bl_idname = 'export_scene.obj_for_xnormal_low'
    bl_label = 'Export selected for xNormal (lowpoly)'
    
    def __init__(self):
        settings = bpy.context.scene.xnormal_settings
        self.filepath = settings.low_path


class OBJECT_OT_export_for_xnormal_cage(Export_for_xnormal):
    bl_idname = 'export_scene.obj_for_xnormal_cage'
    bl_label = 'Export selected for xNormal (Cage)'
    
    def __init__(self):
        settings = bpy.context.scene.xnormal_settings
        self.filepath = settings.cage_path


class OBJECT_OT_export_for_xnormal_high(Export_for_xnormal):
    bl_idname = 'export_scene.obj_for_xnormal_high'
    bl_label = 'Export selected for xNormal (highpoly)'
    
    def __init__(self):
        settings = bpy.context.scene.xnormal_settings
        self.filepath = settings.high_path


class OBJECT_OT_bake_with_xnormal(Operator):
    """ Bake using the external xNormal normal map baking tool """
    bl_idname = 'object.bake_with_xnormal'
    bl_label = 'Bake'
    
    def execute(self, context):
        
        settings = bpy.context.scene.xnormal_settings
        #import xml.dom.minidom as minidom
        from xml.dom.minidom import Document
        
        config = Document()
        xml_settings = config.createElement("Settings") 
        config.appendChild(xml_settings)
        
        #
        # High Poly Mesh
        #
        
        xml_highpoly = config.createElement("HighPolyModel")
        xml_settings.appendChild(xml_highpoly)
        
        xml_highpolymesh = config.createElement("Mesh")
        xml_highpoly.appendChild(xml_highpolymesh)
        
        # Variables
        xml_highpolymesh.setAttribute("IgnorePerVertexColor", bool2str(settings.high_ignore_per_vertex_color))
        xml_highpolymesh.setAttribute("AverageNormals", str(settings.high_normals))
        xml_highpolymesh.setAttribute("File", str(settings.high_path))
        xml_highpolymesh.setAttribute("Scale", str(settings.high_scale))
        
        #
        # Low Poly Mesh
        #
        
        xml_lowpoly = config.createElement("LowPolyModel")
        xml_settings.appendChild(xml_lowpoly)
        
        xml_lowpolymesh = config.createElement("Mesh")
        xml_lowpoly.appendChild(xml_lowpolymesh)

        # Variables
        xml_lowpolymesh.setAttribute("File", str(settings.low_path))
        xml_lowpolymesh.setAttribute("AverageNormals", str(settings.low_normals))
        xml_lowpolymesh.setAttribute("MatchUVs", str(settings.low_match_uvs))
        xml_lowpolymesh.setAttribute("UOffset", str(settings.low_offset_u))
        xml_lowpolymesh.setAttribute("VOffset", str(settings.low_offset_v))
        xml_lowpolymesh.setAttribute("Scale", str(settings.low_scale))
        
        # If cagefile
        if (settings.use_cage):
            xml_lowpolymesh.setAttribute("CageFile", settings.cage_path)
            xml_lowpolymesh.setAttribute("UseCage", bool2str(settings.use_cage))
            
        #
        # The Maps
        #
        
        xml_genmaps = config.createElement("GenerateMaps")
        xml_settings.appendChild(xml_genmaps)
        
        #common settings
        xml_genmaps.setAttribute("Width", str(settings.width))
        xml_genmaps.setAttribute("Height", str(settings.height))
        xml_genmaps.setAttribute("EdgePadding", str(settings.padding))
        xml_genmaps.setAttribute("BucketSize", str(settings.bucket_size))
        xml_genmaps.setAttribute("AA", str(settings.anti_aliasing))
        xml_genmaps.setAttribute("ClosestIfFails", bool2str(settings.use_closest_hit))
        xml_genmaps.setAttribute("DiscardRayBackFacesHits", bool2str(settings.discard_back_faces))
        xml_genmaps.setAttribute("File", str(settings.output))
        
        def denormalize(float):
            return math.ceil(float * 255.0)
        
        def generateColorXML(name, vector):
            xml_col = config.createElement(name)
            xml_col.setAttribute("R", str(denormalize(vector[0])))
            xml_col.setAttribute("G", str(denormalize(vector[1])))
            xml_col.setAttribute("B", str(denormalize(vector[2])))
            return xml_col
        
        # Set GenNormals false or else xNormal will assume it's true
        xml_genmaps.setAttribute("GenNormals", "false")
        
        # Which map do we bake?
        if settings.maptype == 'NORMAL':
            s = settings.NORMAL_settings
            xml_genmaps.setAttribute("GenNormals", "true")
            xml_genmaps.setAttribute("SwizzleX", str(s.swizzle_x))
            xml_genmaps.setAttribute("SwizzleY", str(s.swizzle_y))
            xml_genmaps.setAttribute("SwizzleZ", str(s.swizzle_z))
            xml_genmaps.setAttribute("TangentSpace", bool2str(s.tangentspace))
            
            xml_genmaps.appendChild(generateColorXML(name = 'NMBackgroundColor', vector = s.bgcolor)) 
            
        elif settings.maptype == 'HEIGHT':
            s = settings.HEIGHT_settings
            xml_genmaps.setAttribute("GenHeights", "true")
            xml_genmaps.setAttribute("HeightTonemap", str(s.normalization))
            xml_genmaps.setAttribute("HeightMinVal", str(s.min))
            xml_genmaps.setAttribute("HeightMaxVal", str(s.max))
            
            xml_genmaps.appendChild(generateColorXML(name = 'HMBackgroundColor', vector = s.bgcolor))
            
        elif settings.maptype == 'AMBIENT_OCCLUSION':
            s = settings.AMBIENT_OCCLUSION_settings
            xml_genmaps.setAttribute("GenAO", "true")
            xml_genmaps.setAttribute("AORaysPerSample", str(s.rays))
            xml_genmaps.setAttribute("AODistribution", str(s.distribution))
            xml_genmaps.setAttribute("AOConeAngle", str(s.spread_angle))
            xml_genmaps.setAttribute("AOBias", str(s.bias))
            xml_genmaps.setAttribute("AOAllowPureOccluded", bool2str(s.allow_full_occlusion))
            xml_genmaps.setAttribute("AOLimitRayDistance", bool2str(s.limit_ray_distance))
            xml_genmaps.setAttribute("AOAttenConstant", str(s.atten1))
            xml_genmaps.setAttribute("AOAttenLinear", str(s.atten2))
            xml_genmaps.setAttribute("AOAttenCuadratic", str(s.atten3))
            xml_genmaps.setAttribute("AOJitter", bool2str(s.jitter))
            xml_genmaps.setAttribute("AOIgnoreBackfaceHits", bool2str(s.ignore_backfaces))
            
            xml_genmaps.appendChild(generateColorXML(name = 'AOBackgroundColor', vector = s.bgcolor))
            xml_genmaps.appendChild(generateColorXML(name = 'AOOccludedColor', vector = s.color_occluded))
            xml_genmaps.appendChild(generateColorXML(name = 'AOUnoccludedColor', vector = s.color_unoccluded))
         
        elif settings.maptype == 'BENT_NORMAL':
            s = settings.BENT_NORMAL_settings
            xml_genmaps.setAttribute("GenBent", "true")
            xml_genmaps.setAttribute("BentRaysPerSample", str(s.rays))
            xml_genmaps.setAttribute("BentConeAngle", str(s.spread_angle))
            xml_genmaps.setAttribute("BentBias", str(s.bias))
            xml_genmaps.setAttribute("BentTangentSpace", bool2str(s.tangentspace))
            xml_genmaps.setAttribute("BentLimitRayDistance", bool2str(s.limit_ray_distance))
            xml_genmaps.setAttribute("BentJitter", bool2str(s.jitter))
            xml_genmaps.setAttribute("BentDistribution", str(s.distribution))
            xml_genmaps.setAttribute("BentSwizzleX", str(s.swizzle_x))
            xml_genmaps.setAttribute("BentSwizzleY", str(s.swizzle_y))
            xml_genmaps.setAttribute("BentSwizzleZ", str(s.swizzle_z))
            
            xml_genmaps.appendChild(generateColorXML(name = 'BentBackgroundColor', vector = s.bgcolor))
        
        elif settings.maptype == 'PRTPN':
            s = settings.PRTPN_settings
            xml_genmaps.setAttribute("GenPRT", "true")
            xml_genmaps.setAttribute("PRTRaysPerSample", str(s.rays))
            xml_genmaps.setAttribute("PRTConeAngle", str(s.spread_angle))
            xml_genmaps.setAttribute("PRTBias", str(s.bias))
            xml_genmaps.setAttribute("PRTLimitRayDistance", bool2str(s.limit_ray_distance))
            xml_genmaps.setAttribute("PRTJitter", bool2str(s.jitter))
            xml_genmaps.setAttribute("PRTNormalize", bool2str(s.prt_color_normalize))
            xml_genmaps.setAttribute("PRTThreshold", str(s.threshold))
        
            xml_genmaps.appendChild(generateColorXML(name = 'PRTBackgroundColor', vector = s.bgcolor))
        
        elif settings.maptype == 'CONVEXITY':
            s = settings.CONVEXITY_settings
            xml_genmaps.setAttribute("GenConvexity", "true")
            xml_genmaps.setAttribute("ConvexityScale", str(s.convexity_scale))
            
            xml_genmaps.appendChild(generateColorXML(name = 'ConvexityBackgroundColor', vector = s.bgcolor))
        
        elif settings.maptype == 'THICKNESS':
            # Has no properties
            xml_genmaps.setAttribute("GenThickness", "true")
           
        elif settings.maptype == 'PROXIMITY':
            s = settings.PROXIMITY_settings
            xml_genmaps.setAttribute("GenProximity", "true")
            xml_genmaps.setAttribute("ProximityRaysPerSample", str(s.rays))
            xml_genmaps.setAttribute("ProximityConeAngle", str(s.spread_angle))
            xml_genmaps.setAttribute("ProximityLimitRayDistance", bool2str(s.limit_ray_distance))
            
            xml_genmaps.appendChild(generateColorXML(name = 'ProximityBackgroundColor', vector = s.bgcolor))
        
        elif settings.maptype == 'CAVITY':
            s = settings.CAVITY_settings
            xml_genmaps.setAttribute("GenCavity", "true")
            xml_genmaps.setAttribute("CavityRaysPerSample", str(s.rays))
            xml_genmaps.setAttribute("CavityJitter", bool2str(s.jitter))
            xml_genmaps.setAttribute("CavitySearchRadius", str(s.radius))
            xml_genmaps.setAttribute("CavityContrast", str(s.contrast))
            xml_genmaps.setAttribute("CavitySteps", str(s.steps))
        
            xml_genmaps.appendChild(generateColorXML(name = 'CavityBackgroundColor', vector = s.bgcolor))
        
        elif settings.maptype == 'WIREFRAME_RAY_FAILS':
            s = settings.WIREFRAME_RAY_FAILS_settings
            xml_genmaps.setAttribute("GenWireRays", "true")
            xml_genmaps.setAttribute("RenderRayFails", bool2str(s.render_ray_fails))
            xml_genmaps.setAttribute("RenderWireframe", bool2str(s.render_wireframe))
            
            xml_genmaps.appendChild(generateColorXML(name = 'RenderWireframeCol', vector = s.color_wire))
            xml_genmaps.appendChild(generateColorXML(name = 'RenderCWCol', vector = s.color_cw))
            xml_genmaps.appendChild(generateColorXML(name = 'RenderSeamCol', vector = s.color_seam))
            xml_genmaps.appendChild(generateColorXML(name = 'RenderRayFailsCol', vector = s.color_rayfail))
            xml_genmaps.appendChild(generateColorXML(name = 'RenderWireframeBackgroundColor', vector = s.bgcolor))
        
        elif settings.maptype == 'DIRECTION':
            s = settings.DIRECTION_settings
            xml_genmaps.setAttribute("GenDirections", "true")
            xml_genmaps.setAttribute("DirectionsTS", bool2str(s.tangentspace))
            xml_genmaps.setAttribute("DirectionsSwizzleX", str(s.swizzle_x))
            xml_genmaps.setAttribute("DirectionsSwizzleY", str(s.swizzle_y))
            xml_genmaps.setAttribute("DirectionsSwizzleZ", str(s.swizzle_z))
            xml_genmaps.setAttribute("DirectionsTonemap", str(s.normalization))
            xml_genmaps.setAttribute("DirectionsMinVal", str(s.min))
            xml_genmaps.setAttribute("DirectionsMaxVal", str(s.max))
            
            xml_genmaps.appendChild(generateColorXML(name = 'VDMBackgroundColor', vector = s.bgcolor))
        
        elif settings.maptype == 'RADIOSITY_NORMAL':
            s = settings.RADIOSITY_NORMAL_settings
            xml_genmaps.setAttribute("GenRadiosityNormals", "true")
            xml_genmaps.setAttribute("RadiosityNormalsRaysPerSample", str(s.rays))
            xml_genmaps.setAttribute("RadiosityNormalsDistribution", str(s.distribution))
            xml_genmaps.setAttribute("RadiosityNormalsConeAngle", str(s.spread_angle))
            xml_genmaps.setAttribute("RadiosityNormalsBias", str(s.bias))
            xml_genmaps.setAttribute("RadiosityNormalsLimitRayDistance", bool2str(s.limit_ray_distance))
            xml_genmaps.setAttribute("RadiosityNormalsAttenConstant", str(s.atten1))
            xml_genmaps.setAttribute("RadiosityNormalsAttenLinear", str(s.atten2))
            xml_genmaps.setAttribute("RadiosityNormalsAttenCuadratic", str(s.atten3))
            xml_genmaps.setAttribute("RadiosityNormalsJitter", bool2str(s.jitter))
            xml_genmaps.setAttribute("RadiosityNormalsContrast", str(s.contrast))
            xml_genmaps.setAttribute("RadiosityNormalsEncodeAO", bool2str(s.encode_occlusion))
            xml_genmaps.setAttribute("RadiosityNormalsCoordSys", str(s.coordinate_system))
            xml_genmaps.setAttribute("RadiosityNormalsAllowPureOcclusion", bool2str(s.allow_full_occlusion))
            
            xml_genmaps.appendChild(generateColorXML(name = 'RadNMBackgroundColor', vector = s.bgcolor))
            
        elif settings.maptype == 'VERTEX_COLOR':
            s = settings.VERTEX_COLOR_settings
            # Has no further properties
            xml_genmaps.setAttribute("BakeHighpolyVCols", "true")
            
            xml_genmaps.appendChild(generateColorXML(name = 'BakeHighpolyVColsBackgroundCol', vector = s.bgcolor))
        
        elif settings.maptype == 'CURVATURE':
            s = settings.CURVATURE_settings
            xml_genmaps.setAttribute("GenCurv", "true")
            xml_genmaps.setAttribute("CurvRaysPerSample", str(s.rays))
            xml_genmaps.setAttribute("CurvBias", str(s.bias))
            xml_genmaps.setAttribute("CurvConeAngle", str(s.spread_angle))
            xml_genmaps.setAttribute("CurvJitter", bool2str(s.jitter))
            xml_genmaps.setAttribute("CurvSearchDistance", str(s.search_distance))
            xml_genmaps.setAttribute("CurvTonemap", str(s.tone_mapping))
            xml_genmaps.setAttribute("CurvDistribution", str(s.distribution))
            xml_genmaps.setAttribute("CurvAlgorithm", str(s.algorithm))
            xml_genmaps.setAttribute("CurvSmoothing", bool2str(s.smoothing))
            
            xml_genmaps.appendChild(generateColorXML(name = 'CurvBackgroundColor', vector = s.bgcolor))
            
        elif settings.maptype == 'DERIVATIVE':
            s = settings.DERIVATIVE_settings
            # Has no further properties
            xml_genmaps.setAttribute("GenDerivNM", "true")
            
            xml_genmaps.appendChild(generateColorXML(name = 'DerivNMBackgroundColor', vector = s.bgcolor))
            
        # Save XML to disk
        import tempfile
        tempdir = tempfile.gettempdir()
        ensure_dir(tempdir)
        temporary_xml_file = tempfile.NamedTemporaryFile(mode = 'w', dir = tempdir, delete = False)
        config.writexml(temporary_xml_file, addindent = "\t", newl = "\n")
        
        # Launch xNormal
        import subprocess
        prefs = getPrefs(context)
        exe = prefs.path_to_xNormal
        command = exe + " " + os.path.join(tempdir, temporary_xml_file.name)
        subprocess.Popen(command)
        
        temporary_xml_file.close()
        
        return {'FINISHED'}


class OBJECT_PT_xnormal(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_label = 'Bake with xNormal'
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        settings = scene.xnormal_settings
        
        col_all = layout.column()
        
        
        row = col_all.row(align = True)
        row.operator('export_scene.obj_for_xnormal_low', text = 'Export Low')
        row.operator('export_scene.obj_for_xnormal_high', text = 'Export High')
        row.operator('export_scene.obj_for_xnormal_cage', text = 'Export Cage')
        
        row = col_all.row(align = True)
        row.prop(settings, 'use_cage')
        
        col_all.operator('object.bake_with_xnormal', icon = 'RENDER_STILL')
        col_all.operator('object.open_bake_dir', icon = 'FILESEL')
        
        col_all.separator()
        
        # Show general props first
        box_general = col_all.box()

        # Size
        row = box_general.row(align = True)
        row.label(text = 'Size')
        row.prop(settings, 'width', text = '')
        row.prop(settings, 'height', text = '')
        
        # Padding and bucket size
        row = box_general.row()
        row.prop(settings, 'padding')
        row.prop(settings, 'bucket_size')
        
        # Closest hit and discard back faces 
        row = box_general.row()
        row.prop(settings, 'use_closest_hit')
        row.prop(settings, 'discard_back_faces')
        
        # Anti aliasing
        row = box_general.row()
        row.prop(settings, 'anti_aliasing')
        
        # Output
        box_general.prop(settings, 'output', text = 'Output')
        
        # Show specific options
        col_all.separator()
        box = col_all.box()
        box.label(text = 'What to bake and how to bake it:')
        box.prop(settings, 'maptype', text = '')
        # Normal map settings
        if settings.maptype == 'NORMAL':
            row = box.row(align = True)
            row.label(text = 'Swizzle Coordinates')
            row.prop(settings.NORMAL_settings, 'swizzle_x', text = '')
            row.prop(settings.NORMAL_settings, 'swizzle_y', text = '')
            row.prop(settings.NORMAL_settings, 'swizzle_z', text = '')
            box.prop(settings.NORMAL_settings, 'tangentspace')
            box.prop(settings.NORMAL_settings, 'bgcolor')
        
        elif settings.maptype == 'HEIGHT':
            box.prop(settings.HEIGHT_settings, 'normalization')
            
            if settings.HEIGHT_settings.normalization == 'Manual':
                row = box.row()
                row.prop(settings.HEIGHT_settings, 'min')
                row.prop(settings.HEIGHT_settings, 'min')
            
            box.prop(settings.HEIGHT_settings, 'bgcolor')
        
        elif settings.maptype == 'AMBIENT_OCCLUSION':
            box.prop(settings.AMBIENT_OCCLUSION_settings, 'rays')
            box.prop(settings.AMBIENT_OCCLUSION_settings, 'distribution')
            
            row = box.row()
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'color_occluded')
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'color_unoccluded')
            
            row = box.row()
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'bias')
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'spread_angle')
            
            box.prop(settings.AMBIENT_OCCLUSION_settings, 'limit_ray_distance')
            
            row = box.row(align = True)
            row.label(text = 'Attenuation')
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'atten1', text = '')
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'atten2', text = '')
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'atten3', text = '')
            
            row = box.row()
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'jitter')
            row.prop(settings.AMBIENT_OCCLUSION_settings, 'ignore_backfaces')
            
            box.prop(settings.AMBIENT_OCCLUSION_settings, 'allow_full_occlusion')
            box.prop(settings.AMBIENT_OCCLUSION_settings, 'bgcolor')
            
        elif settings.maptype == 'BENT_NORMAL':
            box.prop(settings.BENT_NORMAL_settings, 'rays')
            
            row = box.row()
            row.prop(settings.BENT_NORMAL_settings, 'bias')
            row.prop(settings.BENT_NORMAL_settings, 'spread_angle')
            
            row = box.row()
            row.prop(settings.BENT_NORMAL_settings, 'limit_ray_distance')
            row.prop(settings.BENT_NORMAL_settings, 'jitter')
            
            row = box.row(align = True)
            row.label(text = 'Swizzle Coordinates')
            row.prop(settings.BENT_NORMAL_settings, 'swizzle_x', text = '')
            row.prop(settings.BENT_NORMAL_settings, 'swizzle_y', text = '')
            row.prop(settings.BENT_NORMAL_settings, 'swizzle_z', text = '')
            
            box.prop(settings.BENT_NORMAL_settings, 'tangentspace')
            box.prop(settings.BENT_NORMAL_settings, 'distribution')
            box.prop(settings.BENT_NORMAL_settings, 'bgcolor')
            
        elif settings.maptype == 'PRTPN':
            box.prop(settings.PRTPN_settings, 'rays')
            
            row = box.row()
            row.prop(settings.PRTPN_settings, 'bias')
            row.prop(settings.PRTPN_settings, 'spread_angle')
            
            row = box.row()
            row.prop(settings.PRTPN_settings, 'limit_ray_distance')
            row.prop(settings.PRTPN_settings, 'jitter')
            
            box.prop(settings.PRTPN_settings, 'prt_color_normalize')
            box.prop(settings.PRTPN_settings, 'threshold')
            box.prop(settings.PRTPN_settings, 'bgcolor')
            
        elif settings.maptype == 'CONVEXITY':
            box.prop(settings.CONVEXITY_settings, 'convexity_scale')
            box.prop(settings.CONVEXITY_settings, 'bgcolor')
            
        elif settings.maptype == 'THICKNESS':
            # Has no properties
            pass
        
        elif settings.maptype == 'PROXIMITY':
            box.prop(settings.PROXIMITY_settings, 'rays')
            box.prop(settings.PROXIMITY_settings, 'spread_angle')
            box.prop(settings.PROXIMITY_settings, 'limit_ray_distance')
            box.prop(settings.PROXIMITY_settings, 'bgcolor')
            
        elif settings.maptype == 'CAVITY':
            row = box.row()
            row.prop(settings.CAVITY_settings, 'rays')
            row.prop(settings.CAVITY_settings, 'jitter')
            
            box.prop(settings.CAVITY_settings, 'radius')
            box.prop(settings.CAVITY_settings, 'contrast')
            box.prop(settings.CAVITY_settings, 'steps')
            box.prop(settings.CAVITY_settings, 'bgcolor')
            
        elif settings.maptype == 'WIREFRAME_RAY_FAILS':
            box.prop(settings.WIREFRAME_RAY_FAILS_settings, 'render_wireframe')
            box.prop(settings.WIREFRAME_RAY_FAILS_settings, 'color_wire')
            box.prop(settings.WIREFRAME_RAY_FAILS_settings, 'color_cw')
            box.prop(settings.WIREFRAME_RAY_FAILS_settings, 'color_seam')
            box.prop(settings.WIREFRAME_RAY_FAILS_settings, 'render_ray_fails')
            box.prop(settings.WIREFRAME_RAY_FAILS_settings, 'color_rayfail')
            box.prop(settings.WIREFRAME_RAY_FAILS_settings, 'bgcolor')
            
        elif settings.maptype == 'DIRECTION':    
            row = box.row(align = True)
            row.label(text = 'Swizzle Coordinates')
            row.prop(settings.DIRECTION_settings, 'swizzle_x', text = '')
            row.prop(settings.DIRECTION_settings, 'swizzle_y', text = '')
            row.prop(settings.DIRECTION_settings, 'swizzle_z', text = '')
            
            box.prop(settings.DIRECTION_settings, 'tangentspace')
            box.prop(settings.DIRECTION_settings, 'normalization')
            
            if settings.DIRECTION_settings.normalization == 'Manual':
                row = box.row()
                row.prop(settings.DIRECTION_settings, 'min')
                row.prop(settings.DIRECTION_settings, 'min')
                
            box.prop(settings.DIRECTION_settings, 'bgcolor')
            
        elif settings.maptype == 'RADIOSITY_NORMAL':
            row = box.row()
            row.prop(settings.RADIOSITY_NORMAL_settings, 'rays')
            row.prop(settings.RADIOSITY_NORMAL_settings, 'encode_occlusion')
            
            box.prop(settings.RADIOSITY_NORMAL_settings, 'distribution')
        
            row = box.row()
            row.prop(settings.RADIOSITY_NORMAL_settings, 'bias')
            row.prop(settings.RADIOSITY_NORMAL_settings, 'spread_angle')
            
            row = box.row(align = True)
            row.label(text = 'Attenuation')
            row.prop(settings.RADIOSITY_NORMAL_settings, 'atten1', text = '')
            row.prop(settings.RADIOSITY_NORMAL_settings, 'atten2', text = '')
            row.prop(settings.RADIOSITY_NORMAL_settings, 'atten3', text = '')
        
            box.prop(settings.RADIOSITY_NORMAL_settings, 'coordinate_system')
            
            row = box.row()
            row.prop(settings.RADIOSITY_NORMAL_settings, 'contrast')
            row.prop(settings.RADIOSITY_NORMAL_settings, 'allow_full_occlusion')
            
            box.prop(settings.RADIOSITY_NORMAL_settings, 'bgcolor')
            
        elif settings.maptype == 'VERTEX_COLOR':   
            box.prop(settings.VERTEX_COLOR_settings, 'bgcolor')
            
        elif settings.maptype == 'CURVATURE':
            row = box.row()
            row.prop(settings.CURVATURE_settings, 'rays')
            row.prop(settings.CURVATURE_settings, 'jitter')
            
            row = box.row()
            row.prop(settings.CURVATURE_settings, 'spread_angle')
            row.prop(settings.CURVATURE_settings, 'bias')
             
            box.prop(settings.CURVATURE_settings, 'algorithm')
            box.prop(settings.CURVATURE_settings, 'distribution')
            box.prop(settings.CURVATURE_settings, 'search_distance')
            
            row = box.row()
            row.prop(settings.CURVATURE_settings, 'tone_mapping')
            row.prop(settings.CURVATURE_settings, 'smoothing')
               
            box.prop(settings.CURVATURE_settings, 'bgcolor') 
              
        elif settings.maptype == 'DERIVATIVE':   
            box.prop(settings.DERIVATIVE_settings, 'bgcolor')
        
        box.operator('object.bake_with_xnormal', icon = 'RENDER_STILL')
        
        #
        # Show options for all low poly meshes
        #
        
        col_all.separator()
        box = col_all.box()
        box.label(text = 'Low resultion mesh options:')
        box.prop(settings, 'low_scale')
        box.prop(settings, 'low_match_uvs')
        box.prop(settings, 'low_normals') 
        row = box.row(align = True)
        row.prop(settings, 'low_offset_u')
        row.prop(settings, 'low_offset_v')
        box.prop(settings, 'low_path')
        
        box.prop(settings, 'use_cage')
        box.prop(settings, 'cage_path')
        
        row = box.row(align = True)
        row.operator('export_scene.obj_for_xnormal_low')
        
        #
        # Show options for all high poly meshes
        #
        
        col_all.separator()
        box = col_all.box()
        box.label(text = 'High resultion mesh options:')
        box.prop(settings, 'high_scale')
        box.prop(settings, 'high_ignore_per_vertex_color')
        box.prop(settings, 'high_normals')
        box.prop(settings, 'high_path')
        box.operator('export_scene.obj_for_xnormal_high')


def register():
    register_class(BakeXNormalPreferences)
    register_class(OBJECT_OP_open_bake_dir)
    register_class(OBJECT_OT_export_for_xnormal_low)
    register_class(OBJECT_OT_export_for_xnormal_cage)
    register_class(OBJECT_OT_export_for_xnormal_high)
    register_class(OBJECT_OT_bake_with_xnormal)
    register_class(OBJECT_PT_xnormal)
    

def unregister():
    unregister_class(BakeXNormalPreferences)
    unregister_class(OBJECT_PT_xnormal)
    unregister_class(OBJECT_OP_open_bake_dir)
    unregister_class(OBJECT_OT_bake_with_xnormal)
    unregister_class(OBJECT_OT_export_for_xnormal_low)
    unregister_class(OBJECT_OT_export_for_xnormal_cage)
    unregister_class(OBJECT_OT_export_for_xnormal_high)

if __name__ == '__main__':
    register()