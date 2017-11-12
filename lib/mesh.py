from math import radians, sin, cos

import bpy
import bmesh


# Primitives
# ---------------------------


def make_rect(bm, x, y, h):
	coords = (( x,  y, h),
	          (-x,  y, h),
	          (-x, -y, h),
	          ( x, -y, h))

	return [bm.verts.new(co) for co in coords]


def make_tri(bm, x, y, h):
	coords = ((  x,  y / 3,     h),
	          ( -x,  y / 3,     h),
	          (0.0, -y / 3 * 2, h))

	return [bm.verts.new(co) for co in coords]


def make_circle(size):
	bm = bmesh.new()
	radius = size / 2
	rad = radians(360.0) / 64

	for i in range(64):
		x = sin(i * rad) * radius
		y = cos(i * rad) * radius

		bm.verts.new((x, y, 0.0))

	bm.verts.ensure_lookup_table()
	make_edges(bm, bm.verts)

	return bm


# Tools
# ---------------------------


def to_bmesh(ob, apply_modifiers=True, apply_transforms=True, triangulate=True):

	if (apply_modifiers and ob.modifiers) or (ob.type != 'MESH'):
		me = ob.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface=False)
		bm = bmesh.new()
		bm.from_mesh(me)
		bpy.data.meshes.remove(me)
	else:
		me = ob.data
		if ob.mode == 'EDIT':
			bm_orig = bmesh.from_edit_mesh(me)
			bm = bm_orig.copy()
		else:
			bm = bmesh.new()
			bm.from_mesh(me)

	if apply_transforms:
		bm.transform(ob.matrix_world)

	if triangulate:
		bmesh.ops.triangulate(bm, faces=bm.faces)

	return bm


def volume(ob):
	bm = to_bmesh(ob)
	vol = bm.calc_volume()
	bm.free()
	return vol


def polycount(ob):
	bm = to_bmesh(ob, apply_transforms=False, triangulate=False)
	count = len(bm.faces)
	bm.free()
	return count


def edges_length(ob):
	bm = to_bmesh(ob, triangulate=False)
	length = 0.0

	for edge in bm.edges:
		length += edge.calc_length()

	bm.free()
	return length


def make_edges(bm, verts):
	edges = []

	for i in range(len(verts) - 1):
		edges.append(bm.edges.new((verts[i], verts[i + 1])))

	edges.append(bm.edges.new((verts[-1], verts[0])))

	return edges


def bridge_verts(bm, v1, v2):
	faces = []
	edges = []

	for i in range(len(v1) - 1):
		f = bm.faces.new([v1[i + 1], v1[i], v2[i], v2[i + 1]])
		faces.append(f)
		edges.append(f.edges[1])

	f = bm.faces.new([v1[0], v1[i + 1], v2[i + 1], v2[0]])
	faces.append(f)
	edges.append(f.edges[1])

	return {'faces': faces, 'edges': edges}


def duplicate_verts(bm, verts, z=False):
	dup = bmesh.ops.duplicate(bm, geom=verts)
	verts = [x for x in dup['geom'] if isinstance(x, bmesh.types.BMVert)]

	if z is not False:
		for v in verts:
			v.co[2] = z

	return verts


def duplicate_edges(bm, edges, z=False):
	dup = bmesh.ops.duplicate(bm, geom=edges)
	edges = [x for x in dup['geom'] if isinstance(x, bmesh.types.BMEdge)]

	if z is not False:
		verts = [x for x in dup['geom'] if isinstance(x, bmesh.types.BMVert)]
		for v in verts:
			v.co[2] = z

	return edges


def edge_loop_expand(e, limit=0):
	edges = []
	app = edges.append

	app(e)

	loop = e.link_loops[0]

	loop_next = loop
	loop_prev = loop

	i = 1
	while i < limit:
		loop_next = loop_next.link_loop_next.link_loop_radial_next.link_loop_next
		loop_prev = loop_prev.link_loop_prev.link_loop_radial_prev.link_loop_prev
		app(loop_next.edge)
		app(loop_prev.edge)
		i += 1

	return edges


def edge_loop_walk(verts):
	v = verts[0]
	e = v.link_edges[1]

	v_loop = [v.co[:]]
	v_total = len(verts) - 1

	while v_total > 0:
		ov = e.other_vert(v)
		v_loop.append(ov.co[:])
		v = ov

		le = ov.link_edges

		for oe in le:
			if oe != e:
				e = oe
				break

		v_total -= 1

	return v_loop
