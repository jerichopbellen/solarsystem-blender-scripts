import bpy

# --- CONFIGURATION ---
SUN_RADIUS = 3.0
SUN_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_sun.jpg"

def setup_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 1. Create Sun
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=SUN_RADIUS)
    sun = bpy.context.active_object
    sun.name = "Sun"
    bpy.ops.object.shade_smooth()

    # 2. Material
    mat = bpy.data.materials.new(name="SolarSun")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    tex_image = nodes.new('ShaderNodeTexImage')
    noise = nodes.new('ShaderNodeTexNoise')
    
    # Load texture
    try:
        tex_image.image = bpy.data.images.load(SUN_TEX_PATH)
    except: pass
    
    # Subtle boiling movement
    noise.noise_dimensions = '4D'
    noise.inputs['Scale'].default_value = 10.0
    driver = noise.inputs['W'].driver_add('default_value')
    driver.driver.expression = "frame / 100.0"
    
    # MIX node: 1=Texture, 2=Orange Tinted Noise
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.5
    mix.inputs[2].default_value = (1.0, 0.4, 0.1, 1.0) # Deep Orange Tint
    
    # Lower strength to stop the "white" washout
    emit.inputs['Strength'].default_value = 2.0
    
    links = mat.node_tree.links
    links.new(tex_image.outputs['Color'], mix.inputs[1])
    links.new(noise.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], emit.inputs['Color'])
    links.new(emit.outputs['Emission'], out.inputs['Surface'])
    sun.data.materials.append(mat)

    # 3. Camera & Render
    bpy.ops.object.camera_add(location=(0, -15, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.context.scene.render.engine = 'CYCLES'

setup_scene()