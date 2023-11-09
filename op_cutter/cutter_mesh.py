# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import bmesh
from mathutils import Vector

from ..lib import gemlib, iterutils, mesh
from . import profiles


def get(self):

    # Section sizes
    # ---------------------------------

    Handle = Vector((
        self.handle_dim.x / 2,
        self.handle_dim.y / 2,
        self.handle_dim.z1,
        self.handle_dim.z2,
    ))
    Girdle = Vector((
        self.gem_dim.x / 2 + self.girdle_dim.x,
        self.gem_dim.y / 2 + self.girdle_dim.y,
        self.girdle_dim.z1,
        -self.girdle_dim.z2,
    ))
    Hole = Vector((
        self.hole_dim.x / 2,
        self.hole_dim.y / 2,
        -self.hole_dim.z1,
        -self.hole_dim.z2,
    ))

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

    if self.cut in {"PEAR", "HEART"}:
        handle_ofst = (0.0, self.handle_shift, 0.0)
        hole_ofst = (0.0, self.hole_shift, 0.0)
    else:
        handle_ofst = hole_ofst = (0.0, 0.0, 0.0)

    if self.cut == "PEAR":
        cullet_pos = (0.0, self.gem_dim.y / 4 - self.hole_shift, Hole.z)
    else:
        cullet_pos = (0.0, 0.0, Hole.z)

    # Section produce
    # ---------------------------------

    bm = bmesh.new()
    parts = []
    Section = profiles.get(self)

    # Handle
    if self.use_handle:
        parts += Section.add(bm, Handle, offset=handle_ofst)

    # Girdle
    if self.cut == "HEART":
        parts += Section.add_z_fmt(bm, Girdle)
    else:
        parts += Section.add(bm, Girdle)
    bm.faces.new(parts[0])

    # Hole/Seat
    if self.use_curve_seat:
        z = (Girdle.w + Hole.z) / 2 * 1.4
        vs = [bm.verts.new((*v.co.xy, z)) for v in parts[-1]]
        parts.append(vs)
        curved_seat_edges = mesh.connect_verts(bm, vs)

    if self.use_hole:
        parts += Section.add(bm, Hole, offset=hole_ofst)
        bm.faces.new(parts[-1]).normal_flip()
    else:
        if self.shape is gemlib.SHAPE_RECTANGLE:
            Section.add_seat_rect(bm, parts[-1], Girdle, Hole)
        else:
            c = bm.verts.new(cullet_pos)
            for a, b in iterutils.pairwise_cyclic(parts[-1]):
                bm.faces.new((c, b, a))

    # Bridge sections
    for a, b in iterutils.pairwise(parts):
        mesh.bridge_verts(bm, a, b)

    if self.use_curve_seat:
        bmesh.ops.bevel(bm, geom=curved_seat_edges, affect="EDGES", offset=100.0, offset_type="PERCENT", segments=self.curve_seat_segments, profile=self.curve_seat_profile, loop_slide=True)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)

    return bm
