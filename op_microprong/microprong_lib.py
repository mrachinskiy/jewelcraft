# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
from mathutils import Matrix

from ..lib import asset


def prepare_object(self, bm, follow_path=True):

    ob_name = "Microprong Cutter"
    me = bpy.data.meshes.new(ob_name)
    bm.to_mesh(me)
    bm.free()

    ob = bpy.data.objects.new(ob_name, me)
    asset.add_material(ob, name="Cutter", color=self.color)

    if self.rot_x:
        ob.matrix_world @= Matrix.Rotation(self.rot_x, 4, "X")

    if self.rot_z:
        ob.matrix_world @= Matrix.Rotation(self.rot_z, 4, "Z")

    if self.loc_z:
        ob.matrix_world @= Matrix.Translation((0.0, 0.0, self.loc_z))

    if follow_path:
        con = ob.constraints.new("FOLLOW_PATH")
        con.use_curve_follow = True
        con.forward_axis = "FORWARD_X"

    return ob
