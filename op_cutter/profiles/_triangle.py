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


from collections.abc import Iterator

import bmesh
from bmesh.types import BMesh, BMVert

from ...lib import mesh
from ._types import SectionSize


def _add_tri(bm: BMesh, x: float, y: float, z: float) -> list[BMVert]:
    return [
        bm.verts.new((  x,  y / 3.0, z)),
        bm.verts.new(( -x,  y / 3.0, z)),
        bm.verts.new((0.0, -y / 1.5, z)),
    ]


def _add_tri_bevel(self, bm: BMesh, size: SectionSize) -> list[BMVert]:
    if not (self.bv_width or self.curve_factor):
        return _add_tri(bm, *size.xyz)

    bm_temp = bmesh.new()
    vs = _add_tri(bm_temp, size.x, size.y, 0.0)
    es = mesh.connect_verts(bm_temp, vs)

    if self.bv_width:
        bv = bmesh.ops.bevel(bm_temp, geom=vs, affect="VERTICES", clamp_overlap=True, offset=self.bv_width, offset_type=self.bv_type, segments=self.bv_segments, profile=self.bv_profile)
        es = tuple(set(bm_temp.edges) - set(bv["edges"]))

    if self.curve_factor:
        bm_temp.normal_update()
        bmesh.ops.subdivide_edges(bm_temp, edges=es, smooth=self.curve_factor, smooth_falloff="LINEAR", cuts=self.curve_segments)

    f = bm_temp.faces.new(_edge_loop_walk(bm_temp.verts))
    f.normal_update()
    if f.normal.z < 0.0:
        f.normal_flip()

    verts = [bm.verts.new((*v.co.xy, size.z1)) for v in f.verts]
    bm_temp.free()

    return verts


def _edge_loop_walk(verts: list[BMVert]) -> Iterator[BMVert]:
    v0 = v = next(iter(verts))
    e = v.link_edges[1]
    ov = e.other_vert(v)

    yield v

    while ov is not v0:

        yield ov
        v = ov

        for oe in ov.link_edges:
            if oe != e:
                e = oe
                break

        ov = e.other_vert(v)


class Section:
    __slots__ = (
        "bv_type",
        "bv_width",
        "bv_segments",
        "bv_profile",
        "curve_factor",
        "curve_segments",
    )

    def __init__(self, operator) -> None:
        self.bv_type = "PERCENT"
        self.bv_width = operator.bevel_corners_percent
        self.bv_segments = operator.bevel_corners_segments
        self.bv_profile = operator.bevel_corners_profile
        self.curve_factor = operator.curve_profile_factor
        self.curve_segments = operator.curve_profile_segments

    def add(self, bm: BMesh, size: SectionSize) -> tuple[list[BMVert], list[BMVert]]:
        s1 = _add_tri_bevel(self, bm, size)
        s2 = [bm.verts.new((*v.co.xy, size.z2)) for v in s1]
        return s1, s2
