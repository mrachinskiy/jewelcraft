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


from collections.abc import Iterator

import bmesh
from bmesh.types import BMesh, BMVert

from ...lib import mesh


def _add_tri(bm: BMesh, x: float, y: float, z: float) -> list[BMVert]:
    return [
        bm.verts.new(co)
        for co in (
            (  x,  y / 3.0, z),
            ( -x,  y / 3.0, z),
            (0.0, -y / 1.5, z),
        )
    ]


def _add_tri_bevel(
    bm: BMesh,
    x: float,
    y: float,
    z: float,
    bv_width: float,
    bv_type: str,
    bv_segments: int,
    bv_profile: float,
    curve_factor: float,
    curve_segments: int,
) -> list[BMVert]:
    bm_temp = bmesh.new()
    vs = _add_tri(bm_temp, x, y, 0.0)
    es = mesh.connect_verts(bm_temp, vs)

    if bv_width:
        bv = bmesh.ops.bevel(
            bm_temp,
            geom=vs,
            affect="VERTICES",
            clamp_overlap=True,
            offset=bv_width,
            offset_type=bv_type,
            segments=bv_segments,
            profile=bv_profile,
        )
        es = tuple(set(bm_temp.edges) - set(bv["edges"]))

    if curve_factor:
        bm_temp.normal_update()
        bmesh.ops.subdivide_edges(
            bm_temp,
            edges=es,
            smooth=curve_factor,
            smooth_falloff="LINEAR",
            cuts=curve_segments,
        )

    f = bm_temp.faces.new(_edge_loop_walk(bm_temp.verts))
    f.normal_update()
    if f.normal.z < 0.0:
        f.normal_flip()

    verts = [bm.verts.new((*v.co.xy, z)) for v in f.verts]
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
        "bv_width",
        "bv_type",
        "bv_segments",
        "bv_profile",
        "add",
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

        if self.bv_width or self.curve_factor:
            self.add = self._add_bevel
        else:
            self.add = self._add

    @staticmethod
    def _add(bm: BMesh, size) -> tuple[list[BMVert], list[BMVert]]:
        s1 = _add_tri(bm, size.x, size.y, size.z1)
        s2 = [bm.verts.new((*v.co.xy, size.z2)) for v in s1]
        return s1, s2

    def _add_bevel(self, bm: BMesh, size) -> tuple[list[BMVert], list[BMVert]]:
        s1 = _add_tri_bevel(
            bm,
            size.x,
            size.y,
            size.z1,
            self.bv_width,
            self.bv_type,
            self.bv_segments,
            self.bv_profile,
            self.curve_factor,
            self.curve_segments,
        )
        s2 = [bm.verts.new((*v.co.xy, size.z2)) for v in s1]
        return s1, s2
