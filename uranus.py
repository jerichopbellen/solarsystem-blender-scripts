import bpy
import math

# --- CONFIGURATION ---
URANUS_RADIUS = 3.0 
URANUS_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/2k_uranus.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Uranus
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=URANUS_RADIUS)
    uranus = bpy.context.active_object
    uranus.name = "Uranus"
    bpy.ops.object.shade_smooth()

    # 3. Material (Blue Saturation Boost)
    mat = bpy.data.materials.new(name="UranusMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    hsv = nodes.new('ShaderNodeHueSaturation') 
    
    bsdf.inputs['Roughness'].default_value = 0.8 
    hsv.inputs['Saturation'].default_value = 1.8  # Stronger blue push
    hsv.inputs['Value'].default_value = 0.7       # Prevents white-out
    
    try:
        tex.image = bpy.data.images.load(URANUS_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], hsv.inputs['Color'])
        links.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        bsdf.inputs['Base Color'].default_value = (0.05, 0.4, 0.8, 1) 
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    uranus.data.materials.append(mat)

    # 3.5 ROTATION & AXIAL TILT
    uranus.rotation_euler[0] = math.radians(98)
    uranus.keyframe_insert(data_path="rotation_euler", frame=1)
    uranus.rotation_euler[2] = math.radians(360)
    uranus.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING (EXACT JUPITER SETTINGS)
    bpy.ops.object.light_add(type='POINT', location=(12, -18, 8))
    light_main = bpy.context.active_object; light_main.data.energy = 35000 
    
    bpy.ops.object.light_add(type='POINT', location=(-7, 8, 0.5))
    light_rim = bpy.context.active_object; light_rim.data.energy = 7000
    
    bpy.ops.object.light_add(type='POINT', location=(-10, -5, 0))
    light_fill = bpy.context.active_object; light_fill.data.energy = 400 

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -12, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER & UPDATED COLOR MANAGEMENT
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    
    # FIXED FOR BLENDER 4.0+: Added "AgX - " prefix
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

setup_scene()