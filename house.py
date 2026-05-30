"""
Low-poly house generator (headless Blender).

Run with:
    blender --background --python house.py
"""

import bpy
import os
import math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name, rgba, metallic=0.0, roughness=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    return m


def assign(obj, m, smooth=False):
    obj.data.materials.clear()
    obj.data.materials.append(m)
    for p in obj.data.polygons:
        p.use_smooth = smooth


# --- Ground ---
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
assign(ground, mat("Grass", (0.25, 0.55, 0.2, 1.0), roughness=0.9))

# --- Walls (a box) ---
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
walls = bpy.context.active_object
walls.name = "Walls"
walls.scale = (2.0, 1.6, 1.0)  # 4 x 3.2 x 2 m
assign(walls, mat("WallCream", (0.92, 0.87, 0.72, 1.0)))

# --- Roof (a cone with 4 sides = pyramid) ---
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=3.1, radius2=0,
                                depth=1.8, location=(0, 0, 2.9))
roof = bpy.context.active_object
roof.name = "Roof"
roof.rotation_euler = (0, 0, math.radians(45))
assign(roof, mat("RoofRed", (0.6, 0.12, 0.1, 1.0), roughness=0.7))

# --- Door ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.61, 0.7))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.5, 0.05, 0.7)
assign(door, mat("DoorWood", (0.35, 0.2, 0.08, 1.0), roughness=0.5))

# --- Windows ---
for i, x in enumerate((-1.2, 1.2)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -1.61, 1.2))
    w = bpy.context.active_object
    w.name = f"Window{i}"
    w.scale = (0.45, 0.05, 0.45)
    assign(w, mat("Glass", (0.55, 0.8, 0.95, 1.0), metallic=0.3, roughness=0.1))

# --- Chimney ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.2, 0.6, 3.2))
chim = bpy.context.active_object
chim.name = "Chimney"
chim.scale = (0.35, 0.35, 0.9)
assign(chim, mat("Brick", (0.5, 0.25, 0.2, 1.0), roughness=0.8))

# --- A couple of low-poly trees ---
def tree(x, y):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.0, location=(x, y, 0.5))
    trunk = bpy.context.active_object
    assign(trunk, mat("Trunk", (0.3, 0.18, 0.08, 1.0)))
    bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0, depth=1.8, location=(x, y, 1.8))
    leaves = bpy.context.active_object
    assign(leaves, mat("Leaves", (0.15, 0.45, 0.15, 1.0)))

tree(-4.5, 2.0)
tree(5.0, -1.5)

# --- Lighting ---
bpy.ops.object.light_add(type="SUN", location=(6, -6, 12))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))

world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.7, 0.95, 1.0)
scene.world = world

# --- Camera ---
bpy.ops.object.camera_add(location=(9, -9, 6))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(65), 0, math.radians(45))
scene.camera = cam

# --- Render + save + export ---
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = os.path.join(OUT, "house_preview.png")
print(">>> Rendering house...")
bpy.ops.render.render(write_still=True)

blend_path = os.path.join(OUT, "house.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f">>> Saved {blend_path}")

bpy.ops.object.select_all(action="SELECT")
glb_path = os.path.join(OUT, "house.glb")
bpy.ops.export_scene.gltf(filepath=glb_path, export_format="GLB", use_selection=True)
print(f">>> Exported {glb_path}")
print(">>> DONE")
