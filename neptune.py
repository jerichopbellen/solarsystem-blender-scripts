import bpy
import math

# --- CONFIGURATION ---
NEPTUNE_RADIUS = 2.9 
NEPTUNE_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/2k_neptune.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Neptune
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=NEPTUNE_RADIUS)
    neptune = bpy.context.active_object
    neptune.name = "Neptune"
    bpy.ops.object.shade_smooth()

    # 3. Material (Deep Blue Saturation)
    mat = bpy.data.materials.new(name="NeptuneMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    hsv = nodes.new('ShaderNodeHueSaturation') 
    
    bsdf.inputs['Roughness'].default_value = 0.8 
    hsv.inputs['Saturation'].default_value = 1.6  
    hsv.inputs['Value'].default_value = 0.6 
    
    try:
        tex.image = bpy.data.images.load(NEPTUNE_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], hsv.inputs['Color'])
        links.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        bsdf.inputs['Base Color'].default_value = (0.02, 0.15, 0.6, 1) 
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    neptune.data.materials.append(mat)

    # 3.5 ROTATION (NO TILT)
    # Reset tilt to 0 and animate Z-axis rotation
    neptune.rotation_euler = (0, 0, 0)
    neptune.keyframe_insert(data_path="rotation_euler", frame=1)
    
    neptune.rotation_euler[2] = math.radians(360)
    neptune.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING
    bpy.ops.object.light_add(type='POINT', location=(12, -18, 8))
    light_main = bpy.context.active_object; light_main.data.energy = 35000 
    
    bpy.ops.object.light_add(type='POINT', location=(-7, 8, 0.5))
    light_rim = bpy.context.active_object; light_rim.data.energy = 5000
    
    bpy.ops.object.light_add(type='POINT', location=(-10, -5, 0))
    light_fill = bpy.context.active_object; light_fill.data.energy = 600 

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -12, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER & COLOR MANAGEMENT
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

setup_scene()