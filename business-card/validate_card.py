"""Check the generated single-material STL's dimensions and manifold edges."""

from pathlib import Path

import bmesh
import bpy


filename = Path(__file__).resolve().parent / "output" / "jacob-andres-card.stl"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(filename))
objects = list(bpy.context.selected_objects)
vertices = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
bounds = tuple(
    max(getattr(vertex, axis) for vertex in vertices)
    - min(getattr(vertex, axis) for vertex in vertices)
    for axis in "xyz"
)
open_edges = 0
for obj in objects:
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    open_edges += sum(not edge.is_manifold for edge in mesh.edges)
    mesh.free()

print(
    f"{filename.name}: bounds={bounds[0]:.2f} x {bounds[1]:.2f} x {bounds[2]:.2f} mm; "
    f"non-manifold edges={open_edges}"
)
