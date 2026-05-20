import bpy
import math
import os
import random

# PRESERVED VISUAL MATRIX
bodies = [
    {"name": "Sun",     "filename": "sun.blend",     "orbit_radius": 0.0,  "period": 1,     "radius": 12.0, "tilt": 0.0,   "rot_period": 0.0},  
    {"name": "Mercury", "filename": "mercury.blend", "orbit_radius": 18.0, "period": 88,    "radius": 0.8,  "tilt": 0.03,  "rot_period": 58.6},
    {"name": "Venus",   "filename": "venus.blend",   "orbit_radius": 24.0, "period": 225,   "radius": 1.3,  "tilt": 177.3, "rot_period": -243.0},
    {"name": "Earth",   "filename": "earth.blend",   "orbit_radius": 31.0, "period": 600,   "radius": 1.5,  "tilt": 23.44, "rot_period": 3.5},  
    {"name": "Moon",    "filename": "moon.blend",    "orbit_radius": 3.8,  "period": 380,   "radius": 0.4,  "tilt": 6.68,  "rot_period": 27.3}, 
    {"name": "Mars",    "filename": "mars.blend",    "orbit_radius": 38.0, "period": 687,   "radius": 1.0,  "tilt": 25.19, "rot_period": 8.5},   
    {"name": "Jupiter", "filename": "jupiter.blend", "orbit_radius": 52.0, "period": 4333,  "radius": 4.5,  "tilt": 3.13,  "rot_period": 4.1},
    {"name": "Saturn",  "filename": "saturn.blend",  "orbit_radius": 68.0, "period": 10759, "radius": 3.8,  "tilt": 26.73, "rot_period": 4.4},
    {"name": "Uranus",  "filename": "uranus.blend",  "orbit_radius": 82.0, "period": 30687, "radius": 2.4,  "tilt": 97.77, "rot_period": -7.2},
    {"name": "Neptune", "filename": "neptune.blend", "orbit_radius": 95.0, "period": 60190, "radius": 2.2,  "tilt": 28.32, "rot_period": 6.7},
    {"name": "Pluto",   "filename": "pluto.blend",   "orbit_radius": 106.0,"period": 90560, "radius": 0.6,  "tilt": 122.5, "rot_period": -6.39},
]

base_dir = r"C:\solarsystem blender files"
start_frame = 1
frames_per_body = 120 
showcase_total_frames = len(bodies) * frames_per_body 
outro_duration = 1440 
total_frames = showcase_total_frames + outro_duration 

bpy.context.scene.frame_start = start_frame
bpy.context.scene.frame_end = total_frames

random.seed(42)
for b in bodies:
    b["start_offset"] = random.uniform(0, 2 * math.pi)

def clear_scene():
    print("Clearing scene...")
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for block in [bpy.data.meshes, bpy.data.curves, bpy.data.actions, bpy.data.materials, bpy.data.lights, bpy.data.cameras]:
        for item in list(block):
            if item.users == 0: block.remove(item)

def setup_space_lighting():
    print("Deploying directional studio lighting and ambient protection lines...")
    light_data = bpy.data.lights.new(name="Sun_Core_Light", type='POINT')
    light_data.energy = 1600000.0  
    light_data.shadow_soft_size = 3.0
    sun_light = bpy.data.objects.new(name="Sun_Core_Light", object_data=light_data)
    bpy.context.scene.collection.objects.link(sun_light)
    sun_light.location = (0, 0, 0)
    
    fill_sun_data = bpy.data.lights.new(name="Overhead_Fill", type='SUN')
    fill_sun_data.energy = 4.2  
    fill_sun = bpy.data.objects.new(name="Overhead_Fill", object_data=fill_sun_data)
    bpy.context.scene.collection.objects.link(fill_sun)
    fill_sun.rotation_euler = (math.radians(35), math.radians(15), math.radians(45))
    
    bounce_sun_data = bpy.data.lights.new(name="Under_Fill", type='SUN')
    bounce_sun_data.energy = 1.8
    bounce_sun = bpy.data.objects.new(name="Under_Fill", object_data=bounce_sun_data)
    bpy.context.scene.collection.objects.link(bounce_sun)
    bounce_sun.rotation_euler = (math.radians(-145), 0, math.radians(15))

    amb_angles = [0, 120, 240]
    for i, angle in enumerate(amb_angles):
        rad = math.radians(angle)
        amb_data = bpy.data.lights.new(name=f"Ambient_Zone_Glow_{i}", type='SUN')
        amb_data.energy = 0.35 
        amb_data.use_shadow = False
        amb_light = bpy.data.objects.new(name=f"Ambient_Zone_Glow_{i}", object_data=amb_data)
        bpy.context.scene.collection.objects.link(amb_light)
        amb_light.rotation_euler = (math.radians(20), math.radians(40), rad)

    if bpy.context.scene.world:
        bpy.context.scene.world.use_nodes = False
        bpy.context.scene.world.color = (0.002, 0.002, 0.004)

def create_background_environment():
    print("Deploying isolated distant background elements...")
    star_mat = bpy.data.materials.new(name="Star_Emission_Mat")
    star_mat.use_nodes = True
    
    nodes = star_mat.node_tree.nodes
    nodes.clear()
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    emit_node = nodes.new(type='ShaderNodeEmission')
    emit_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    emit_node.inputs['Strength'].default_value = 2.0 
    star_mat.node_tree.links.new(emit_node.outputs['Emission'], out_node.inputs['Surface'])
    
    # Generate background star field matrix
    for _ in range(1200):
        dist = random.uniform(350, 600) 
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        x = dist * math.sin(phi) * math.cos(theta)
        y = dist * math.sin(phi) * math.sin(theta)
        z = dist * math.cos(phi)
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.12, 0.28), location=(x, y, z))
        star_part = bpy.context.active_object
        star_part.name = "Background_Star"
        star_part.data.materials.append(star_mat)
        
        # FIXED: Object-level shadow suppression (Perfect for Blender 4.2+)
        star_part.visible_shadow = False
        star_part.select_set(False)

    # Generate distant background shooting stars
    for s in range(5):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=25.0, location=(random.uniform(-150, 150), random.uniform(380, 500), random.uniform(-60, 90)))
        s_star = bpy.context.active_object
        s_star.name = f"Distant_Shooting_Star_{s}"
        s_star.rotation_euler = (math.radians(random.uniform(20, 40)), math.radians(random.uniform(10, 25)), 0)
        s_star.data.materials.append(star_mat)
        s_star.visible_shadow = False
        
        s_start = random.randint(150, total_frames - 350)
        s_star.location.x -= 60
        s_star.keyframe_insert(data_path="location", frame=s_start)
        s_star.location.x += 180
        s_star.location.y -= 80
        s_star.keyframe_insert(data_path="location", frame=s_start + 35)

def append_collection(filepath, collection_name):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        if collection_name in data_from.collections:
            data_to.collections = [collection_name]
        elif len(data_from.collections) > 0:
            data_to.collections = [data_from.collections[0]]
        else:
            return None
    coll = data_to.collections[0]
    if coll and coll.name not in bpy.context.scene.collection.children.keys():
        bpy.context.scene.collection.children.link(coll)
    return coll

def create_orbit_line(radius, name):
    if radius == 0.0: return
    bpy.ops.mesh.primitive_circle_add(vertices=128, radius=radius, location=(0,0,0))
    ring = bpy.context.active_object
    ring.name = f"{name}_Orbit_Track"
    bpy.ops.object.convert(target='CURVE')
    ring.data.bevel_depth = 0.005 

def normalize_and_scale_object(obj, target_radius):
    obj.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()
    max_dim = max(obj.dimensions)
    if max_dim > 0:
        scale_factor = (target_radius * 2.0) / max_dim
        obj.scale = (scale_factor, scale_factor, scale_factor)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# --- Scene Setup ---
clear_scene()
setup_space_lighting()
create_background_environment()

planet_objects = {}

for body in bodies:
    blend_path = os.path.join(base_dir, body["filename"])
    coll = append_collection(blend_path, body["name"])
    if not coll: continue

    planet_obj = None
    
    for obj in coll.objects:
        if obj.name.lower() == body["name"].lower():
            planet_obj = obj
            break
    if not planet_obj:
        valid_meshes = [o for o in coll.objects if o.type == 'MESH' and o.dimensions.x > 0.05]
        if valid_meshes:
            planet_obj = max(valid_meshes, key=lambda o: o.dimensions.x)
                
    if planet_obj:
        planet_objects[body["name"]] = planet_obj
        
        # Clean collection imports
        for extra_obj in list(coll.objects):
            if extra_obj != planet_obj:
                if extra_obj.type in {'LIGHT', 'CAMERA'}:
                    bpy.data.objects.remove(extra_obj, do_unlink=True)
                elif body["name"] == "Saturn" and extra_obj.type == 'MESH':
                    if "ring" not in extra_obj.name.lower():
                        bpy.data.objects.remove(extra_obj, do_unlink=True)

        bpy.ops.object.select_all(action='DESELECT')
        planet_obj.select_set(True)
        bpy.context.view_layer.objects.active = planet_obj
        normalize_and_scale_object(planet_obj, body["radius"])
        if body["name"] != "Sun":
            create_orbit_line(body["orbit_radius"], body["name"])

if "Moon" in planet_objects and "Earth" in planet_objects:
    moon = planet_objects["Moon"]
    earth = planet_objects["Earth"]
    moon.parent = earth
    moon.matrix_parent_inverse = earth.matrix_world.inverted()

# --- Physics / Orbit Loop ---
for body in bodies:
    name = body["name"]
    if name not in planet_objects: continue
    obj = planet_objects[name]
    obj.rotation_mode = 'XYZ'
    
    current_angle = body["start_offset"]
    current_spin = 0.0

    for f in range(start_frame, total_frames + 1):
        if name == "Sun":
            obj.location = (0, 0, 0)
            obj.rotation_euler = (0, 0, 0) 
        else:
            if f <= showcase_total_frames:
                orbit_speed = (2 * math.pi) / body["period"]
                spin_speed = (2 * math.pi) / (body["rot_period"] * 12)
            else:
                progress = (f - showcase_total_frames) / outro_duration
                factor = 1.0 + (progress * 70.0) 
                orbit_speed = ((2 * math.pi) / body["period"]) * factor
                spin_speed = ((2 * math.pi) / (body["rot_period"] * 12)) * (factor * 0.35)

            current_angle += orbit_speed
            current_spin += spin_speed
            
            obj.location = (body["orbit_radius"] * math.cos(current_angle), body["orbit_radius"] * math.sin(current_angle), 0)
            obj.rotation_euler = (math.radians(body["tilt"]), 0, current_spin)
            
        obj.keyframe_insert(data_path="location", frame=f)
        obj.keyframe_insert(data_path="rotation_euler", frame=f)

for obj in planet_objects.values():
    if obj.animation_data and obj.animation_data.action:
        curves = getattr(obj.animation_data.action, "fcurves", getattr(obj.animation_data.action, "curves", None))
        if curves:
            for fc in curves:
                for kf in fc.keyframe_points: kf.interpolation = 'LINEAR'

# --- Cinematic Camera Controller Rig ---
cam_data = bpy.data.cameras.new(name="Cinematic_Camera")
cam_data.lens = 38
cam_obj = bpy.data.objects.new(name="Cinematic_Camera", object_data=cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

constraints_dict = {}
for body in bodies:
    name = body["name"]
    if name in planet_objects:
        track_c = cam_obj.constraints.new(type='TRACK_TO')
        track_c.name = f"Track_{name}"
        track_c.target = planet_objects[name]
        track_c.track_axis = 'TRACK_NEGATIVE_Z'
        track_c.up_axis = 'UP_Y'
        track_c.influence = 0.0
        constraints_dict[name] = track_c

for idx, body in enumerate(bodies):
    name = body["name"]
    if name not in planet_objects: continue
    target_obj = planet_objects[name]
    
    body_start_frame = start_frame + (idx * frames_per_body)
    body_end_frame = body_start_frame + frames_per_body - 1
    
    for c_name, con in constraints_dict.items():
        con.influence = 1.0 if c_name == name else 0.0
        con.keyframe_insert(data_path="influence", frame=body_start_frame)
        con.keyframe_insert(data_path="influence", frame=body_end_frame)

    offset_dist = body["radius"] * 5.0 if name != "Sun" else body["radius"] * 3.2
        
    for f in range(body_start_frame, body_end_frame + 1):
        bpy.context.scene.frame_set(f)
        if name == "Sun":
            # Sun Intro Timeline Lock
            if f <= 72:
                zoom_factor = (f - 1) / 71
                current_dist = (body["radius"] * 6.5) - (zoom_factor * (body["radius"] * 3.3))
                cam_obj.location = (0, -current_dist, current_dist * 0.35)
            else:
                stable_dist = body["radius"] * 3.2
                cam_obj.location = (0, -stable_dist, stable_dist * 0.35)
        elif name == "Moon":
            m_world = target_obj.matrix_world.to_translation()
            cam_obj.location = (m_world.x - 2.5, m_world.y - 2.5, m_world.z + 1.0)
        else:
            p_loc = target_obj.location
            angle = math.atan2(p_loc.y, p_loc.x) - 0.25
            cam_obj.location = (
                p_loc.x - (offset_dist * math.cos(angle)),
                p_loc.y - (offset_dist * math.sin(angle)),
                p_loc.z + (offset_dist * 0.35)
            )
        cam_obj.keyframe_insert(data_path="location", frame=f)

# --- Outro Wide Angle Settle ---
outro_start = showcase_total_frames + 1                     
zoom_settle_frame = showcase_total_frames + (35 * 24)       
outro_end = total_frames                                   

for c_name, con in constraints_dict.items():
    con.influence = 1.0 if c_name == "Sun" else 0.0
    con.keyframe_insert(data_path="influence", frame=outro_start)

bpy.context.scene.frame_set(outro_start)
cam_obj.keyframe_insert(data_path="location", frame=outro_start)

bpy.context.scene.frame_set(zoom_settle_frame)
cam_obj.location = (0, -185, 135)
cam_obj.keyframe_insert(data_path="location", frame=zoom_settle_frame)

bpy.context.scene.frame_set(outro_end)
cam_obj.location = (0, -185, 135)
cam_obj.keyframe_insert(data_path="location", frame=outro_end)

if cam_obj.animation_data and cam_obj.animation_data.action:
    curves = getattr(cam_obj.animation_data.action, "fcurves", getattr(cam_obj.animation_data.action, "curves", None))
    if curves:
        for fcurve in curves:
            if fcurve.data_path == "location":
                for kf in fcurve.keyframe_points: kf.interpolation = 'BEZIER'

bpy.context.scene.frame_set(start_frame)