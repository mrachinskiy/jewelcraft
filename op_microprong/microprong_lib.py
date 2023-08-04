# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

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
