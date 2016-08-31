# ##### BEGIN GPL LICENSE BLOCK #####
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# 
# ##### END GPL LICENSE BLOCK #####

# Copyright (c) Campbell Barton

import bmesh


def bmesh_copy_from_object(ob, transform=True, triangulate=True, apply_modifiers=True):

	assert(obj.type == 'MESH')

		import bpy
		bm = bmesh.new()
		bm.from_mesh(me)
		bpy.data.meshes.remove(me)
		del bpy
	else:
			bm_orig = bmesh.from_edit_mesh(me)
			bm = bm_orig.copy()
		else:
			bm = bmesh.new()
			bm.from_mesh(me)

	if transform:

	if triangulate:
		bmesh.ops.triangulate(bm, faces=bm.faces)

	return bm


	volume = bm.calc_volume()
	bm.free()
	return volume
