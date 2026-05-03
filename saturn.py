import bpy
import math

# --- CONFIGURATION ---
SATURN_RADIUS = 3.0 
RING_INNER_RADIUS = 4.2
RING_OUTER_RADIUS = 7.5
SATURN_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_saturn.jpg" 
RING_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_saturn_ring_alpha.png" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Saturn (High Res)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=SATURN_RADIUS)
    saturn = bpy.context.active_object
    saturn.name = "SaturnBody"
    subsurf = saturn.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 3. Create Saturn's Rings (512 vertices)
    bpy.ops.mesh.primitive_circle_add(vertices=512, radius=RING_OUTER_RADIUS, fill_type='NGON')
    rings = bpy.context.active_object
    rings.name = "SaturnRings"
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.inset(thickness=(RING_OUTER_RADIUS - RING_INNER_RADIUS))
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.shade_smooth()
    rings.parent = saturn

    # 4. Materials
    # --- SATURN MATERIAL ---
    s_mat = bpy.data.materials.new(name="SaturnMat")
    s_mat.use_nodes = True
    s_nodes = s_mat.node_tree.nodes
    s_links = s_mat.node_tree.links
    s_nodes.clear()
    s_out = s_nodes.new('ShaderNodeOutputMaterial')
    s_bsdf = s_nodes.new('ShaderNodeBsdfPrincipled')
    s_bsdf.inputs['Roughness'].default_value = 0.8
    try:
        s_tex = s_nodes.new('ShaderNodeTexImage')
        s_tex.image = bpy.data.images.load(SATURN_TEX_PATH)
        s_hsv = s_nodes.new('ShaderNodeHueSaturation')
        s_hsv.inputs['Saturation'].default_value = 1.8
        s_hsv.inputs['Value'].default_value = 0.7
        s_links.new(s_tex.outputs['Color'], s_hsv.inputs['Color'])
        s_links.new(s_hsv.outputs['Color'], s_bsdf.inputs['Base Color'])
    except: pass
    s_links.new(s_bsdf.outputs['BSDF'], s_out.inputs['Surface'])
    saturn.data.materials.append(s_mat)

    # --- RING MATERIAL (WITH SATURATION PUSH) ---
    r_mat = bpy.data.materials.new(name="RingMat")
    r_mat.use_nodes = True
    r_mat.blend_method = 'HASHED'
    r_nodes = r_mat.node_tree.nodes
    r_links = r_mat.node_tree.links
    r_nodes.clear()

    r_out = r_nodes.new('ShaderNodeOutputMaterial')
    r_bsdf = r_nodes.new('ShaderNodeBsdfPrincipled')
    r_bsdf.inputs['Roughness'].default_value = 0.8 # Applied Roughness
    
    # Texture/Mapping Nodes
    r_tex = r_nodes.new('ShaderNodeTexImage')
    r_coord = r_nodes.new('ShaderNodeTexCoord')
    r_sep = r_nodes.new('ShaderNodeSeparateXYZ')
    r_math_x = r_nodes.new('ShaderNodeMath'); r_math_x.operation = 'POWER'; r_math_x.inputs[1].default_value = 2
    r_math_y = r_nodes.new('ShaderNodeMath'); r_math_y.operation = 'POWER'; r_math_y.inputs[1].default_value = 2
    r_add = r_nodes.new('ShaderNodeMath'); r_add.operation = 'ADD'
    r_sqrt = r_nodes.new('ShaderNodeMath'); r_sqrt.operation = 'SQRT'
    r_map = r_nodes.new('ShaderNodeMapRange')
    r_map.inputs[1].default_value = RING_INNER_RADIUS 
    r_map.inputs[2].default_value = RING_OUTER_RADIUS 
    r_vec = r_nodes.new('ShaderNodeCombineXYZ')

    # NEW: HSV Node for the Rings
    r_hsv = r_nodes.new('ShaderNodeHueSaturation')
    r_hsv.inputs['Saturation'].default_value = 1.6
    r_hsv.inputs['Value'].default_value = 0.7

    try:
        r_tex.image = bpy.data.images.load(RING_TEX_PATH)
        r_links.new(r_coord.outputs['Object'], r_sep.inputs['Vector'])
        r_links.new(r_sep.outputs['X'], r_math_x.inputs[0])
        r_links.new(r_sep.outputs['Y'], r_math_y.inputs[0])
        r_links.new(r_math_x.outputs['Value'], r_add.inputs[0])
        r_links.new(r_math_y.outputs['Value'], r_add.inputs[1])
        r_links.new(r_add.outputs['Value'], r_sqrt.inputs[0])
        r_links.new(r_sqrt.outputs['Value'], r_map.inputs[0])
        r_links.new(r_map.outputs['Result'], r_vec.inputs[0])
        r_links.new(r_vec.outputs['Vector'], r_tex.inputs['Vector'])
        
        # Connect through HSV
        r_links.new(r_tex.outputs['Color'], r_hsv.inputs['Color'])
        r_links.new(r_hsv.outputs['Color'], r_bsdf.inputs['Base Color'])
        r_links.new(r_hsv.outputs['Color'], r_bsdf.inputs['Emission Color'])
        r_bsdf.inputs['Emission Strength'].default_value = 0.1 
        
        # Alpha logic
        m_alpha = r_nodes.new('ShaderNodeMath')
        m_alpha.operation = 'MULTIPLY'; m_alpha.inputs[1].default_value = 3.0
        r_links.new(r_tex.outputs['Alpha'], m_alpha.inputs[0])
        r_links.new(m_alpha.outputs['Value'], r_bsdf.inputs['Alpha'])
    except: pass

    r_links.new(r_bsdf.outputs['BSDF'], r_out.inputs['Surface'])
    rings.data.materials.append(r_mat)

    # 5. Animation
    saturn.rotation_euler = (0, 0, 0)
    saturn.keyframe_insert(data_path="rotation_euler", frame=1)
    saturn.rotation_euler = (0, 0, math.radians(360))
    saturn.keyframe_insert(data_path="rotation_euler", frame=250)

    # 6. Lighting
    bpy.ops.object.light_add(type='POINT', location=(12, -18, 8))
    bpy.context.active_object.data.energy = 75000 
    bpy.ops.object.light_add(type='POINT', location=(-7, 8, 0.5))
    bpy.context.active_object.data.energy = 6000
    bpy.ops.object.light_add(type='POINT', location=(-10, -5, 0))
    bpy.context.active_object.data.energy = 400 
    bpy.ops.object.light_add(type='POINT', location=(0, -5, -8))
    bottom = bpy.context.active_object
    bottom.data.energy = 500
    bottom.data.specular_factor = 0.0 

    # 7. Camera & Render
    bpy.ops.object.camera_add(location=(0, -22, 4), rotation=(1.4, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 512
    bpy.context.scene.render.use_motion_blur = True
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

setup_scene()