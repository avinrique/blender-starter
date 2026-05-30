"""
Starter 3D scene generator (headless Blender).

Builds a small scene of primitive shapes with colored materials, soft lighting
and a camera, renders a preview PNG, then exports the model to multiple formats.

Run with:
    blender --background --python starter_shapes.py
"""

import bpy
import os
import math

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------
# Start from a clean scene
# ----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def make_material(name, rgba, metallic=0.0, roughness=0.5):
    """Create a Principled BSDF material with a base color."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    # smooth shading looks nicer on curved primitives
    for poly in obj.data.polygons:
        poly.use_smooth = True


# ----------------------------------------------------------------------------
# Ground plane
# ----------------------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
assign(ground, make_material("GroundMat", (0.9, 0.9, 0.92, 1.0), roughness=0.8))
# keep the plane flat-shaded
for poly in ground.data.polygons:
    poly.use_smooth = False

# ----------------------------------------------------------------------------
# The three starter shapes
# ----------------------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=2, location=(-3, 0, 1))
cube = bpy.context.active_object
cube.name = "Cube"
assign(cube, make_material("RedMat", (0.8, 0.1, 0.15, 1.0), roughness=0.4))

bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, 1.2))
sphere = bpy.context.active_object
sphere.name = "Sphere"
assign(sphere, make_material("BlueMetal", (0.1, 0.3, 0.85, 1.0), metallic=0.9, roughness=0.25))

bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=2.4, location=(3, 0, 1.2))
cyl = bpy.context.active_object
cyl.name = "Cylinder"
assign(cyl, make_material("GreenMat", (0.15, 0.7, 0.25, 1.0), roughness=0.5))

# ----------------------------------------------------------------------------
# Lighting: a key sun + a soft area fill
# ----------------------------------------------------------------------------
bpy.ops.object.light_add(type="SUN", location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(40))

bpy.ops.object.light_add(type="AREA", location=(-4, -6, 6))
area = bpy.context.active_object
area.data.energy = 400
area.data.size = 8

# subtle world background
world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.06, 0.08, 1.0)
scene.world = world

# ----------------------------------------------------------------------------
# Camera
# ----------------------------------------------------------------------------
bpy.ops.object.camera_add(location=(0, -10, 6))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(62), 0, 0)
scene.camera = cam

# ----------------------------------------------------------------------------
# Render settings + preview render
# ----------------------------------------------------------------------------
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.film_transparent = False
scene.render.filepath = os.path.join(OUT, "preview.png")
print(">>> Rendering preview...")
bpy.ops.render.render(write_still=True)

# ----------------------------------------------------------------------------
# Save .blend + export GLB / OBJ / STL
# ----------------------------------------------------------------------------
blend_path = os.path.join(OUT, "starter_shapes.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f">>> Saved {blend_path}")

# select only the mesh objects for export
bpy.ops.object.select_all(action="DESELECT")
for o in (ground, cube, sphere, cyl):
    o.select_set(True)

glb_path = os.path.join(OUT, "starter_shapes.glb")
bpy.ops.export_scene.gltf(filepath=glb_path, export_format="GLB", use_selection=True)
print(f">>> Exported {glb_path}")

obj_path = os.path.join(OUT, "starter_shapes.obj")
bpy.ops.wm.obj_export(filepath=obj_path, export_selected_objects=True)
print(f">>> Exported {obj_path}")

stl_path = os.path.join(OUT, "starter_shapes.stl")
bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
print(f">>> Exported {stl_path}")

print(">>> DONE")
