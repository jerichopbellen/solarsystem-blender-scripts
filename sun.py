import bpy
import math

# --- CONFIGURATION ---
SUN_RADIUS = 3.0
SUN_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_sun.jpg"

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Sun (High Res + Subsurf for perfect roundness)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=SUN_RADIUS)
    sun = bpy.context.active_object
    sun.name = "Sun"
    
    subsurf = sun.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 3. Material (With HSV Saturation Push and Value Control)
    mat = bpy.data.materials.new(name="SolarSun")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') # Switching to Principled for Roughness control
    tex_image = nodes.new('ShaderNodeTexImage')
    noise = nodes.new('ShaderNodeTexNoise')
    hsv = nodes.new('ShaderNodeHueSaturation')
    
    # Applied your requested Roughness
    bsdf.inputs['Roughness'].default_value = 0.8
    
    # Load texture
    try:
        tex_image.image = bpy.data.images.load(SUN_TEX_PATH)
    except: pass
    
    # Applied your requested HSV tweaks
    hsv.inputs['Saturation'].default_value = 1.8  # Strong color push
    hsv.inputs['Value'].default_value = 0.7       # Stops white-out
    
    # Subtle boiling movement (Noise W-driver)
    noise.noise_dimensions = '4D'
    noise.inputs['Scale'].default_value = 10.0
    driver = noise.inputs['W'].driver_add('default_value')
    driver.driver.expression = "frame / 100.0"
    
    # Mix texture with noise
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.5
    
    links = mat.node_tree.links
    # Path: Texture -> HSV -> Mix -> BSDF
    links.new(tex_image.outputs['Color'], hsv.inputs['Color'])
    links.new(hsv.outputs['Color'], mix.inputs[1])
    links.new(noise.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Set Emission so the sun actually glows
    links.new(mix.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 2.0
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    sun.data.materials.append(mat)

    # 4. AXIAL ROTATION (Modeling/Animation Purposes)
    sun.rotation_euler = (0, 0, 0)
    sun.keyframe_insert(data_path="rotation_euler", frame=1)
    # Rotating 360 degrees over the timeline
    sun.rotation_euler = (0, 0, math.radians(360))
    sun.keyframe_insert(data_path="rotation_euler", frame=250)

    # 5. Camera & Render Settings
    bpy.ops.object.camera_add(location=(0, -15, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

setup_scene()