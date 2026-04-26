import bpy

# --- CONFIGURATION ---
SUN_RADIUS = 3.0
SUN_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_sun.jpg"

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Sun
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=SUN_RADIUS)
    sun = bpy.context.active_object
    sun.name = "Sun"
    bpy.ops.object.shade_smooth()

    # 3. Enhanced Material
    mat = bpy.data.materials.new(name="SunMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    tex = nodes.new('ShaderNodeTexImage')
    # Mix node to control the orange tint
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1.0 # Factor
    mix.inputs[1].default_value = (1.0, 0.3, 0.05, 1) # Deep Orange Tint
    
    try:
        tex.image = bpy.data.images.load(SUN_TEX_PATH)
    except:
        pass
    
    # Keep Strength low (1.0 - 2.0) so the texture doesn't blow out
    emit.inputs['Strength'].default_value = 1.5
    fcurve = emit.inputs['Strength'].driver_add('default_value')
    fcurve.driver.expression = "1.5 + sin(frame / 5) * 0.5" 
    
    # Linking: Texture -> Multiply (Orange Tint) -> Emission -> Surface
    links = mat.node_tree.links
    links.new(tex.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], emit.inputs['Color'])
    links.new(emit.outputs['Emission'], out.inputs['Surface'])
    sun.data.materials.append(mat)

    # 4. Light (Keep it separate from the surface emission)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
    light = bpy.context.active_object
    light.data.energy = 2000 # Lower energy = texture remains visible
    light.data.color = (1.0, 0.5, 0.1) # Light itself is orange

    # 5. Camera
    bpy.ops.object.camera_add(location=(0, -15, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. Render Settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128

setup_scene()