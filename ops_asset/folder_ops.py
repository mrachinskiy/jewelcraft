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


import os

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from ..lib import asset, dynamic_list


class Setup:

    def __init__(self):
        self.props = bpy.context.window_manager.jewelcraft
        self.folder_name = self.props.asset_folder
        self.folder = os.path.join(asset.user_asset_library_folder_object(), self.folder_name)


class WM_OT_asset_folder_create(Setup, Operator):
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
        layout.prop(self, "folder_name")
        layout.separator()

    def execute(self, context):
        if not self.folder_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        folder = os.path.join(asset.user_asset_library_folder_object(), self.folder_name)

        if not os.path.exists(folder):
            os.makedirs(folder)
            dynamic_list.asset_folder_list_refresh()
            self.props.asset_folder = self.folder_name

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_asset_folder_rename(Setup, Operator):
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
        layout.prop(self, "folder_name")
        layout.separator()

    def execute(self, context):
        if not self.folder_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        folder_new = os.path.join(asset.user_asset_library_folder_object(), self.folder_name)

        if os.path.exists(self.folder):
            os.rename(self.folder, folder_new)
            dynamic_list.asset_folder_list_refresh()
            self.props.asset_folder = self.folder_name

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_asset_ui_refresh(Operator):
    bl_label = "Refresh"
    bl_description = "Refresh asset UI"
    bl_idname = "wm.jewelcraft_asset_ui_refresh"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        dynamic_list.asset_folder_list_refresh()
        dynamic_list.asset_list_refresh(hard=True)
        return {"FINISHED"}
