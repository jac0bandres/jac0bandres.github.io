"""Generate a one-color, website-inspired 3D-printable business card.

Run with:
    blender --background --python business-card/generate_card.py

All dimensions are millimetres. The result is a single watertight STL with
shallow/deep engraving and a perforated, pixel-stencil website address.
"""

from pathlib import Path
import math
import sys

import bpy
import bmesh
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from complex_grid import mobius_pole_paths, save_diagnostic


ROOT = SCRIPT_DIR
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

CARD_W = 85.60
CARD_H = 54.00
BODY_H = 1.20
CORNER_RADIUS = 2.35

SHALLOW_DEPTH = 0.18
DEEP_DEPTH = 0.38
GRID_WIDTH = 0.42
CUTTER_OVERTRAVEL = 0.30

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"

CARD_COLOR = (0.035, 0.043, 0.043, 1.0)
CUTTER_COLOR = (0.55, 0.08, 0.04, 1.0)

def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def material(name, rgba, roughness=0.48):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def cube_obj(name, location, dimensions, mat=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    return obj


def rounded_body(mat):
    # Build an exact rounded-rectangle prism. A 3D bevel modifier expands very
    # thin solids in Z, so explicit top/bottom loops preserve the 1.20 mm spec.
    outline = []
    corner_centers = (
        (CARD_W / 2 - CORNER_RADIUS, CARD_H / 2 - CORNER_RADIUS, 0),
        (-CARD_W / 2 + CORNER_RADIUS, CARD_H / 2 - CORNER_RADIUS, 1),
        (-CARD_W / 2 + CORNER_RADIUS, -CARD_H / 2 + CORNER_RADIUS, 2),
        (CARD_W / 2 - CORNER_RADIUS, -CARD_H / 2 + CORNER_RADIUS, 3),
    )
    segments = 10
    for cx, cy, quadrant in corner_centers:
        start = quadrant * math.pi / 2
        for step in range(segments + 1):
            angle = start + step * math.pi / 2 / segments
            outline.append((cx + CORNER_RADIUS * math.cos(angle),
                            cy + CORNER_RADIUS * math.sin(angle)))
    count = len(outline)
    vertices = [(x, y, 0) for x, y in outline] + [(x, y, BODY_H) for x, y in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count) for i in range(count))
    mesh = bpy.data.meshes.new("card_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("card", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def text_cutter(name, value, x, y, size, depth, font, mat, max_width=None,
                tracking=0.0, align="LEFT"):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = value
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.size = size
    # Extend decisively above and below the requested cut. This prevents thin
    # top-face remnants where text intersects the shallow grid.
    curve.extrude = (depth + CUTTER_OVERTRAVEL) / 2
    curve.resolution_u = 8
    curve.bevel_resolution = 1
    curve.offset_x = tracking
    curve.font = bpy.data.fonts.load(font, check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, BODY_H - depth / 2 + .01)
    obj.data.materials.append(mat)
    bpy.context.view_layer.update()
    if max_width and obj.dimensions.x > max_width:
        obj.scale.x *= max_width / obj.dimensions.x
        bpy.context.view_layer.update()
    return obj


def curve_cutter(name, points, width, depth, mat):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = width / 2
    curve.bevel_resolution = 2
    curve.use_fill_caps = True
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (co[0], co[1], 0, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    cutter_h = depth + .12
    obj.scale.z = cutter_h / width
    obj.location.z = BODY_H - depth / 2 + .01
    obj.data.materials.append(mat)
    return obj


def warped_grid(mat):
    paths = mobius_pole_paths(CARD_W, CARD_H, inversion=.10)
    save_diagnostic(OUTPUT / "complex-plane-grid.png", paths, CARD_W, CARD_H, .10)
    cutters = []
    for index, path in enumerate(paths):
        points = [tuple(point) for point in path["points"]]
        cutters.append(curve_cutter(
            f"lens_{path['family']}_{index}", points, GRID_WIDTH,
            SHALLOW_DEPTH, mat,
        ))
    return cutters


def stencil_text_cutters(value, x, y, size, mat):
    """Build mono through-cut text with narrow bridges in closed glyphs."""
    cutters = []
    pitch = size * .602
    counter_chars = {"a", "b", "d", "o"}
    for char_index, char in enumerate(value):
        glyph = text_cutter(
            f"domain_{char_index}", char, x + char_index * pitch, y, size,
            BODY_H + .30, FONT_MONO, mat,
        )
        bpy.context.view_layer.update()
        if char in counter_chars:
            # Remove a hairline from the cutter so the card retains a classic
            # stencil bridge and enclosed counters remain physically attached.
            bounds = [glyph.matrix_world @ Vector(corner) for corner in glyph.bound_box]
            center_x = (min(v.x for v in bounds) + max(v.x for v in bounds)) / 2
            bridge = cube_obj(
                f"domain_bridge_{char_index}",
                (center_x, y, BODY_H / 2),
                (.36, size * 1.25, BODY_H + .50),
            )
            bpy.context.view_layer.objects.active = glyph
            glyph.select_set(True)
            bpy.ops.object.convert(target="MESH")
            modifier = glyph.modifiers.new("stencil_bridge", "BOOLEAN")
            modifier.operation = "DIFFERENCE"
            modifier.solver = "EXACT"
            modifier.object = bridge
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.data.objects.remove(bridge, do_unlink=True)
        cutters.append(glyph)
    return cutters


def convert_to_mesh(objects):
    for obj in objects:
        if obj.type in {"CURVE", "FONT"}:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.convert(target="MESH")
            obj.select_set(False)


def subtract(body, cutters, modifier_name):
    cutter_collection = bpy.data.collections.new(f"{modifier_name}_operands")
    bpy.context.scene.collection.children.link(cutter_collection)
    for cutter in cutters:
        cutter_collection.objects.link(cutter)
    modifier = body.modifiers.new(modifier_name, "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.operand_type = "COLLECTION"
    modifier.collection = cutter_collection
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for cutter in cutters:
        bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.collections.remove(cutter_collection)


def make_watertight(body):
    """Resolve coincident Boolean edges into a single printable skin."""
    mesh = bmesh.new()
    mesh.from_mesh(body.data)
    bmesh.ops.remove_doubles(mesh, verts=mesh.verts, dist=.0005)
    bmesh.ops.dissolve_degenerate(mesh, edges=mesh.edges, dist=.0001)
    bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    mesh.to_mesh(body.data)
    mesh.free()
    body.data.update()


def export_stl(body):
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.wm.stl_export(
        filepath=str(OUTPUT / "jacob-andres-card.stl"),
        export_selected_objects=True,
        apply_modifiers=True,
        ascii_format=False,
    )


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_preview(body):
    scene = bpy.context.scene
    bpy.context.preferences.filepaths.save_version = 0
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.use_nodes = True
    world = scene.world.node_tree.nodes["Background"]
    world.inputs["Color"].default_value = (.018, .020, .020, 1)
    world.inputs["Strength"].default_value = .06

    ground_mat = material("ground", (.014, .016, .016, 1), roughness=.62)
    cube_obj("render_ground", (0, 0, -.55), (180, 130, 1), ground_mat)

    bpy.ops.object.camera_add(location=(68, -102, 132))
    camera = bpy.context.object
    camera.data.lens = 52
    point_at(camera, (0, 0, 0))
    scene.camera = camera

    for name, location, energy, size, color in (
        ("key", (-50, -28, 70), 39000, 48, (1.0, .78, .50)),
        ("fill", (55, -4, 38), 23000, 38, (.55, .73, 1.0)),
        ("rim", (5, 60, 52), 29000, 32, (1.0, .65, .30)),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        point_at(light, (0, 0, 0))

    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = .45
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / "business-card.blend"))
    scene.render.filepath = str(OUTPUT / "preview.png")
    bpy.ops.render.render(write_still=True)


def main():
    print("[card] building source geometry", flush=True)
    reset_scene()
    card_mat = material("single_color_filament", CARD_COLOR, roughness=.43)
    cutter_mat = material("boolean_cutters", CUTTER_COLOR)
    body = rounded_body(card_mat)

    shallow = warped_grid(cutter_mat)
    shallow.append(text_cutter(
        "tagline", "HUMAN / SYSTEMS / MATH", -38.0, -11.8, 2.45,
        SHALLOW_DEPTH, FONT_MONO, cutter_mat, max_width=39.0, tracking=.015,
    ))
    email_prefix = text_cutter(
        "email_prefix", "jacob@", -38.0, -20.0, 3.75,
        DEEP_DEPTH, FONT_MONO, cutter_mat, tracking=.01,
    )
    bpy.context.view_layer.update()
    name_prefix = text_cutter(
        "name_line_1_prefix", "JACOB ANDR", -38.0, 10.6, 11.8,
        DEEP_DEPTH, FONT_BOLD, cutter_mat, tracking=-.18,
    )
    bpy.context.view_layer.update()
    accent_x = -38.0 + name_prefix.dimensions.x - .35
    name_accent = text_cutter(
        "name_accent", "É", accent_x, 10.6, 11.8,
        BODY_H + .30, FONT_BOLD, cutter_mat, tracking=-.18,
    )
    bpy.context.view_layer.update()
    name_suffix = text_cutter(
        "name_line_1_suffix", "S", accent_x + name_accent.dimensions.x + .55,
        10.6, 11.8, DEEP_DEPTH, FONT_BOLD, cutter_mat, tracking=-.18,
    )
    deep = [
        name_prefix,
        name_suffix,
        text_cutter("name_line_2", "NAVARRETE", -38.0, -.4, 11.8,
                    DEEP_DEPTH, FONT_BOLD, cutter_mat, max_width=55.0, tracking=-.18),
        email_prefix,
    ]
    domain_x = -38.0 + email_prefix.dimensions.x + .28
    through = stencil_text_cutters("jacobandres.com", domain_x, -20.0, 3.75, cutter_mat)
    through.append(name_accent)

    print("[card] converting cutters", flush=True)
    convert_to_mesh([*shallow, *deep, *through])
    print("[card] subtracting website", flush=True)
    subtract(body, through, "website_through_cut")
    print("[card] subtracting deep etch", flush=True)
    subtract(body, deep, "deep_etch")
    print("[card] subtracting shallow etch", flush=True)
    subtract(body, shallow, "shallow_etch")
    print("[card] making print mesh watertight", flush=True)
    make_watertight(body)

    print("[card] exporting", flush=True)
    export_stl(body)
    print("[card] rendering preview", flush=True)
    render_preview(body)


if __name__ == "__main__":
    main()
