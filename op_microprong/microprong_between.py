# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import operator

import bmesh
from bpy.types import Collection, Object

from ..lib import iterutils, mesh
from . import microprong_lib


def _get_obs(context, is_cyclic: bool) -> tuple[list[Object], Object, tuple[Collection]]:
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

    if is_cyclic:
        app((size_1, ofst_end))
    else:
        obs.insert(0, (size_1, ofst_start))
        app((size_n1, ofst_end))

    return obs, fp.target, fp.id_data.users_collection


def _distribute(context, ob: Object, curve_length: float, is_cyclic: bool) -> tuple[float, float]:
    obs, curve, colls = _get_obs(context, is_cyclic)

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)

    base_unit = 100.0 / curve_length
    first_cycle = True

    for (size1, ofst1), (size2, ofst2) in iterutils.pairwise(obs):

        offset = (ofst2 + ofst1 - base_unit * (size1 - size2) / 2) / 2

        if first_cycle:
            first_cycle = False
            ob_copy = ob
            start = -offset
        else:
            ob_copy = ob.copy()
            end = -offset

        for coll in colls:
            coll.objects.link(ob_copy)

        if use_local_view:
            ob_copy.local_view_set(space_data, True)

        con = ob_copy.constraints[0]
        con.offset = offset
        con.target = curve

    return start, end


def add(self, context) -> tuple[float, float]:
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
    return _distribute(context, ob, self.curve_length, self.is_cyclic)
