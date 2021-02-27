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


import bmesh

from ..lib import mesh, iterutils
from . import microprong_lib


def _get_obs(context):
    obs = []
    app = obs.append

    for ob in context.selected_objects:
        for con in ob.constraints:
            if con.type == "FOLLOW_PATH":
                app((ob, con))
                break

    return obs


def _distribute(context, ob, size):
    obs = _get_obs(context)

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)
    collection = context.collection

    for is_last, (parent, pcon) in iterutils.spot_last(obs):

        if is_last:
            ob_copy = ob
        else:
            ob_copy = ob.copy()

        collection.objects.link(ob_copy)

        if use_local_view:
            ob_copy.local_view_set(space_data, True)

        ob_copy.location += parent.location
        ob_copy.scale *= parent.dimensions.y / size

        con = ob_copy.constraints[0]
        con.offset = pcon.offset
        con.target = pcon.target


def execute(self, context):
    bm = bmesh.new()

    w = self.dim_x / 2
    l = self.dim_y / 2

    coords = (
        ( w, l,  w + self.handle_z),
        ( w, l, -w),
        (-w, l, -w),
        (-w, l,  w + self.handle_z),
    )

    vs_north = [bm.verts.new(co) for co in coords]
    vs_south = [bm.verts.new((x, -y, z)) for x, y, z in coords]

    bm.faces.new(vs_north)
    bm.faces.new(vs_south).normal_flip()

    es, _ = mesh.bridge_verts(bm, vs_north, vs_south)

    if self.bevel_btm:
        edges = (es[1], es[2])
        ofst = self.bevel_btm / 100.0 * self.dim_x
        bmesh.ops.bevel(
            bm,
            geom=edges,
            affect="EDGES",
            clamp_overlap=False,
            offset=ofst,
            offset_type="OFFSET",
            segments=self.bevel_segments, profile=0.5,
        )

    if self.bevel_top:
        edges = (es[0], es[3])
        ofst = self.bevel_top / 100.0 * self.dim_x
        bmesh.ops.bevel(
            bm,
            geom=edges,
            affect="EDGES",
            clamp_overlap=False,
            offset=ofst,
            offset_type="OFFSET",
            segments=self.bevel_segments, profile=0.5,
        )

    if self.bevel_btm or self.bevel_top:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    ob = microprong_lib.prepare_object(self, bm)
    _distribute(context, ob, self.size_active)

    return {"FINISHED"}
