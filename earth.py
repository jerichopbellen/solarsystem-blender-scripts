import bpy

# --- CONFIGURATION ---
EARTH_RADIUS = 0.75 
EARTH_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_earth_daymap.jpg"

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Earth
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=EARTH_RADIUS)
    earth = bpy.context.active_object
    earth.name = "Earth"
    bpy.ops.object.shade_smooth()

    # 3. Material (Deep blue + Bump waves)
    mat = bpy.data.materials.new(name="EarthMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    tex = nodes.new('ShaderNodeTexImage')
    
    # Wave Texture for subtle movement
    wave = nodes.new('ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = 50.0
    wave.inputs['Distortion'].default_value = 2.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.1
    
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['B'].default_value = (0.05, 0.1, 0.25, 1.0)
    mix.inputs['Factor'].default_value = 0.6
    
    bsdf.inputs['Roughness'].default_value = 0.1
    
    try:
        tex.image = bpy.data.images.load(EARTH_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], mix.inputs['A'])
        links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
        links.new(wave.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    except:
        pass 
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    earth.data.materials.append(mat)

    # 4. LINEAR ROTATION
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    earth.rotation_euler = (0, 0, 0); earth.keyframe_insert(data_path="rotation_euler", frame=1)
    earth.rotation_euler = (0, 0, 6.28); earth.keyframe_insert(data_path="rotation_euler", frame=250)
    
    # 5. WAVE ANIMATION
    driver = wave.inputs[1].driver_add('default_value')
    driver.driver.expression = "frame / 25.0"

    # 6. LIGHTING (The 3-point setup)
    # Key Light
    bpy.ops.object.light_add(type='POINT', location=(3, -5, 2))
    bpy.context.active_object.data.energy = 5000 
    
    # Rim Light
    bpy.ops.object.light_add(type='POINT', location=(-1.5, 2, -0.3))
    bpy.context.active_object.data.energy = 1000 
    
    # Fill Light (Brings out detail in the shaded region)
    bpy.ops.object.light_add(type='POINT', location=(-2, -1, 0))
    bpy.context.active_object.data.energy = 30 

    # 7. CAMERA & RENDER
    bpy.ops.object.camera_add(location=(0, -2.3, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64

setup_scene()