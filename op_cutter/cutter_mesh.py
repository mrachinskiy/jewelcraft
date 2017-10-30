from math import radians, sin, cos

import bmesh

from ..lib.mesh import (
	make_rect,
	make_tri,
	make_edges,
	bridge_verts,
	edge_loop_expand,
	duplicate_verts,
	edge_loop_walk,
	)
from . import profile_pear, profile_heart


_offset_type = {
	'offset': 0,
	'width': 1,
	'depth': 2,
	'percent': 3,
	}


def create_cutter(self):
	bm = bmesh.new()

	# Square/Rectangle
	# ---------------------------

	if self.shape_sq or self.shape_rect:

		handle_l_size = self.handle_l_size / 2
		girdle_l_size = self.gem_l / 2 + self.girdle_l_ofst
		hole_l_size = self.hole_l_size / 2

		if self.shape_rect:
			handle_w_size = self.handle_w_size / 2
			girdle_w_size = self.gem_w / 2 + self.girdle_l_ofst
			hole_w_size = self.hole_w_size / 2
		else:
			handle_w_size = handle_l_size
			girdle_w_size = girdle_l_size
			hole_w_size = hole_l_size

		if self.bevel_corners:

			if self.shape_rect:
				bv_off_t = _offset_type['offset']
				bv_off = self.bevel_corners_width
			else:
				bv_off_t = _offset_type['percent']
				bv_off = self.bevel_corners_percent

			base_coords = ((handle_w_size, handle_l_size, self.handle_z_btm),
			               (girdle_w_size, girdle_l_size, -self.girdle_z_btm),
			               (hole_w_size, hole_l_size, -self.hole_z_top))

			coords = []

			for co in base_coords:
				vs = make_rect(bm, co[0], co[1], co[2])
				make_edges(bm, vs)

				bv = bmesh.ops.bevel(bm, geom=bm.verts, clamp_overlap=True, vertex_only=True, offset=bv_off, offset_type=bv_off_t, segments=self.bevel_corners_segments, profile=self.bevel_corners_profile)
				bv_coords = edge_loop_walk(bv['verts'])
				coords.append(bv_coords)

				bm.free()
				bm = bmesh.new()

			if self.handle:
				v_handle_bottom = [bm.verts.new(v) for v in coords[0]]
			v_girdle_btm = [bm.verts.new(v) for v in coords[1]]
			v_hole_top = [bm.verts.new(v) for v in coords[2]]

		else:
			if self.handle:
				v_handle_bottom = make_rect(bm, handle_w_size, handle_l_size, self.handle_z_btm)
			v_girdle_btm = make_rect(bm, girdle_w_size, girdle_l_size, -self.girdle_z_btm)
			v_hole_top = make_rect(bm, hole_w_size, hole_l_size, -self.hole_z_top)

		e_hole_top = make_edges(bm, v_hole_top)

		v_girdle_top = duplicate_verts(bm, v_girdle_btm, z=self.girdle_z_top)

		if self.handle:
			v_handle_top = duplicate_verts(bm, v_handle_bottom, z=self.handle_z_top)
			bridge_verts(bm, v_handle_top, v_handle_bottom)
			bridge_verts(bm, v_handle_bottom, v_girdle_top)
			bm.faces.new(v_handle_top)
		else:
			bm.faces.new(v_girdle_top)

		bridge_verts(bm, v_girdle_top, v_girdle_btm)

		if self.curve_seat:
			sm_z = (self.girdle_z_btm + self.hole_z_top) / 2 * 1.4

			v_sm = duplicate_verts(bm, v_girdle_btm, z=-sm_z)
			e_sm = make_edges(bm, v_sm)

			bridge_verts(bm, v_girdle_btm, v_sm)

			v_fallback = v_sm

		else:
			v_fallback = v_girdle_btm

		bridge_verts(bm, v_fallback, v_hole_top)

		if self.hole:
			v_hole_bottom = duplicate_verts(bm, v_hole_top, z=-self.hole_z_btm)
			bridge_verts(bm, v_hole_top, v_hole_bottom)
			bm.faces.new(reversed(v_hole_bottom))

		else:
			if self.shape_rect:
				half = int(len(v_hole_top) / 2)

				e_0 = e_hole_top[0]
				e_h = e_hole_top[half]

				if self.bevel_corners:
					quarter = int(half / 2)

					e_side_1 = edge_loop_expand(e_0, limit=quarter)
					e_side_2 = edge_loop_expand(e_h, limit=quarter)

					bmesh.ops.collapse(bm, edges=e_side_1)
					bmesh.ops.collapse(bm, edges=e_side_2)

				else:
					bmesh.ops.collapse(bm, edges=(e_0, e_h))

			else:
				bmesh.ops.collapse(bm, edges=e_hole_top)

	# Triangle
	# ---------------------------

	elif self.shape_tri:

		handle_l_size = self.handle_l_size
		handle_w_size = self.handle_w_size / 2

		girdle_l_size = self.gem_l + self.girdle_l_ofst
		girdle_w_size = self.gem_w / 2 + self.girdle_w_ofst

		hole_l_size = self.hole_l_size
		hole_w_size = self.hole_w_size / 2

		if self.bevel_corners or self.curve_profile:

			bv_off_t = _offset_type['percent']
			bv_off = self.bevel_corners_percent

			base_coords = [(handle_w_size, handle_l_size),
			               (girdle_w_size, girdle_l_size),
			               (hole_w_size, hole_l_size)]

			coords = []

			for co in base_coords:
				v_profile = make_tri(bm, co[0], co[1], 0.0)
				make_edges(bm, v_profile)

				if self.bevel_corners:
					bmesh.ops.bevel(bm, geom=v_profile, clamp_overlap=True, vertex_only=True, offset=bv_off, offset_type=bv_off_t, segments=self.bevel_corners_segments, profile=self.bevel_corners_profile)

				if self.curve_profile:
					bm.edges.ensure_lookup_table()
					e_subd = (bm.edges[-1],
					          bm.edges[-2],
					          bm.edges[-3])
					bm.normal_update()
					bmesh.ops.subdivide_edges(bm, edges=e_subd, smooth=self.curve_profile_factor, smooth_falloff=4, cuts=self.curve_profile_segments)

				bm.verts.ensure_lookup_table()
				profile_coords = edge_loop_walk(bm.verts)
				coords.append(profile_coords)

				bm.free()
				bm = bmesh.new()

			if self.handle:
				v_handle_bottom = [bm.verts.new((v[0], v[1], self.handle_z_btm)) for v in coords[0]]
			v_girdle_btm = [bm.verts.new((v[0], v[1], -self.girdle_z_btm)) for v in coords[1]]
			if self.hole:
				v_hole_top = [bm.verts.new((v[0], v[1], -self.hole_z_top)) for v in coords[2]]

		else:

			if self.handle:
				v_handle_bottom = make_tri(bm, handle_w_size, handle_l_size, self.handle_z_btm)
			v_girdle_btm = make_tri(bm, girdle_w_size, girdle_l_size, -self.girdle_z_btm)
			if self.hole:
				v_hole_top = make_tri(bm, hole_w_size, hole_l_size, -self.hole_z_top)

		v_girdle_top = duplicate_verts(bm, v_girdle_btm, z=self.girdle_z_top)
		bridge_verts(bm, v_girdle_top, v_girdle_btm)

		if self.handle:
			v_handle_top = duplicate_verts(bm, v_handle_bottom, z=self.handle_z_top)
			bridge_verts(bm, v_handle_top, v_handle_bottom)
			bridge_verts(bm, v_handle_bottom, v_girdle_top)
			bm.faces.new(v_handle_top)
		else:
			bm.faces.new(v_girdle_top)

		if self.curve_seat:
			sm_z = (self.girdle_z_btm + self.hole_z_top) / 2 * 1.4

			v_sm = duplicate_verts(bm, v_girdle_btm, z=-sm_z)
			e_sm = make_edges(bm, v_sm)

			bridge_verts(bm, v_girdle_btm, v_sm)

			v_fallback = v_sm
		else:
			v_fallback = v_girdle_btm
			sm_z = 0.0

		if self.hole:
			bridge_verts(bm, v_fallback, v_hole_top)
			v_hole_bottom = duplicate_verts(bm, v_hole_top, z=-self.hole_z_btm)
			bridge_verts(bm, v_hole_top, v_hole_bottom)
			bm.faces.new(reversed(v_hole_bottom))
		else:
			f_bottom = bm.faces.new(reversed(v_fallback))
			bm.normal_update()
			bmesh.ops.poke(bm, faces=[f_bottom], offset=self.hole_z_top - sm_z, center_mode=0)

	# Fantasy
	# ---------------------------

	elif self.shape_fant:

		if self.cut == 'OVAL':
			size_l = self.gem_l / 2 + self.girdle_l_ofst
			size_w = self.gem_w / 2 + self.girdle_l_ofst

			curve_resolution = self.detalization
			rad = radians(-360.0) / curve_resolution

			profile_coords = []
			co_app = profile_coords.append

			for i in range(curve_resolution):
				x = sin(i * rad)
				y = cos(i * rad)
				z = 0.0
				co_app((x, y, z))

			v_cos = [(v[0] * size_w, v[1] * size_l, -self.girdle_z_btm) for v in profile_coords]

		elif self.cut == 'MARQUISE':
			size_l = self.gem_l / 2 + self.girdle_l_ofst
			size_w = self.gem_w / 2 + self.girdle_l_ofst

			curve_resolution = int(self.detalization / 4) + 1
			rad = radians(90.0) / (curve_resolution - 1)

			profile_coords = []
			co_app = profile_coords.append

			m1 = 1.0
			m2 = 1.0

			for i in range(curve_resolution):
				x = sin(i * rad)
				y = cos(i * rad) * m1
				z = 0.0
				co_app((-x, y, z))

				m1 *= (self.mul_1 * m2 - 1) / curve_resolution + 1
				m2 *= self.mul_2 / curve_resolution + 1

			for v in reversed(profile_coords[:-1]):
				co_app((v[0], -v[1], v[2]))

			for v in reversed(profile_coords[1:-1]):
				co_app((-v[0], v[1], v[2]))

			v_cos = [(v[0] * size_w, v[1] * size_l, -self.girdle_z_btm) for v in profile_coords]

		elif self.cut in {'PEAR', 'HEART'}:
			profile_coords = profile_pear.vertex_coords if self.cut == 'PEAR' else profile_heart.vertex_coords

			size_l = self.gem_l + self.girdle_l_ofst * 2
			size_w = self.gem_w + self.girdle_l_ofst * 2

			size = max(size_l, size_w)

			v_cos = [(x[0] * size, x[1] * size, -self.girdle_z_btm) for x in profile_coords]

		v_girdle_btm = [bm.verts.new(v) for v in v_cos]
		v_girdle_top = duplicate_verts(bm, v_girdle_btm, z=self.girdle_z_top)
		bridge_verts(bm, v_girdle_top, v_girdle_btm)

		if self.handle:
			if self.cut == 'PEAR':
				handle_l_size = self.handle_l_size
				handle_w_size = self.handle_w_size * 1.6
			elif self.cut == 'HEART':
				handle_l_size = self.handle_l_size
				handle_w_size = self.handle_w_size
			else:
				handle_l_size = self.handle_l_size / 2
				handle_w_size = self.handle_w_size / 2

			v_cos_handle = [(v[0] * handle_w_size, v[1] * handle_l_size, self.handle_z_btm) for v in profile_coords]
			v_handle_bottom = [bm.verts.new(v) for v in v_cos_handle]
			v_handle_top = duplicate_verts(bm, v_handle_bottom, z=self.handle_z_top)
			bridge_verts(bm, v_handle_top, v_handle_bottom)
			bridge_verts(bm, v_handle_bottom, v_girdle_top)
			bm.faces.new(v_handle_top)

			if self.cut in {'PEAR', 'HEART'}:
				bmesh.ops.translate(bm, verts=v_handle_top + v_handle_bottom, vec=(0.0, self.hole_pos_ofst, 0.0))
		else:
			bm.faces.new(v_girdle_top)

		if self.curve_seat:
			sm_z = (self.girdle_z_btm + self.hole_z_top) / 2 * 1.4

			v_sm = duplicate_verts(bm, v_girdle_btm, z=-sm_z)
			e_sm = make_edges(bm, v_sm)

			bridge_verts(bm, v_girdle_btm, v_sm)

			v_fallback = v_sm

		else:
			v_fallback = v_girdle_btm
			sm_z = 0.0

		if self.hole:
			if self.cut == 'PEAR':
				hole_l_size = self.hole_l_size
				hole_w_size = self.hole_w_size * 1.6
			elif self.cut == 'HEART':
				hole_l_size = self.hole_l_size
				hole_w_size = self.hole_w_size
			else:
				hole_l_size = self.hole_l_size / 2
				hole_w_size = self.hole_w_size / 2

			v_cos_hole = [(v[0] * hole_w_size, v[1] * hole_l_size, -self.hole_z_top) for v in profile_coords]

			v_hole_top = [bm.verts.new(v) for v in v_cos_hole]
			v_hole_bottom = [bm.verts.new((v[0], v[1], -self.hole_z_btm)) for v in v_cos_hole]

			bridge_verts(bm, v_fallback, v_hole_top)
			bridge_verts(bm, v_hole_top, v_hole_bottom)

			bm.faces.new(reversed(v_hole_bottom))

			if self.cut in {'PEAR', 'HEART'}:
				bmesh.ops.translate(bm, verts=v_hole_top + v_hole_bottom, vec=(0.0, self.hole_pos_ofst, 0.0))

		else:
			f_bottom = bm.faces.new(reversed(v_fallback))
			bm.normal_update()
			pk = bmesh.ops.poke(bm, faces=[f_bottom], offset=self.hole_z_top - sm_z, center_mode=0)

			if self.cut == 'PEAR':
				pk['verts'][0].co[1] = v_girdle_btm[16].co[1]
			elif self.cut == 'HEART':
				pk['verts'][0].co[1] = 0.0

	# Round
	# ---------------------------

	else:

		handle_size = self.handle_l_size / 2
		girdle_size = self.gem_l / 2 + self.girdle_l_ofst
		hole_size = self.hole_l_size / 2

		v_cos = []

		if self.handle:
			v_cos += [(0.0, handle_size, self.handle_z_top),
			          (0.0, handle_size, self.handle_z_btm)]

		v_cos += [(0.0, girdle_size, self.girdle_z_top),
		          (0.0, girdle_size, -self.girdle_z_btm)]

		if self.hole:
			v_cos += [(0.0, hole_size, -self.hole_z_top),
			          (0.0, hole_size, -self.hole_z_btm)]
		else:
			v_cos += [(0.0, 0.0, -self.hole_z_top)]

		v_profile = [bm.verts.new(v) for v in v_cos]

		for i in range(len(v_profile) - 1):
			bm.edges.new((v_profile[i], v_profile[i + 1]))

		bmesh.ops.spin(bm, geom=bm.edges, angle=radians(360.0), steps=self.detalization, axis=(0.0, 0.0, 1.0), cent=(0.0, 0.0, 0.0))
		bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
		bmesh.ops.holes_fill(bm, edges=bm.edges, sides=0)

	# Common operations
	# ---------------------------

	if self.curve_seat:
		bmesh.ops.bevel(bm, geom=e_sm[:] + v_sm[:], offset=100.0, offset_type=_offset_type['percent'], segments=self.curve_seat_segments, profile=self.curve_seat_profile, loop_slide=True)
		bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

	return bm
