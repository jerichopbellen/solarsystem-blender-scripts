import bpy

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

    # 2. Create Saturn
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=SATURN_RADIUS)
    saturn = bpy.context.active_object
    saturn.name = "SaturnBody"
    bpy.ops.object.shade_smooth()

    # 3. Create Saturn's Rings (The Belt)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    rings = bpy.context.active_object
    rings.name = "SaturnRings"
    
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(RING_OUTER_RADIUS - RING_INNER_RADIUS, 1, 1))
    bpy.ops.transform.translate(value=((RING_INNER_RADIUS + RING_OUTER_RADIUS) / 2, 0, 0))
    bpy.ops.object.editmode_toggle()

    screw = rings.modifiers.new(name="RingScrew", type='SCREW')
    screw.angle = 6.28319 
    screw.steps = 128
    
    rings.parent = saturn

    # 4. Materials
    # Saturn Material
    s_mat = bpy.data.materials.new(name="SaturnMat")
    s_mat.use_nodes = True
    try:
        s_tex = s_mat.node_tree.nodes.new('ShaderNodeTexImage')
        s_tex.image = bpy.data.images.load(SATURN_TEX_PATH)
        s_bsdf = s_mat.node_tree.nodes["Principled BSDF"]
        s_mat.node_tree.links.new(s_tex.outputs['Color'], s_bsdf.inputs['Base Color'])
    except: pass
    saturn.data.materials.append(s_mat)

    # Ring Material
    r_mat = bpy.data.materials.new(name="RingMat")
    r_mat.use_nodes = True
    r_mat.blend_method = 'HASHED'
    nodes = r_mat.node_tree.nodes
    links = r_mat.node_tree.links
    bsdf = nodes["Principled BSDF"]

    try:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(RING_TEX_PATH)
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 0.15 
        
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.05 
        links.new(tex.outputs['Alpha'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Alpha'])
    except: pass
    rings.data.materials.append(r_mat)

    # 5. ANIMATION (Horizontal Spin)
    saturn.rotation_euler = (0, 0, 0)
    saturn.keyframe_insert(data_path="rotation_euler", frame=1)
    saturn.rotation_euler = (0, 0, 6.28319)
    saturn.keyframe_insert(data_path="rotation_euler", frame=250)

    # 6. LIGHTING (Synced to Jupiter Setup)
    # Key Light
    bpy.ops.object.light_add(type='POINT', location=(12, -18, 8))
    light_main = bpy.context.active_object
    light_main.data.energy = 35000 
    
    # Rim Light (Powerful highlight)
    bpy.ops.object.light_add(type='POINT', location=(-7, 8, 0.5))
    light_rim = bpy.context.active_object
    light_rim.name = "RimLight"
    light_rim.data.energy = 8000
    
    # Fill Light (Low contrast)
    bpy.ops.object.light_add(type='POINT', location=(-10, -5, 0))
    light_fill = bpy.context.active_object
    light_fill.data.energy = 400 

    # 7. CAMERA (Your Z=4 preference)
    bpy.ops.object.camera_add(location=(0, -22, 4), rotation=(1.4, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 8. RENDER
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64

setup_scene()