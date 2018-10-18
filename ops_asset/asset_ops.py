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


import os

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import bpy.utils.previews

from .. import var, dynamic_lists
from ..lib import asset


class Setup:

    def __init__(self):
        self.props = bpy.context.window_manager.jewelcraft
        self.folder_name = self.props.asset_folder
        self.folder = os.path.join(asset.user_asset_library_folder_object(), self.folder_name)
        self.asset_name = self.props.asset_list
        self.filepath = os.path.join(self.folder, self.asset_name)


class WM_OT_jewelcraft_asset_add_to_library(Operator, Setup):
    bl_label = "Add To Library"
    bl_description = "Add selected objects to asset library"
    bl_idname = "wm.jewelcraft_asset_add_to_library"
    bl_options = {"INTERNAL"}

    asset_name = StringProperty(name="Asset Name", description="Asset name", options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_folder)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        row = layout.row()
        row.label("Asset Name")
        row.prop(self, "asset_name", text="")
        layout.separator()

    def execute(self, context):
        if not self.asset_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        filepath = os.path.join(self.folder, self.asset_name)

        asset.asset_export(folder=self.folder, filename=self.asset_name + ".blend")
        asset.render_preview(filepath=filepath + ".png")
        dynamic_lists.asset_list_refresh()
        self.props.asset_list = self.asset_name

        return {"FINISHED"}

    def invoke(self, context, event):
        prefs = context.user_preferences.addons[var.ADDON_ID].preferences

        if prefs.asset_name_from_obj:
            self.asset_name = context.active_object.name
        else:
            self.asset_name = ""

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_jewelcraft_asset_remove_from_library(Operator, Setup):
    bl_label = "Remove Asset"
    bl_description = "Remove asset from library"
    bl_idname = "wm.jewelcraft_asset_remove_from_library"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        asset_list = dynamic_lists.assets(self, context)
        last = self.asset_name == asset_list[-1][0]
        iterable = len(asset_list) > 1

        if os.path.exists(self.filepath + ".blend"):
            os.remove(self.filepath + ".blend")

        if os.path.exists(self.filepath + ".png"):
            os.remove(self.filepath + ".png")

        dynamic_lists.asset_list_refresh(preview_id=self.folder_name + self.asset_name)

        if last and iterable:
            self.props.asset_list = asset_list[-2][0]

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_jewelcraft_asset_rename(Operator, Setup):
    bl_label = "Rename Asset"
    bl_description = "Rename asset"
    bl_idname = "wm.jewelcraft_asset_rename"
    bl_options = {"INTERNAL"}

    asset_name = StringProperty(name="Asset Name", description="Asset name", options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        row = layout.row()
        row.label("Asset Name")
        row.prop(self, "asset_name", text="")
        layout.separator()

    def execute(self, context):
        if not self.asset_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        name_current = self.props.asset_list

        file_current = os.path.join(self.folder, name_current + ".blend")
        file_preview_current = os.path.join(self.folder, name_current + ".png")

        file_new = os.path.join(self.folder, self.asset_name + ".blend")
        file_preview_new = os.path.join(self.folder, self.asset_name + ".png")

        if not os.path.exists(file_current):
            self.report({"ERROR"}, "File not found")
            return {"CANCELLED"}

        os.rename(file_current, file_new)

        if os.path.exists(file_preview_current):
            os.rename(file_preview_current, file_preview_new)

        dynamic_lists.asset_list_refresh()
        self.props.asset_list = self.asset_name

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_jewelcraft_asset_replace(Operator, Setup):
    bl_label = "Replace Asset"
    bl_description = "Replace current asset with selected objects"
    bl_idname = "wm.jewelcraft_asset_replace"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        asset.asset_export(folder=self.folder, filename=self.asset_name + ".blend")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_jewelcraft_asset_preview_replace(Operator, Setup):
    bl_label = "Replace Asset Preview"
    bl_description = "Replace asset preview image"
    bl_idname = "wm.jewelcraft_asset_preview_replace"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        asset.render_preview(filepath=self.filepath + ".png")
        dynamic_lists.asset_list_refresh(preview_id=self.folder_name + self.asset_name)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_jewelcraft_asset_import(Operator, Setup):
    bl_label = "JewelCraft Import Asset"
    bl_description = "Import selected asset"
    bl_idname = "wm.jewelcraft_asset_import"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        scene = context.scene

        for ob in scene.objects:
            ob.select = False

        imported = asset.asset_import_batch(filepath=self.filepath + ".blend")
        obs = imported.objects

        for ob in obs:
            scene.objects.link(ob)
            ob.select = True
            ob.layers = self.view_layers

        if len(obs) == 1:
            ob.location = scene.cursor_location

            if context.mode == "EDIT_MESH":
                asset.ob_copy_to_pos(ob)
                bpy.ops.object.mode_set(mode="OBJECT")

        scene.objects.active = ob

        return {"FINISHED"}

    def invoke(self, context, event):
        self.view_layers = [False for x in range(20)]
        self.view_layers[context.scene.active_layer] = True

        return self.execute(context)
