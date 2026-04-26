## Libraries
- networkx
	- creation, manipulation, and study of complex graph networks
	- directed and undirected graphs
	- nodes can be any hashable object
- numpy
- pyvista
	- 3d visualization and analysis
- tetgen
	- tetrahedral mesh generation
	- Deluanay meshes, Voronoi partitions 
- scipy (optimize, spatial.transform)
- open3d
	- visualize 3d data
- time
- pickle
	- object serialization
- base64

## Functions
- encode_object
	- encodes using pickle
- decode_object
	- decodes using pickle
- o3d.io.read_triangle_mesh
	- reads triangle mesh from file
- tetgen.TetGen()
	- Input, clean, and tetrahedralize surface meshes using TetGen.
- tetgen.tetrahedralize()
	- Generate tetrahedrals interior to the surface mesh.
	- .grid() returns pyvista.UnstructuredGrid
	- 

Returns nodes and elements belonging to the all tetrahedral mesh.

Nahum Bearden