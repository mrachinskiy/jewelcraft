# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025-2026 Mikhail Rachinskiy

import math
import sys
import traceback

import bpy


def set_up() -> None:
    bpy.ops.curve.primitive_nurbs_path_add()
    cu = bpy.context.object
    cu.name = "CU"
    cu.dimensions.x = 8

    bpy.ops.mesh.primitive_cube_add()
    ob1 = bpy.context.object
    ob1.name = "OB"

    md = ob1.modifiers.new("CU", "CURVE")
    md.object = cu


def cleanup() -> None:
    for me in bpy.data.meshes:
        bpy.data.meshes.remove(me)

    for me in bpy.data.curves:
        bpy.data.curves.remove(me)

    for ng in bpy.data.node_groups:
        bpy.data.node_groups.remove(ng)

    for coll in bpy.data.collections:
        bpy.data.collections.remove(coll)


def _eq(a: float, b: float) -> bool:
    return abs(a - b) < 1e-6


def test_size() -> None:
    d = 50.0 / math.pi
    bpy.ops.curve.jewelcraft_size_curve_add(diameter=d)
    ob = bpy.context.object

    assert _eq(ob.dimensions.x, d)


def test_stretch() -> None:
    bpy.ops.object.jewelcraft_stretch_along_curve()

    ob = bpy.context.object
    assert _eq(ob.dimensions.x, 8.0)


def test_over_under() -> None:
    ob = bpy.context.object

    bpy.ops.object.jewelcraft_move_over_under(position="OVER")
    assert _eq(ob.location.z, 1.0)

    bpy.ops.object.jewelcraft_move_over_under(position="UNDER")
    assert _eq(ob.location.z, -1.0)

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.jewelcraft_move_over_under(position="OVER")
    bpy.ops.object.editmode_toggle()
    assert _eq(ob.location.z, -1.0)
    assert _eq(ob.bound_box[0][2], 1.0)


def main() -> None:
    for name, test in globals().items():
        if name.startswith("test"):
            set_up()
            test()
            cleanup()


try:
    main()
except:
    traceback.print_exc()
    sys.exit(1)
