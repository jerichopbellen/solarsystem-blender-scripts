import bpy

# --- CONFIGURATION ---
VENUS_RADIUS = 0.75 
# Note: You can swap this path for your Venus texture if you have one
VENUS_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_venus_surface.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Venus (Slightly smaller than Mercury)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=VENUS_RADIUS)
    venus = bpy.context.active_object
    venus.name = "Venus"
    bpy.ops.object.shade_smooth()

    # 3. Material (Optimized for Venus's cloud-like surface)
    mat = bpy.data.materials.new(name="VenusMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    
    # Venus is more reflective and smoother than Mercury
    bsdf.inputs['Roughness'].default_value = 0.4 
    bsdf.inputs['Base Color'].default_value = (0.9, 0.85, 0.7, 1) # Warm, yellowish hue
    
    try:
        tex.image = bpy.data.images.load(VENUS_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        pass # Fallback to default warm color if texture is missing
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    venus.data.materials.append(mat)

    # 3.5 ROTATION
    venus.rotation_euler = (0, 0, 0); venus.keyframe_insert(data_path="rotation_euler", frame=1)
    venus.rotation_euler = (0, 0, 1.57); venus.keyframe_insert(data_path="rotation_euler", frame=63)
    venus.rotation_euler = (0, 0, 3.14); venus.keyframe_insert(data_path="rotation_euler", frame=126)
    venus.rotation_euler = (0, 0, 4.71); venus.keyframe_insert(data_path="rotation_euler", frame=189)
    venus.rotation_euler = (0, 0, 6.28); venus.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING (Maintained from your final setup)
    # Key Light
    bpy.ops.object.light_add(type='POINT', location=(3, -5, 2))
    light_main = bpy.context.active_object; light_main.data.energy = 5000 
    
    # Rim Light (Kept position)
    bpy.ops.object.light_add(type='POINT', location=(-1.5, 2, -0.3))
    light_rim = bpy.context.active_object; light_rim.data.energy = 1000 
    
    # Fill Light (Kept energy 30)
    bpy.ops.object.light_add(type='POINT', location=(-2, -1, 0))
    light_fill = bpy.context.active_object; light_fill.data.energy = 30 

    # 5. CAMERA (Kept position)
    bpy.ops.object.camera_add(location=(0, -2.3, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64

setup_scene()