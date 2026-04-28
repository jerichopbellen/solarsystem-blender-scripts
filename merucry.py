import bpy

# --- CONFIGURATION ---
MERCURY_RADIUS = 0.8 
MERCURY_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_mercury.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Mercury
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=MERCURY_RADIUS)
    mercury = bpy.context.active_object
    mercury.name = "Mercury"
    bpy.ops.object.shade_smooth()

    # 3. Material
    mat = bpy.data.materials.new(name="MercuryMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    bsdf.inputs['Roughness'].default_value = 0.9 
    try:
        tex.image = bpy.data.images.load(MERCURY_TEX_PATH)
    except:
        bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1)
    links = mat.node_tree.links
    links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mercury.data.materials.append(mat)

    # 3.5 ROTATION
    mercury.rotation_euler = (0, 0, 0); mercury.keyframe_insert(data_path="rotation_euler", frame=1)
    mercury.rotation_euler = (0, 0, 1.57); mercury.keyframe_insert(data_path="rotation_euler", frame=63)
    mercury.rotation_euler = (0, 0, 3.14); mercury.keyframe_insert(data_path="rotation_euler", frame=126)
    mercury.rotation_euler = (0, 0, 4.71); mercury.keyframe_insert(data_path="rotation_euler", frame=189)
    mercury.rotation_euler = (0, 0, 6.28); mercury.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING SETUP
    # Key Light (Main Intensity)
    bpy.ops.object.light_add(type='POINT', location=(3, -5, 2))
    light_main = bpy.context.active_object; light_main.data.energy = 5000 
    
    # Rim Light (Edge definition)
    bpy.ops.object.light_add(type='POINT', location=(-1.5, 2, -0.3))
    light_rim = bpy.context.active_object; light_rim.data.energy = 1000 
    
    # Fill Light (Texture visibility in shadow)
    bpy.ops.object.light_add(type='POINT', location=(-2, -1, 0))
    light_fill = bpy.context.active_object; light_fill.data.energy = 30 

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -2.3, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128

setup_scene()