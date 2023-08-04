# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import bmesh
from bmesh.types import BMesh, BMVert

from ...lib import mesh, gemlib
from ._types import SectionSize


def _add_rect(bm: BMesh, x: float, y: float, z: float) -> list[BMVert]:
    return [
        bm.verts.new(( x,  y, z)),
        bm.verts.new((-x,  y, z)),
        bm.verts.new((-x, -y, z)),
        bm.verts.new(( x, -y, z)),
    ]


def _add_rect_bevel(self, bm: BMesh, size: SectionSize) -> list[BMVert]:
    if not self.bv_width:
        return _add_rect(bm, *size.xyz)

    bm_temp = bmesh.new()
    vs = _add_rect(bm_temp, *size.xyz)
    bm_temp.faces.new(vs)

    bmesh.ops.bevel(bm_temp, geom=vs, affect="VERTICES", clamp_overlap=True, offset=self.bv_width, offset_type=self.bv_type, segments=self.bv_segments, profile=self.bv_profile)

    f = next(iter(bm_temp.faces))
    verts = [bm.verts.new(v.co) for v in f.verts]
    bm_temp.free()

    return verts


class Section:
    __slots__ = "bv_width", "bv_type", "bv_segments", "bv_profile"

    def __init__(self, operator) -> None:
        if operator.shape is gemlib.SHAPE_RECTANGLE:
            self.bv_type = "OFFSET"
            self.bv_width = operator.bevel_corners_width
        else:
            self.bv_type = "PERCENT"
            self.bv_width = operator.bevel_corners_percent

        self.bv_segments = operator.bevel_corners_segments
        self.bv_profile = operator.bevel_corners_profile

    def add(self, bm: BMesh, size: SectionSize) -> tuple[list[BMVert], list[BMVert]]:
        s1 = _add_rect_bevel(self, bm, size)
        s2 = [bm.verts.new((*v.co.xy, size.z2)) for v in s1]
        return s1, s2

    @staticmethod
    def add_seat_rect(bm: BMesh, girdle_verts: list[BMVert], Girdle: SectionSize, Hole: SectionSize) -> None:
        scale_y = Hole.y / (Girdle.y or Hole.y)
        vs = [bm.verts.new((v.co.x, v.co.y * scale_y, Hole.z1)) for v in girdle_verts]
        es = mesh.connect_verts(bm, vs)
        mesh.bridge_verts(bm, girdle_verts, vs)

        es1 = []
        es2 = []
        app1 = es1.append
        app2 = es2.append

        for e in es:
            v1, v2 = e.verts
            if v1.co.y > 0.0 and v2.co.y > 0.0:
                app1(e)
            elif v1.co.y < 0.0 and v2.co.y < 0.0:
                app2(e)

        bmesh.ops.collapse(bm, edges=es1)
        bmesh.ops.collapse(bm, edges=es2)
