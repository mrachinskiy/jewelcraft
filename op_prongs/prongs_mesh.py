# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
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


from math import sin, cos, pi

import bmesh
from mathutils import Matrix


tau = pi * 2


def create_prongs(self):
    prong_size = self.diameter / 2
    taper = self.taper + 1

    if self.bump_scale == 0.0:

        v_cos = (
            (0.0, 0.0,                 self.z_top),
            (0.0, prong_size,          self.z_top),
            (0.0, prong_size * taper, -self.z_btm),
        )

    else:

        curve_resolution = int(self.detalization / 4) + 1
        angle = (pi / 2) / (curve_resolution - 1)

        v_cos = []
        v_co_app = v_cos.append

        for i in range(curve_resolution):
            x = 0.0
            y = sin(i * angle) * prong_size
            z = cos(i * angle) * prong_size * self.bump_scale + self.z_top
            v_co_app((x, y, z))

        v_co_app((x, prong_size * taper, -self.z_btm))

    bm = bmesh.new()

    v_profile = [bm.verts.new(v) for v in v_cos]

    for i in range(len(v_profile) - 1):
        bm.edges.new((v_profile[i], v_profile[i + 1]))

    bmesh.ops.spin(bm, geom=bm.edges, angle=tau, steps=self.detalization, axis=(0.0, 0.0, 1.0), cent=(0.0, 0.0, 0.0))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    v_boundary = [x for x in bm.verts if x.is_boundary]
    bm.faces.new(reversed(v_boundary))

    if self.alignment != 0.0:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=Matrix.Rotation(-self.alignment, 4, "X"))

    offset = (self.gem_l / 2) + prong_size - (prong_size * 2) * (self.intersection / 100)
    spin_dupl = self.number - 1
    spin_angle = tau - tau / self.number

    bmesh.ops.translate(bm, verts=bm.verts, vec=(0.0, offset, 0.0))

    if spin_dupl > 0:
        bmesh.ops.spin(bm, geom=bm.faces, angle=spin_angle, steps=spin_dupl, axis=(0.0, 0.0, 1.0), cent=(0.0, 0.0, 0.0), use_duplicate=True)

    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=Matrix.Rotation(-self.position, 4, "Z"))

    if self.symmetry:
        bmesh.ops.mirror(bm, geom=bm.faces, merge_dist=0, axis=1)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=Matrix.Rotation(-self.symmetry_pivot, 4, "Z"))

    return bm
