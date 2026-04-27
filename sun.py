import bpy
import random

# --- CONFIGURATION ---
SUN_RADIUS = 3.0
SUN_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_sun.jpg"

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Sun
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=SUN_RADIUS)
    sun = bpy.context.active_object
    sun.name = "Sun"
    bpy.ops.object.shade_smooth()
    
    # 2.5 Boiling Plasma (Displacement)
    mod_disp = sun.modifiers.new(name="Boil", type='DISPLACE')
    tex_noise = bpy.data.textures.new("Plasma", type='VORONOI')
    tex_noise.noise_scale = 0.2
    mod_disp.texture = tex_noise
    mod_disp.strength = 0.1
    driver = mod_disp.driver_add("mid_level")
    driver.driver.expression = "frame / 100.0"

    # 3. Material (Principled BSDF + SSS for "Hot" Volume)
    mat = bpy.data.materials.new(name="SunMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = nodes.new('ShaderNodeTexImage')
    
    # Realistic Sun Material Settings
    bsdf.inputs['Emission Strength'].default_value = 2.0
    bsdf.inputs['Subsurface Weight'].default_value = 0.5 # Adds glowing depth
    bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1) # Red/Orange scatter
    bsdf.inputs['Roughness'].default_value = 0.8
    
    try:
        tex.image = bpy.data.images.load(SUN_TEX_PATH)
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
    except: pass 
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    sun.data.materials.append(mat)

    # 3.5 SOLAR FLARES
    bpy.context.view_layer.objects.active = sun
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.1)
    flare_obj = bpy.context.active_object
    flare_obj.hide_viewport = True; flare_obj.hide_render = True
    
    bpy.context.view_layer.objects.active = sun
    bpy.ops.object.particle_system_add()
    psys = sun.particle_systems[0]
    psys.settings.render_type = 'OBJECT'
    psys.settings.instance_object = flare_obj
    psys.settings.count = 500
    psys.settings.lifetime = 30
    psys.settings.normal_factor = 0.8
    psys.settings.brownian_factor = 0.1

    # 4. LIGHTING
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
    light = bpy.context.active_object; light.data.energy = 60000
    light.data.color = (1.0, 0.5, 0.2) # Deep "Hot" Orange

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -15, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128

setup_scene()