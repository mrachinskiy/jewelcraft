# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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


import operator
from itertools import tee

import bpy
import bmesh
from mathutils import Matrix

from .. import var
from ..lib import asset, mesh


def _get_obs(context):
    obs = []
    app = obs.append

    for ob in context.selected_objects:
        for con in ob.constraints:
            if con.type == "FOLLOW_PATH":
                app((ob.dimensions.y, con.offset))
                break

    obs.sort(key=operator.itemgetter(1), reverse=True)

    ob = context.object

    for con in ob.constraints:
        if con.type == "FOLLOW_PATH":
            break
    else:
        ob, con, _ = obs[0]

    return obs, con.target


def _pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def _distribute(context, curve_length, ob):
    obs, curve = _get_obs(context)

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)
    collection = context.collection

    base_unit = 100.0 / curve_length
    first_cycle = True

    for (size1, ofst1), (size2, ofst2) in _pairwise(obs):

        if first_cycle:
            ob_copy = ob
            first_cycle = False
        else:
            ob_copy = ob.copy()

        collection.objects.link(ob_copy)

        if use_local_view:
            ob_copy.local_view_set(space_data, True)

        con = ob_copy.constraints[0]
        con.offset = (ofst2 + ofst1 - base_unit * (size1 - size2) / 2) / 2
        con.target = curve


def execute(self, context):

    # Mesh
    # --------------------------------------

    bm = bmesh.new()

    w_half = self.dim_x / 2
    l_half = self.dim_y / 2

    verts = (
        bm.verts.new((w_half,  -l_half, self.handle_z)),
        bm.verts.new((w_half,  -l_half, 0.0)),
        bm.verts.new((0.0,     -l_half, -self.keel_z)),
        bm.verts.new((-w_half, -l_half, 0.0)),
        bm.verts.new((-w_half, -l_half, self.handle_z)),
    )

    f = bm.faces.new(verts)
    extrude = bmesh.ops.extrude_face_region(bm, geom=(f,))
    extrude_verts = [x for x in extrude["geom"] if isinstance(x, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=extrude_verts, vec=(0.0, self.dim_y, 0.0))

    # Prepeare object
    # --------------------------------------

    ob_name = "Micro Prong Cutter"
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

    con = ob.constraints.new("FOLLOW_PATH")
    con.use_curve_follow = True
    con.forward_axis = "FORWARD_X"

    _distribute(context, self.curve_length, ob)

    return {"FINISHED"}


def invoke(self, context, event):
    curve = None
    obs_count = 0

    for ob in context.selected_objects:

        if obs_count == 2:
            break

        for con in ob.constraints:
            if con.type == "FOLLOW_PATH":
                curve = con.target
                obs_count += 1
                break

    if not curve:
        self.report({"ERROR"}, "Selected objects do not have Follow Path constraint")
        return {"CANCELLED"}

    if obs_count < 2:
        self.report({"ERROR"}, "At least two objects must be selected")
        return {"CANCELLED"}

    prefs = context.preferences.addons[var.ADDON_ID].preferences
    self.color = prefs.color_cutter
    self.curve_length = mesh.est_curve_length(curve)

    wm = context.window_manager
    wm.invoke_props_popup(self, event)
    return self.execute(context)
