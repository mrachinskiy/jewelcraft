# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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


from math import pi, tau, sin, cos

import bmesh
from mathutils import Matrix


def create_prongs(self):

    # Prong
    # ---------------------------

    prong_rad = self.diameter / 2
    taper = self.taper + 1

    if self.bump_scale:

        curve_resolution = int(self.detalization / 4) + 1
        angle = (pi / 2) / (curve_resolution - 1)

        v_cos = []
        v_co_app = v_cos.append
        x = 0.0

        for i in range(curve_resolution):
            y = sin(i * angle) * prong_rad
            z = cos(i * angle) * prong_rad * self.bump_scale + self.z_top
            v_co_app((x, y, z))

        v_co_app((x, prong_rad * taper, -self.z_btm))

    else:

        v_cos = (
            (0.0, 0.0,                self.z_top),
            (0.0, prong_rad,          self.z_top),
            (0.0, prong_rad * taper, -self.z_btm),
        )

    bm = bmesh.new()
    v_profile = [bm.verts.new(v) for v in v_cos]

    for i in range(len(v_profile) - 1):
        bm.edges.new((v_profile[i], v_profile[i + 1]))

    bmesh.ops.spin(bm, geom=bm.edges, angle=tau, steps=self.detalization, axis=(0.0, 0.0, 1.0), cent=(0.0, 0.0, 0.0))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)

    v_boundary = [x for x in bm.verts if x.is_boundary]
    bm.faces.new(reversed(v_boundary))

    # Transforms
    # ---------------------------

    pos_offset = (self.gem_l / 2 + prong_rad) - (self.diameter * (self.intersection / 100))
    spin_steps = self.number - 1

    if self.alignment:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=Matrix.Rotation(-self.alignment, 4, "X"))

    bmesh.ops.translate(bm, verts=bm.verts, vec=(0.0, pos_offset, 0.0))

    if spin_steps:
        spin_angle = tau - tau / self.number
        bmesh.ops.spin(bm, geom=bm.faces, angle=spin_angle, steps=spin_steps, axis=(0.0, 0.0, 1.0), cent=(0.0, 0.0, 0.0), use_duplicate=True)

    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=Matrix.Rotation(-self.position, 4, "Z"))

    if self.symmetry:
        bmesh.ops.mirror(bm, geom=bm.faces, merge_dist=0, axis="Y")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=Matrix.Rotation(-self.symmetry_pivot, 4, "Z"))

    return bm
