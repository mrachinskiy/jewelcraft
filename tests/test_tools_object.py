# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025-2026 Mikhail Rachinskiy

import sys
import traceback

import bpy


def set_up() -> None:
    bpy.ops.mesh.primitive_cube_add()
    ob1 = bpy.context.object
    ob1.name = "OB"


def cleanup() -> None:
    for me in bpy.data.meshes:
        bpy.data.meshes.remove(me)

    for ng in bpy.data.node_groups:
        bpy.data.node_groups.remove(ng)

    for coll in bpy.data.collections:
        bpy.data.collections.remove(coll)


def _eq(a: float, b: float) -> bool:
    return abs(a - b) < 1e-6


def test_mirror() -> None:
    ob = bpy.context.object
    bpy.ops.object.jewelcraft_mirror(collection_name=bpy.context.object.name, x=True)

    assert bpy.context.object.name == f"{ob.name} Mirror Instance"
    assert ob.name in bpy.context.scene.collection.children
    assert len(ob.users_collection) == 1
    assert ob.users_collection[0] is bpy.context.scene.collection.children[ob.name]


def test_radial() -> None:
    ob = bpy.context.object
    bpy.ops.object.jewelcraft_radial_instance(collection_name=bpy.context.object.name, count=3)

    assert bpy.context.object.name == f"{ob.name} Radial Instance"
    assert ob.name in bpy.context.scene.collection.children
    assert len(ob.users_collection) == 1
    assert ob.users_collection[0] is bpy.context.scene.collection.children[ob.name]


def test_instance_face() -> None:
    ob = bpy.context.object
    bpy.ops.object.jewelcraft_instance_face(collection_name=bpy.context.object.name)

    assert bpy.context.object.name == f"{ob.name} Instance Face"
    assert ob.name in bpy.context.scene.collection.children
    assert len(ob.users_collection) == 1
    assert ob.users_collection[0] is bpy.context.scene.collection.children[ob.name]


def test_resize() -> None:
    bpy.context.object.scale = 1.0, 2.0, 3.0
    cases = (
        ("X", 4.0, (4.0, 8.0, 12.0)),
        ("Y", 2.0, (1.0, 2.0, 3.0)),
        ("Z", 9.0, (3.0, 6.0, 9.0)),
    )

    for axis, size, result in cases:
        bpy.ops.object.jewelcraft_resize(axis=axis, size=size, dimensions=bpy.context.object.dimensions)
        assert bpy.context.object.dimensions.to_tuple(5) == result, axis


def test_lattice_profile() -> None:
    ob = bpy.context.object
    bpy.ops.object.jewelcraft_lattice_profile()
    assert bpy.context.object.name == "Lattice Profile"
    assert ob.dimensions.xy.to_tuple(5) == (2.0, 2.0)
    assert ob.dimensions.z < 2.0


def test_lattice_project() -> None:
    ob1 = bpy.context.object

    bpy.ops.mesh.primitive_cube_add()
    ob2 = bpy.context.object
    ob2.location.z = -3.0

    ob1.select_set(True)

    bpy.ops.object.jewelcraft_lattice_project(direction="NEG_Z")
    assert bpy.context.object.name == "Lattice Project"
    assert _eq(ob1.bound_box[1][2], 0.0)


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
