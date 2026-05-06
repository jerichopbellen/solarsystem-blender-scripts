import bpy
import math

# --- CONFIGURATION ---
MOON_RADIUS = 1.0  # Proportionate size
MOON_TEX_PATH = "C:/Users/jefbe/Downloads/solar system assets/8k_moon.jpg" 

def setup_scene():
    # 1. Clean Slate
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Create Moon (High Resolution + Subdivision)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=MOON_RADIUS)
    moon = bpy.context.active_object
    moon.name = "Moon"
    
    # Smooth edges for high-quality video
    subsurf = moon.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 3. Material (Making her shine)
    mat = bpy.data.materials.new(name="MoonMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled') 
    
    # Roughness at 0.8 for that dusty, lunar feel
    bsdf.inputs['Roughness'].default_value = 0.8 
    
    try:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(MOON_TEX_PATH)
        
        # HSV for the "Star" glow effect
        hsv = nodes.new('ShaderNodeHueSaturation')
        hsv.inputs['Saturation'].default_value = 1.8  # Extra pop
        hsv.inputs['Value'].default_value = 0.8       # Brighter surface
        
        links = mat.node_tree.links
        links.new(tex.outputs['Color'], hsv.inputs['Color'])
        links.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
        
        # Slight Emission to make it "shine"
        links.new(hsv.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 0.05 
    except:
        bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.7, 1) 
        
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    moon.data.materials.append(mat)

    # 3.5 ROTATION
    moon.rotation_euler = (0, 0, 0)
    moon.keyframe_insert(data_path="rotation_euler", frame=1)
    moon.rotation_euler[2] = math.radians(360)
    moon.keyframe_insert(data_path="rotation_euler", frame=250)

    # 4. LIGHTING (Intense Sun/Shadow Contrast)
    bpy.ops.object.light_add(type='POINT', location=(8, -12, 6))
    light_main = bpy.context.active_object; light_main.data.energy = 25000 
    
    # Rim Light to catch the crater edges
    bpy.ops.object.light_add(type='POINT', location=(-5, 6, 0.5))
    light_rim = bpy.context.active_object; light_rim.data.energy = 3000
    
    # Subtle Fill
    bpy.ops.object.light_add(type='POINT', location=(-6, -3, 0))
    light_fill = bpy.context.active_object; light_fill.data.energy = 200 

    # 5. CAMERA
    bpy.ops.object.camera_add(location=(0, -5, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

    # 6. RENDER & COLOR MANAGEMENT
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

setup_scene()