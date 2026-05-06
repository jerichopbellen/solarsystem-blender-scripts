import bpy
import math

# --- CONFIGURATION ---
PLUTO_RADIUS = 0.5  # Smaller than your other planets
PLUTO_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/plutomap2k.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Pluto (High Resolution + Subdivision)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=PLUTO_RADIUS)
    pluto = bpy.context.active_object
    pluto.name = "Pluto"
    
    subsurf = pluto.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 3. Material (With Saturation Push)
    mat = bpy.data.materials.new(name="PlutoMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    hsv = nodes.new('ShaderNodeHueSaturation') 
    
    # Applied your requested Roughness
    bsdf.inputs['Roughness'].default_value = 0.8 
    
    # Applied your requested HSV tweaks
    hsv.inputs['Saturation'].default_value = 1.8  # Stronger push for the reddish-browns
    hsv.inputs['Value'].default_value = 0.7       # Prevents white-out on the heart-shaped glacier
    
    try:
        tex.image = bpy.data.images.load(PLUTO_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], hsv.inputs['Color'])
        links.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        # Fallback color (Dusty Brown)
        bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.15, 1) 
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    pluto.data.materials.append(mat)

    # 3.5 ROTATION
    pluto.rotation_euler = (0, 0, 0)
    pluto.keyframe_insert(data_path="rotation_euler", frame=1)
    
    pluto.rotation_euler[2] = math.radians(360)
    pluto.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING (Adjusted distance slightly for the smaller radius)
    bpy.ops.object.light_add(type='POINT', location=(5, -8, 4))
    light_main = bpy.context.active_object; light_main.data.energy = 9000 
    
    bpy.ops.object.light_add(type='POINT', location=(-3, 4, 0.5))
    light_rim = bpy.context.active_object; light_rim.data.energy = 1500
    
    bpy.ops.object.light_add(type='POINT', location=(-4, -2, 0))
    light_fill = bpy.context.active_object; light_fill.data.energy = 100 

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -3.5, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER & COLOR MANAGEMENT
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

setup_scene()