# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025-2026 Mikhail Rachinskiy

import sys
import traceback

import bpy
from bpy.types import Object


def _ob_copy(ob: Object) -> Object:
    ob_copy = ob.copy()
    bpy.context.collection.objects.link(ob_copy)
    return ob_copy


def set_up() -> None:
    bpy.ops.object.jewelcraft_gem_add(cut="ROUND", stone="DIAMOND")
    g1 = bpy.context.object
    g1.name = "G1"

    g2 = _ob_copy(g1)
    g2.name = "G2"
    g2.location.x = 1.2

    g3 = _ob_copy(g1)
    g3.name = "G3"
    g3.location.x = 2.2


def cleanup() -> None:
    for me in bpy.data.meshes:
        bpy.data.meshes.remove(me)

    for coll in bpy.data.collections:
        bpy.data.collections.remove(coll)


def test_edit_gem() -> None:
    ob = bpy.context.object
    n_verts = len(ob.data.vertices)
    mat = ob.active_material

    bpy.ops.object.jewelcraft_gem_edit(cut="SQUARE", stone="RUBY", edit_id=False, edit_mesh=False, edit_mat=False)
    assert ob["gem"]["cut"] == "ROUND"
    assert ob["gem"]["stone"] == "DIAMOND"
    assert len(ob.data.vertices) == n_verts
    assert ob.active_material is mat

    bpy.ops.object.jewelcraft_gem_edit(cut="SQUARE", stone="RUBY", edit_id=True, edit_mesh=True, edit_mat=True)
    assert ob["gem"]["cut"] == "SQUARE"
    assert ob["gem"]["stone"] == "RUBY"
    assert len(ob.data.vertices) != n_verts
    assert ob.active_material is not mat


def test_recover_gem() -> None:
    n_gems = len(bpy.context.scene.objects)
    assert n_gems > 1

    for ob in bpy.context.scene.objects:
        ob.select_set(True)
    bpy.ops.object.join()
    assert len(bpy.context.scene.objects) == 1

    bpy.ops.object.jewelcraft_gem_recover()
    assert len(bpy.context.scene.objects) == n_gems


def test_select_by_trait() -> None:
    assert len(bpy.context.selected_objects) == 3
    bpy.ops.object.jewelcraft_gem_select_by_trait(filter_size=True, size=2)
    assert len(bpy.context.selected_objects) == 0
    bpy.ops.object.jewelcraft_gem_select_by_trait(filter_size=True, size=1)
    assert len(bpy.context.selected_objects) == 3


def test_select_overlapping() -> None:
    assert len(bpy.context.selected_objects) == 3
    bpy.ops.object.jewelcraft_gem_select_overlapping()
    assert len(bpy.context.selected_objects) == 2


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
