# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import bmesh

from ..lib import mesh, iterutils
from . import microprong_lib


def _get_obs(context):
    obs = []
    app = obs.append

    for ob in context.selected_objects:
        for con in ob.constraints:
            if con.type == "FOLLOW_PATH":
                app(ob)
                break

    return obs, obs[0].users_collection


def _distribute(context, ob, size):
    obs, colls = _get_obs(context)

    space_data = context.space_data
    use_local_view = bool(space_data.local_view)

    for is_last, parent in iterutils.spot_last(obs):

        if is_last:
            ob_copy = ob
        else:
            ob_copy = ob.copy()

        for coll in colls:
            coll.objects.link(ob_copy)

        if use_local_view:
            ob_copy.local_view_set(space_data, True)

        ob_copy.location.xy = parent.location.xy
        ob_copy.scale *= parent.dimensions.y / size
        ob_copy.parent = parent
        ob_copy.matrix_parent_inverse = parent.matrix_basis.inverted()


def add(self, context):
    bm = bmesh.new()

    w = self.side_x / 2
    l = self.side_y / 2

    coords = (
        ( w,   l,  w + self.side_z1),
        ( w,   l, -w),
        ( 0.0, l, -w - self.side_z2),
        (-w,   l, -w),
        (-w,   l,  w + self.side_z1),
    )

    vs_north = [bm.verts.new(co) for co in coords]
    vs_south = [bm.verts.new((x, -y, z)) for x, y, z in coords]

    bm.faces.new(vs_north)
    bm.faces.new(vs_south).normal_flip()

    es, _ = mesh.bridge_verts(bm, vs_north, vs_south)

    if self.bevel_top:
        edges = (es[0], es[4])
        ofst = self.bevel_top / 100.0 * self.side_x
        bmesh.ops.bevel(
            bm,
            geom=edges,
            affect="EDGES",
            clamp_overlap=False,
            offset=ofst,
            offset_type="OFFSET",
            segments=self.bevel_segments,
            profile=0.5,
        )

    if self.bevel_btm:
        edges = (es[1], es[3])
        ofst = self.bevel_btm / 100.0 * self.side_x
        bmesh.ops.bevel(
            bm,
            geom=edges,
            affect="EDGES",
            clamp_overlap=False,
            offset=ofst,
            offset_type="OFFSET",
            segments=self.bevel_segments,
            profile=0.5,
        )

    if self.bevel_wedge and self.side_z2:
        bmesh.ops.bevel(
            bm,
            geom=(es[2],),
            affect="EDGES",
            clamp_overlap=False,
            offset=self.bevel_wedge,
            offset_type="PERCENT",
            segments=self.bevel_segments,
            profile=0.5,
        )

    if self.bevel_btm or self.bevel_top or (self.bevel_wedge and self.side_z2):
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    ob = microprong_lib.prepare_object(self, bm, follow_path=False)
    _distribute(context, ob, self.size_active)
