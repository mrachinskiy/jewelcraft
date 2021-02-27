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


from typing import List, Iterable, Tuple

import bpy
from bpy.types import Object
import bmesh
from bmesh.types import BMesh, BMVert, BMEdge, BMFace
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

    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="SHORT_EDGE")

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


def connect_verts(bm: BMesh, verts: Iterable[BMVert]) -> List[BMEdge]:
    return [bm.edges.new(x) for x in pairwise_cyclic(verts)]


def bridge_verts(bm: BMesh, v1: Iterable[BMVert], v2: Iterable[BMVert]) -> Tuple[List[BMEdge], List[BMFace]]:
    faces = [bm.faces.new(x) for x in quadwise_cyclic(v1, v2)]
    edges = [f.edges[1] for f in faces]

    return edges, faces


def face_pos() -> List[Matrix]:
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
