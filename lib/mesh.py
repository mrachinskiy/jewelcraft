# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterable

import bmesh
import bpy
from bmesh.types import BMEdge, BMesh, BMFace, BMVert
from bpy.types import Object
from mathutils import Matrix

from .iterutils import pairwise_cyclic, quadwise_cyclic


def est_volume(obs: Iterable[Object]) -> float:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()

    for ob in obs:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(ob.matrix_world)

        bm.from_mesh(me)

        ob_eval.to_mesh_clear()

    bmesh.ops.triangulate(bm, faces=bm.faces)

    vol = bm.calc_volume()
    bm.free()

    return vol


def est_curve_length(ob: Object) -> float:
    if ob.modifiers:

        # Reset curve
        # ---------------------------

        settings = {
            "bevel_object": None,
            "bevel_depth": 0.0,
            "extrude": 0.0,
        }

        for k, v in settings.items():
            x = getattr(ob.data, k)
            setattr(ob.data, k, v)
            settings[k] = x

        # Calculate length
        # ---------------------------

        depsgraph = bpy.context.evaluated_depsgraph_get()
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(ob.matrix_world)

        bm = bmesh.new()
        bm.from_mesh(me)

        ob_eval.to_mesh_clear()

        length = 0.0

        for edge in bm.edges:
            length += edge.calc_length()

        bm.free()

        # Restore curve
        # ---------------------------

        for k, v in settings.items():
            setattr(ob.data, k, v)

    else:

        curve = ob.data.copy()
        curve.transform(ob.matrix_world)

        length = 0.0

        for spline in curve.splines:
            length += spline.calc_length()

        bpy.data.curves.remove(curve)

    return length


def connect_verts(bm: BMesh, verts: list[BMVert]) -> list[BMEdge]:
    return [bm.edges.new(x) for x in pairwise_cyclic(verts)]


def bridge_verts(bm: BMesh, v1: list[BMVert], v2: list[BMVert]) -> tuple[list[BMEdge], list[BMFace]]:
    faces = [bm.faces.new(x) for x in quadwise_cyclic(v1, v2)]
    edges = [f.edges[1] for f in faces]

    return edges, faces


def face_pos() -> list[Matrix]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mats = []

    for ob in bpy.context.objects_in_mode:
        ob.update_from_editmode()
        depsgraph.update()

        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(ob.matrix_world)

        for poly in me.polygons:
            if poly.select:
                mat_loc = Matrix.Translation(poly.center)
                mat_rot = poly.normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
                mat = mat_loc @ mat_rot

                mats.append(mat)

        ob_eval.to_mesh_clear()

    return mats
