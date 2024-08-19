# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator

from ..lib import data


# Scene
# ---------------------------


class SCENE_OT_ul_del(Operator):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "scene.jewelcraft_ul_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.scene.jewelcraft, self.prop).remove()
        return {"FINISHED"}


class SCENE_OT_ul_clear(Operator):
    bl_label = "Clear List"
    bl_description = "Remove all items"
    bl_idname = "scene.jewelcraft_ul_clear"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.scene.jewelcraft, self.prop).clear()
        return {"FINISHED"}


class SCENE_OT_ul_move(Operator):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "scene.jewelcraft_ul_move"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.scene.jewelcraft, self.prop).move(self.move_up)
        return {"FINISHED"}


# Window manager
# ---------------------------


def _serialize(prop: str) -> None:
    if prop == "gem_colors":
        data.gem_colors_serialize()
    elif prop == "asset_libs":
        data.asset_libs_serialize()
    elif prop == "report_metadata":
        data.report_metadata_serialize()


class WM_OT_ul_add(Operator):
    bl_label = "Add Item"
    bl_description = "Add new item to the list"
    bl_idname = "wm.jewelcraft_ul_add"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.window_manager.jewelcraft, self.prop).add()
        _serialize(self.prop)
        return {"FINISHED"}


class WM_OT_ul_del(Operator):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "wm.jewelcraft_ul_del"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.window_manager.jewelcraft, self.prop).remove()
        _serialize(self.prop)
        return {"FINISHED"}


class WM_OT_ul_clear(Operator):
    bl_label = "Clear List"
    bl_description = "Remove all items"
    bl_idname = "wm.jewelcraft_ul_clear"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.window_manager.jewelcraft, self.prop).clear()
        _serialize(self.prop)
        return {"FINISHED"}


class WM_OT_ul_move(Operator):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "wm.jewelcraft_ul_move"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.window_manager.jewelcraft, self.prop).move(self.move_up)
        _serialize(self.prop)
        return {"FINISHED"}
