# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import bpy
from bpy.types import Object
from mathutils import Matrix

from ..lib import asset


def prepare_object(self, bm, is_between: bool = True) -> Object:
    ob_name = "Microprong Cutter"
    me = bpy.data.meshes.new(ob_name)
    bm.to_mesh(me)
    bm.free()

    ob = bpy.data.objects.new(ob_name, me)
    asset.add_material(ob, name="Cutter", color=self.color)

    rot_x = self.rot_x
    rot_z = self.rot_z
    loc_z = self.between_loc_z if is_between else self.side_loc_z

    if rot_x:
        ob.matrix_basis @= Matrix.Rotation(rot_x, 4, "X")
    if rot_z:
        ob.matrix_basis @= Matrix.Rotation(rot_z, 4, "Z")
    if loc_z:
        ob.matrix_basis @= Matrix.Translation((0.0, 0.0, loc_z))

    if is_between:
        con = ob.constraints.new("FOLLOW_PATH")
        con.use_curve_follow = True
        con.forward_axis = "FORWARD_X"

    return ob
