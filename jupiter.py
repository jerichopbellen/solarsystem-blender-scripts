import bpy

# --- CONFIGURATION ---
JUPITER_RADIUS = 3.5 
JUPITER_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_jupiter.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Jupiter
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=JUPITER_RADIUS)
    jupiter = bpy.context.active_object
    jupiter.name = "Jupiter"
    bpy.ops.object.shade_smooth()

    # 3. Material
    mat = bpy.data.materials.new(name="JupiterMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    
    bsdf.inputs['Roughness'].default_value = 0.8 
    bsdf.inputs['Base Color'].default_value = (0.8, 0.7, 0.5, 1) 
    
    try:
        tex.image = bpy.data.images.load(JUPITER_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        pass 
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    jupiter.data.materials.append(mat)

    # 3.5 ROTATION
    jupiter.rotation_euler = (0, 0, 0); jupiter.keyframe_insert(data_path="rotation_euler", frame=1)
    jupiter.rotation_euler = (0, 0, 1.57); jupiter.keyframe_insert(data_path="rotation_euler", frame=63)
    jupiter.rotation_euler = (0, 0, 3.14); jupiter.keyframe_insert(data_path="rotation_euler", frame=126)
    jupiter.rotation_euler = (0, 0, 4.71); jupiter.keyframe_insert(data_path="rotation_euler", frame=189)
    jupiter.rotation_euler = (0, 0, 6.28); jupiter.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING
    # Key Light
    bpy.ops.object.light_add(type='POINT', location=(12, -18, 8))
    light_main = bpy.context.active_object; light_main.data.energy = 35000 
    
    # Rim Light (Optimized for Camera Visibility)
    # Moved X inward to -6 and Y to 8 to catch the rim more sharply from the camera's POV
    bpy.ops.object.light_add(type='POINT', location=(-7, 8, 0.5))
    light_rim = bpy.context.active_object
    light_rim.name = "RimLight"
    light_rim.data.energy = 150000 
    
    # Fill Light (Weakened for contrast)
    bpy.ops.object.light_add(type='POINT', location=(-10, -5, 0))
    light_fill = bpy.context.active_object
    light_fill.data.energy = 400 

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -12, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64

setup_scene()