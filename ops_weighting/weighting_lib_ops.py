# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import StringProperty
from bpy.types import Operator

from .. import var
from ..lib import dynamic_list


class WM_OT_weighting_list_add(Operator):
    bl_label = "Add"
    bl_description = "Add materials list to library"
    bl_idname = "wm.jewelcraft_weighting_list_add"
    bl_options = {"INTERNAL"}

    list_name: StringProperty(name="Name", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.alert = not self.list_name
        layout.prop(self, "list_name")
        layout.separator()

    def execute(self, context):
        if not self.list_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        mats = context.scene.jewelcraft.weighting_materials

        lib_path = mats.serialize_path()
        list_path = lib_path / f"{self.list_name}.json"

        mats.serialize(list_path)
        dynamic_list.weighting_lib_refresh()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_weighting_list_replace(Operator):
    bl_label = "Replace"
    bl_description = "Replace materials list"
    bl_idname = "wm.jewelcraft_weighting_list_replace"
    bl_options = {"INTERNAL"}

    list_name: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        mats = context.scene.jewelcraft.weighting_materials

        lib_path = mats.serialize_path()
        list_path = lib_path / f"{self.list_name}.json"

        if list_path.exists():
            mats.serialize(list_path)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_weighting_list_del(Operator):
    bl_label = "Remove"
    bl_description = "Remove from library"
    bl_idname = "wm.jewelcraft_weighting_list_del"
    bl_options = {"INTERNAL"}

    list_name: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        lib_path = context.scene.jewelcraft.weighting_materials.serialize_path()
        list_path = lib_path / f"{self.list_name}.json"
        list_path.unlink(missing_ok=True)
        dynamic_list.weighting_lib_refresh()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_weighting_list_import(Operator):
    bl_label = "Import"
    bl_description = "Import materials list"
    bl_idname = "wm.jewelcraft_weighting_list_import"
    bl_options = {"INTERNAL"}

    load_id: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        context.scene.jewelcraft.weighting_materials.deserialize(self.load_id)
        context.area.tag_redraw()
        return {"FINISHED"}


class WM_OT_weighting_list_set_default(Operator):
    bl_label = "Set Default"
    bl_description = "Set materials list imported by default"
    bl_idname = "wm.jewelcraft_weighting_list_set_default"
    bl_options = {"INTERNAL"}

    load_id: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        prefs.weighting_default_list = self.load_id
        context.preferences.is_dirty = True
        dynamic_list.weighting_lib_refresh()
        return {"FINISHED"}


class WM_OT_weighting_ui_refresh(Operator):
    bl_label = "Refresh"
    bl_description = "Refresh asset UI"
    bl_idname = "wm.jewelcraft_weighting_ui_refresh"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        dynamic_list.weighting_lib_refresh()
        return {"FINISHED"}
