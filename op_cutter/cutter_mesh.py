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
from mathutils import Matrix

from ..lib import iterutils, mesh, gemlib
from . import profiles


class _SectionSize:
    __slots__ = "x", "y", "z1", "z2"

    def __init__(self, x: float, y: float, z1: float, z2: float) -> None:
        self.x = x
        self.y = y
        self.z1 = z1
        self.z2 = z2

    @property
    def xyz(self):
        return self.x, self.y, self.z1


def get(self):
    bm = bmesh.new()

    # Section sizes
    # ---------------------------------

    Handle = _SectionSize(
        self.handle_dim.x / 2,
        self.handle_dim.y / 2,
        self.handle_dim.z1,
        self.handle_dim.z2,
    )
    Girdle = _SectionSize(
        self.gem_dim.x / 2 + self.girdle_dim.x,
        self.gem_dim.y / 2 + self.girdle_dim.y,
        self.girdle_dim.z1,
        -self.girdle_dim.z2,
    )
    Hole = _SectionSize(
        self.hole_dim.x / 2,
        self.hole_dim.y / 2,
        -self.hole_dim.z1,
        -self.hole_dim.z2,
    )

    if self.shape is gemlib.SHAPE_SQUARE:
        Handle.x = Handle.y
        Girdle.x = Girdle.y
        Hole.x = Hole.y
    elif self.shape is gemlib.SHAPE_TRIANGLE:
        Handle.y = self.handle_dim.y
        Girdle.y = self.gem_dim.y + self.girdle_dim.y
        Hole.y = self.hole_dim.y
    elif self.cut in {"OVAL", "MARQUISE", "PEAR"}:
        Girdle.x = self.gem_dim.x / 2 + self.girdle_dim.y

    # Section produce
    # ---------------------------------

    parts = []
    Section = profiles.sections[self.shape](self)

    # Handle
    if self.use_handle:
        parts += Section.add(bm, Handle)

        if self.cut in {"PEAR", "HEART"}:
            bm.transform(Matrix.Translation((0.0, self.handle_shift, 0.0)))

    # Girdle
    if self.cut == "HEART":
        parts += Section.add_preserve_z2(bm, Girdle)
    else:
        parts += Section.add(bm, Girdle)
    bm.faces.new(parts[0])

    # Hole/Seat
    if self.use_curve_seat:
        z = (Girdle.z2 + Hole.z1) / 2 * 1.4
        vs = [bm.verts.new((*v.co.xy, z)) for v in parts[-1]]
        e_seat = mesh.connect_verts(bm, vs)
        parts.append(vs)

    if self.use_hole:
        parts += Section.add(bm, Hole)
        bm.faces.new(parts[-1]).normal_flip()

        if self.cut in {"PEAR", "HEART"}:
            for verts in parts[-2:]:
                for v in verts:
                    v.co.y += self.hole_shift
    else:
        if self.shape is gemlib.SHAPE_RECTANGLE:
            Section.add_seat_rect(bm, parts[-1], Girdle, Hole)
        else:
            v3 = bm.verts.new((0.0, 0.0, Hole.z1))
            for v1, v2 in iterutils.pairwise_cyclic(parts[-1]):
                bm.faces.new((v3, v2, v1))

            if self.cut == "PEAR":
                v3.co.y = self.gem_dim.y / 4 - self.hole_shift

    # Bridge sections
    for a, b in iterutils.pairwise(parts):
        mesh.bridge_verts(bm, a, b)

    if self.use_curve_seat:
        bmesh.ops.bevel(bm, geom=e_seat, affect="EDGES", offset=100.0, offset_type="PERCENT", segments=self.curve_seat_segments, profile=self.curve_seat_profile, loop_slide=True)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)

    return bm
