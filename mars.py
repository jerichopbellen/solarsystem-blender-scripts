import bpy

# --- CONFIGURATION ---
# Mars radius is slightly smaller than Venus
MARS_RADIUS = 0.53 
# Update this path to your Mars texture
MARS_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_mars.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Mars
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=MARS_RADIUS)
    mars = bpy.context.active_object
    mars.name = "Mars"
    bpy.ops.object.shade_smooth()

    # 3. Material (Optimized for Mars's rocky, dusty surface)
    mat = bpy.data.materials.new(name="MarsMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    
    # Mars is more matte and rougher than Venus
    bsdf.inputs['Roughness'].default_value = 0.8 
    # Rust-red base color
    bsdf.inputs['Base Color'].default_value = (0.6, 0.3, 0.2, 1) 
    
    try:
        tex.image = bpy.data.images.load(MARS_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        pass # Fallback to red base color if texture is missing
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mars.data.materials.append(mat)

    # 3.5 ROTATION
    mars.rotation_euler = (0, 0, 0); mars.keyframe_insert(data_path="rotation_euler", frame=1)
    mars.rotation_euler = (0, 0, 1.57); mars.keyframe_insert(data_path="rotation_euler", frame=63)
    mars.rotation_euler = (0, 0, 3.14); mars.keyframe_insert(data_path="rotation_euler", frame=126)
    mars.rotation_euler = (0, 0, 4.71); mars.keyframe_insert(data_path="rotation_euler", frame=189)
    mars.rotation_euler = (0, 0, 6.28); mars.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING
    bpy.ops.object.light_add(type='POINT', location=(3, -5, 2))
    light_main = bpy.context.active_object; light_main.data.energy = 5000 
    
    bpy.ops.object.light_add(type='POINT', location=(-1.5, 2, -0.3))
    light_rim = bpy.context.active_object; light_rim.data.energy = 1000 
    
    bpy.ops.object.light_add(type='POINT', location=(-2, -1, 0))
    light_fill = bpy.context.active_object; light_fill.data.energy = 30 

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -2.3, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64

setup_scene()