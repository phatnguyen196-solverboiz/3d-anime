"""Executed by Blender's bundled Python, never by the API interpreter.

Input is a validated declarative JSON recipe. No user scripts or asset paths are executed.
"""

import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def _material(name, spec):
    material = bpy.data.materials.new(f"{name}.material")
    material.diffuse_color = spec.get("color", [0.8, 0.8, 0.8, 1.0])
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = material.diffuse_color
    shader.inputs["Metallic"].default_value = spec.get("metallic", 0.0)
    shader.inputs["Roughness"].default_value = spec.get("roughness", 0.5)
    return material


def _object(spec):
    primitive = spec["primitive"]
    if primitive == "cube":
        bpy.ops.mesh.primitive_cube_add()
    elif primitive == "uv_sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12)
    elif primitive == "plane":
        bpy.ops.mesh.primitive_plane_add()
    elif primitive == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=24)
    elif primitive == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=24)
    obj = bpy.context.object
    obj.name = spec["name"]
    obj.location = spec.get("location", [0, 0, 0])
    obj.rotation_euler = [math.radians(v) for v in spec.get("rotation_deg", [0, 0, 0])]
    obj.scale = spec.get("scale", [1, 1, 1])
    obj.data.materials.append(_material(obj.name, spec))
    for key in sorted(spec.get("keyframes", []), key=lambda item: item["frame"]):
        frame = key["frame"] + 1  # Project local frame 0 is Blender frame 1.
        obj.location = key["location"]
        obj.keyframe_insert(data_path="location", frame=frame)
        if "rotation_deg" in key:
            obj.rotation_euler = [math.radians(v) for v in key["rotation_deg"]]
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        if "scale" in key:
            obj.scale = key["scale"]
            obj.keyframe_insert(data_path="scale", frame=frame)
    body = spec.get("rigid_body")
    if body:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.object_add()
        obj.rigid_body.type = body["type"].upper()
        if body["type"] == "active":
            obj.rigid_body.mass = body.get("mass", 1.0)


def _camera(spec, scene):
    data = bpy.data.cameras.new("AnimeFlowCamera")
    obj = bpy.data.objects.new("AnimeFlowCamera", data)
    scene.collection.objects.link(obj)
    obj.location = spec["location"]
    direction = Vector(spec["target"]) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    if spec.get("type") == "orthographic":
        data.type = "ORTHO"
        data.ortho_scale = spec.get("ortho_scale", 6.0)
    else:
        data.lens = spec.get("lens_mm", 50.0)
    scene.camera = obj


def _light(spec, index, scene):
    kind = {"area": "AREA", "point": "POINT", "sun": "SUN"}[spec["type"]]
    data = bpy.data.lights.new(f"AnimeFlowLight{index}", type=kind)
    data.energy = spec["energy"]
    data.color = spec.get("color", [1, 1, 1])
    if kind == "AREA":
        data.shape = "DISK"
        data.size = spec.get("size", 5.0)
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    obj.location = spec["location"]
    if kind == "SUN":
        obj.rotation_euler = (Vector((0, 0, 0)) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main(request_path):
    request = json.loads(Path(request_path).read_text(encoding="utf-8"))
    recipe = request["scene"]
    random.seed(recipe.get("seed", 0))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = recipe.get("samples", 16)
    scene.render.resolution_x = request["width"]
    scene.render.resolution_y = request["height"]
    scene.render.resolution_percentage = 100
    scene.render.fps = request["fps"]["numerator"]
    scene.render.fps_base = request["fps"]["denominator"]
    scene.render.image_settings.file_format = "PNG"
    scene.frame_start = 1
    scene.frame_end = request["shot_duration_frames"]
    if scene.world is None:
        scene.world = bpy.data.worlds.new("AnimeFlowWorld")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = recipe.get(
        "world_color", [0.06, 0.07, 0.1, 1.0]
    )
    _camera(recipe["camera"], scene)
    lights = recipe.get("lights") or [{"type": "area", "location": [3, -4, 7], "energy": 600}]
    for index, light in enumerate(lights):
        _light(light, index, scene)
    physics = False
    for obj in recipe["objects"]:
        _object(obj)
        physics |= "rigid_body" in obj
    if physics:
        cache = scene.rigidbody_world.point_cache
        cache.frame_start = 1
        cache.frame_end = request["shot_duration_frames"]
        bpy.ops.ptcache.bake_all(bake=True)
    frames_dir = Path(request["frames_dir"])
    frames_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for index in range(request["frame_start"], request["frame_end_exclusive"]):
        scene.frame_set(index + 1)
        scene.render.filepath = str(frames_dir / f"frame_{index:06d}.png")
        bpy.ops.render.render(write_still=True)
        count += 1
    result = {"blender_version": bpy.app.version_string, "rendered_frames": count}
    Path(request["result_path"]).write_text(json.dumps(result), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1])
