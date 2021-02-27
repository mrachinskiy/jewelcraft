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


import operator

import bmesh

from ..lib import mesh, iterutils
from . import microprong_lib


def _get_obs(context):
    obs = []
    app = obs.append

    for ob in context.selected_objects:
        for con in ob.constraints:
            if con.type == "FOLLOW_PATH":
                app((ob.dimensions.y, con.offset))
                break

    obs.sort(key=operator.itemgetter(1), reverse=True)

    return obs, con.target


def _distribute(context, curve_length, ob):
    obs, curve = _get_obs(context)

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)
    collection = context.collection

    base_unit = 100.0 / curve_length
    first_cycle = True

    for (size1, ofst1), (size2, ofst2) in iterutils.pairwise(obs):

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
    bm = bmesh.new()

    w = self.dim_x / 2
    l = self.dim_y / 2

    coords = (
        ( w,   l,  self.handle_z),
        ( w,   l,  0.0),
        ( 0.0, l, -self.wedge_z),
        (-w,   l,  0.0),
        (-w,   l,  self.handle_z),
    )

    vs_north = [bm.verts.new(co) for co in coords]
    vs_south = [bm.verts.new((x, -y, z)) for x, y, z in coords]

    bm.faces.new(vs_north)
    bm.faces.new(vs_south).normal_flip()

    mesh.bridge_verts(bm, vs_north, vs_south)

    ob = microprong_lib.prepare_object(self, bm)
    _distribute(context, self.curve_length, ob)

    return {"FINISHED"}
