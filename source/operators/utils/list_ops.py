# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator


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


class SCENE_OT_ul_save(Operator):
    bl_label = "Save As Default"
    bl_description = "Save as default"
    bl_idname = "scene.jewelcraft_ul_save"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ul = getattr(context.scene.jewelcraft, self.prop)
        ul.serialize()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class SCENE_OT_ul_load(Operator):
    bl_label = "Load Default"
    bl_description = "Load default"
    bl_idname = "scene.jewelcraft_ul_load"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    load_factory: BoolProperty(name="Factory Settings", options={"SKIP_SAVE"})

    def execute(self, context):
        ul = getattr(context.scene.jewelcraft, self.prop)
        ul.deserialize(load_factory=self.load_factory)
        context.area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# Window manager
# ---------------------------


class WM_OT_ul_add(Operator):
    bl_label = "Add Item"
    bl_description = "Add new item to the list"
    bl_idname = "wm.jewelcraft_ul_add"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ul = getattr(context.window_manager.jewelcraft, self.prop)
        ul.add()
        ul.serialize_on_change()
        return {"FINISHED"}


class WM_OT_ul_del(Operator):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "wm.jewelcraft_ul_del"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ul = getattr(context.window_manager.jewelcraft, self.prop)
        ul.remove()
        ul.serialize_on_change()
        return {"FINISHED"}


class WM_OT_ul_clear(Operator):
    bl_label = "Clear List"
    bl_description = "Remove all items"
    bl_idname = "wm.jewelcraft_ul_clear"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ul = getattr(context.window_manager.jewelcraft, self.prop)
        ul.clear()
        ul.serialize_on_change()
        return {"FINISHED"}


class WM_OT_ul_move(Operator):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "wm.jewelcraft_ul_move"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ul = getattr(context.window_manager.jewelcraft, self.prop)
        ul.move(self.move_up)
        ul.serialize_on_change()
        return {"FINISHED"}


class WM_OT_ul_save(Operator):
    bl_label = "Save As Default"
    bl_description = "Save as default"
    bl_idname = "wm.jewelcraft_ul_save"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        ul = getattr(context.window_manager.jewelcraft, self.prop)
        ul.serialize()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_ul_load(Operator):
    bl_label = "Load Default"
    bl_description = "Load default"
    bl_idname = "wm.jewelcraft_ul_load"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    load_factory: BoolProperty(name="Factory Settings", options={"SKIP_SAVE"})

    def execute(self, context):
        ul = getattr(context.window_manager.jewelcraft, self.prop)
        ul.deserialize(load_factory=self.load_factory)
        context.area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
