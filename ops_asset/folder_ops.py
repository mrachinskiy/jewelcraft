# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import StringProperty
from bpy.types import Operator

from ..lib import dynamic_list


class WM_OT_asset_folder_create(Operator):
    bl_label = "Create Category"
    bl_description = "Create category"
    bl_idname = "wm.jewelcraft_asset_folder_create"
    bl_options = {"INTERNAL"}

    folder_name: StringProperty(name="Category Name", description="Category name", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.alert = not self.folder_name
        layout.prop(self, "folder_name")
        layout.separator()

    def execute(self, context):
        if not self.folder_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        wm_props = context.window_manager.jewelcraft
        folder = wm_props.asset_libs.path() / self.folder_name

        if not folder.exists():
            folder.mkdir(parents=True)
            dynamic_list.asset_folders_refresh()
            wm_props.asset_folder = self.folder_name
            context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_asset_folder_rename(Operator):
    bl_label = "Rename Category"
    bl_description = "Rename category"
    bl_idname = "wm.jewelcraft_asset_folder_rename"
    bl_options = {"INTERNAL"}

    folder_name: StringProperty(name="Category Name", description="Category name", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.alert = not self.folder_name
        layout.prop(self, "folder_name")
        layout.separator()

    def execute(self, context):
        if not self.folder_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        props = context.window_manager.jewelcraft

        if self.folder_name == props.asset_folder:
            return {"CANCELLED"}

        lib_path = props.asset_libs.path()
        folder = lib_path / props.asset_folder
        folder_new = lib_path / self.folder_name

        if folder.exists():
            folder.rename(folder_new)
            dynamic_list.asset_folders_refresh()
            props.asset_folder = self.folder_name
            context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        self.folder_name = context.window_manager.jewelcraft.asset_folder
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_asset_ui_refresh(Operator):
    bl_label = "Refresh"
    bl_description = "Refresh asset UI"
    bl_idname = "wm.jewelcraft_asset_ui_refresh"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.window_manager.jewelcraft.asset_libs.deserialize()
        dynamic_list.asset_folders_refresh()
        dynamic_list.assets_refresh("ALL", favs=True)
        context.area.tag_redraw()
        return {"FINISHED"}
