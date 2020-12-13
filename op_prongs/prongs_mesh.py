# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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


from typing import List
from math import pi, tau, sin, cos

import bmesh
from bmesh.types import BMesh, BMVert, BMFace
from mathutils import Matrix

from ..lib import iterutils, mesh


def _circle(bm: BMesh, radius: float, height: float, detalization: int) -> List[BMVert]:
    angle = tau / detalization

    return [
        bm.verts.new(
            (
                sin(i * angle) * radius,
                cos(i * angle) * radius,
                height,
            )
        )
        for i in range(detalization)
    ]


def _dome(bm: BMesh, radius: float, height: float, scale: float, detalization: int) -> List[BMVert]:
    curve_resolution = int(detalization / 4) + 1
    angle = (pi / 2) / (curve_resolution - 1)
    zero_loop = True
    first_loop = True

    for i in range(curve_resolution):

        y = sin(i * angle) * radius
        z = cos(i * angle) * radius * scale + height

        if zero_loop:
            zero_loop = False
            pole_z = z
            continue

        step = _circle(bm, y, z, detalization)

        if first_loop:
            first_loop = False
            pole = step
        else:
            mesh.bridge_verts(bm, step, prev_step)

        prev_step = step

    v3 = bm.verts.new((0.0, 0.0, pole_z))
    for v1, v2 in iterutils.pairwise_cyclic(pole):
        bm.faces.new((v3, v2, v1))

    return step


def create_prongs(self):

    # Prong
    # ---------------------------

    prong_rad = self.diameter / 2
    taper = self.taper + 1
    bm = bmesh.new()

    if self.bump_scale:
        top = _dome(bm, prong_rad, self.z_top, self.bump_scale, self.detalization)
    else:
        top = _circle(bm, prong_rad, self.z_top, self.detalization)
        bm.faces.new(top).normal_flip()

    bottom = _circle(bm, prong_rad * taper, -self.z_btm, self.detalization)
    bm.faces.new(bottom)
    mesh.bridge_verts(bm, bottom, top)

    # Transforms
    # ---------------------------

    pos_offset = (self.gem_l / 2 + prong_rad) - (self.diameter * (self.intersection / 100))
    spin_steps = self.number - 1

    if self.alignment:
        bm.transform(Matrix.Rotation(-self.alignment, 4, "X"))

    bm.transform(Matrix.Translation((0.0, pos_offset, 0.0)))

    if spin_steps:
        spin_angle = tau - tau / self.number
        bmesh.ops.spin(bm, geom=bm.faces, angle=spin_angle, steps=spin_steps, axis=(0.0, 0.0, 1.0), cent=(0.0, 0.0, 0.0), use_duplicate=True)

    bm.transform(Matrix.Rotation(-self.position, 4, "Z"))

    if self.use_symmetry:
        mirror_geom = bmesh.ops.mirror(bm, geom=bm.faces, merge_dist=0, axis="Y")
        for ele in mirror_geom["geom"]:
            if isinstance(ele, BMFace):
                ele.normal_flip()
        bm.transform(Matrix.Rotation(-self.symmetry_pivot, 4, "Z"))

    return bm
