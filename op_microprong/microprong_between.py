# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2022  Mikhail Rachinskiy
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
                fp = con
                break

    obs.sort(key=operator.itemgetter(1), reverse=True)

    # Cap ends
    size_1, ofst_1 = obs[0]
    _, ofst_2 = obs[1]
    size_n1, ofst_n1 = obs[-1]
    _, ofst_n2 = obs[-2]

    ofst_start = ofst_1 - (ofst_2 - ofst_1)
    ofst_end = ofst_n1 + (ofst_n1 - ofst_n2)
    is_cyclic = round(ofst_start - 100.0, 2) == round(ofst_n1, 2)

    if is_cyclic:
        app((size_1, ofst_end))
    else:
        obs.insert(0, (size_1, ofst_start))
        app((size_n1, ofst_end))

    return obs, fp.target, fp.id_data.users_collection


def _distribute(context, ob, curve_length):
    obs, curve, colls = _get_obs(context)

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)

    base_unit = 100.0 / curve_length
    first_cycle = True

    for (size1, ofst1), (size2, ofst2) in iterutils.pairwise(obs):

        if first_cycle:
            ob_copy = ob
            first_cycle = False
        else:
            ob_copy = ob.copy()

        for coll in colls:
            coll.objects.link(ob_copy)

        if use_local_view:
            ob_copy.local_view_set(space_data, True)

        con = ob_copy.constraints[0]
        con.offset = (ofst2 + ofst1 - base_unit * (size1 - size2) / 2) / 2
        con.target = curve


def add(self, context):
    bm = bmesh.new()

    w = self.between_x / 2
    l = self.between_y / 2

    coords = (
        ( w,   l,  self.between_z1),
        ( w,   l,  0.0),
        ( 0.0, l, -self.between_z2),
        (-w,   l,  0.0),
        (-w,   l,  self.between_z1),
    )

    vs_north = [bm.verts.new(co) for co in coords]
    vs_south = [bm.verts.new((x, -y, z)) for x, y, z in coords]

    bm.faces.new(vs_north)
    bm.faces.new(vs_south).normal_flip()

    mesh.bridge_verts(bm, vs_north, vs_south)

    ob = microprong_lib.prepare_object(self, bm)
    _distribute(context, ob, self.curve_length)
