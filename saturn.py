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

    # 2. Create Saturn (High Resolution + Subdivision)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=SATURN_RADIUS)
    saturn = bpy.context.active_object
    saturn.name = "SaturnBody"
    
    # Add Subdivision Surface to ensure the planet edge is perfectly round in video
    subsurf = saturn.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 3. Create Saturn's Rings (Donut Flat - Your Method with 512 vertices)
    # 512 vertices ensures the ring doesn't look like a polygon in the render
    bpy.ops.mesh.primitive_circle_add(vertices=512, radius=RING_OUTER_RADIUS, fill_type='NGON')
    rings = bpy.context.active_object
    rings.name = "SaturnRings"
    
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.inset(thickness=(RING_OUTER_RADIUS - RING_INNER_RADIUS))
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.editmode_toggle()
    
    # Shade smooth the ring surface
    bpy.ops.object.shade_smooth()
    
    rings.parent = saturn

    # 4. Materials
    s_mat = bpy.data.materials.new(name="SaturnMat")
    s_mat.use_nodes = True
    try:
        s_tex = s_mat.node_tree.nodes.new('ShaderNodeTexImage')
        s_tex.image = bpy.data.images.load(SATURN_TEX_PATH)
        s_bsdf = s_mat.node_tree.nodes["Principled BSDF"]
        s_mat.node_tree.links.new(s_tex.outputs['Color'], s_bsdf.inputs['Base Color'])
    except: pass
    saturn.data.materials.append(s_mat)

    # Ring Material (Radial Mapping)
    r_mat = bpy.data.materials.new(name="RingMat")
    r_mat.use_nodes = True
    r_mat.blend_method = 'HASHED'
    nodes = r_mat.node_tree.nodes
    links = r_mat.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_tex = nodes.new('ShaderNodeTexImage')
    node_coord = nodes.new('ShaderNodeTexCoord')
    node_sep = nodes.new('ShaderNodeSeparateXYZ')
    node_math_x = nodes.new('ShaderNodeMath'); node_math_x.operation = 'POWER'; node_math_x.inputs[1].default_value = 2
    node_math_y = nodes.new('ShaderNodeMath'); node_math_y.operation = 'POWER'; node_math_y.inputs[1].default_value = 2
    node_add = nodes.new('ShaderNodeMath'); node_add.operation = 'ADD'
    node_sqrt = nodes.new('ShaderNodeMath'); node_sqrt.operation = 'SQRT'
    node_map = nodes.new('ShaderNodeMapRange')
    node_map.inputs[1].default_value = RING_INNER_RADIUS 
    node_map.inputs[2].default_value = RING_OUTER_RADIUS 
    node_vec = nodes.new('ShaderNodeCombineXYZ')

    try:
        node_tex.image = bpy.data.images.load(RING_TEX_PATH)
        links.new(node_coord.outputs['Object'], node_sep.inputs['Vector'])
        links.new(node_sep.outputs['X'], node_math_x.inputs[0])
        links.new(node_sep.outputs['Y'], node_math_y.inputs[0])
        links.new(node_math_x.outputs['Value'], node_add.inputs[0])
        links.new(node_math_y.outputs['Value'], node_add.inputs[1])
        links.new(node_add.outputs['Value'], node_sqrt.inputs[0])
        links.new(node_sqrt.outputs['Value'], node_map.inputs[0])
        links.new(node_map.outputs['Result'], node_vec.inputs[0])
        links.new(node_vec.outputs['Vector'], node_tex.inputs['Vector'])
        
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Emission Color'])
        node_bsdf.inputs['Emission Strength'].default_value = 0.1 
        
        m_solid = nodes.new('ShaderNodeMath')
        m_solid.operation = 'MULTIPLY'; m_solid.inputs[1].default_value = 3.0
        links.new(node_tex.outputs['Alpha'], m_solid.inputs[0])
        links.new(m_solid.outputs['Value'], node_bsdf.inputs['Alpha'])
    except: pass

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    rings.data.materials.append(r_mat)

    # 5. ANIMATION
    saturn.rotation_euler = (0, 0, 0)
    saturn.keyframe_insert(data_path="rotation_euler", frame=1)
    saturn.rotation_euler = (0, 0, math.radians(360))
    saturn.keyframe_insert(data_path="rotation_euler", frame=250)

    # 6. LIGHTING (BLENDER 5.1 COMPATIBLE)
    # Main Sun
    bpy.ops.object.light_add(type='POINT', location=(12, -18, 8))
    bpy.context.active_object.data.energy = 30000 
    
    # Rim Light
    bpy.ops.object.light_add(type='POINT', location=(-7, 8, 0.5))
    bpy.context.active_object.data.energy = 1000
    
    # Fill Light (Side)
    bpy.ops.object.light_add(type='POINT', location=(-10, -5, 0))
    bpy.context.active_object.data.energy = 400 

    # Bottom Fill
    bpy.ops.object.light_add(type='POINT', location=(0, -5, -8))
    bottom_light = bpy.context.active_object
    bottom_light.name = "BottomFill"
    bottom_light.data.energy = 500
    # Specular fix for 5.1
    bottom_light.data.specular_factor = 0.0 

    # 7. CAMERA
    bpy.ops.object.camera_add(location=(0, -22, 4), rotation=(1.4, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 8. RENDER SETTINGS
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 512
    bpy.context.scene.cycles.filter_width = 2.0  
    # Critical for video quality
    bpy.context.scene.render.use_motion_blur = True
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'
    
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

setup_scene()