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
from bpy.props import StringProperty, BoolProperty
import bpy.utils.previews

from ..lib import asset, dynamic_list


class Setup:

    def __init__(self):
        self.props = bpy.context.window_manager.jewelcraft
        self.folder_name = self.props.asset_folder
        self.folder = os.path.join(asset.user_asset_library_folder_object(), self.folder_name)
        self.asset_name = self.props.asset_list
        self.filepath = os.path.join(self.folder, self.asset_name)


class WM_OT_asset_add_to_library(Operator, Setup):
    bl_label = "Add To Library"
    bl_description = "Add selected objects to asset library"
    bl_idname = "wm.jewelcraft_asset_add_to_library"
    bl_options = {"INTERNAL"}

    asset_name: StringProperty(name="Asset Name", description="Asset name", options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_folder)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.prop(self, "asset_name")
        layout.separator()

    def execute(self, context):
        if not self.asset_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        filepath = os.path.join(self.folder, self.asset_name)

        asset.asset_export(filepath + ".blend")
        asset.render_preview(256, 256, filepath + ".png")
        dynamic_list.asset_list_refresh()
        self.props.asset_list = self.asset_name

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            return {"CANCELLED"}

        self.asset_name = context.object.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_asset_remove_from_library(Operator, Setup):
    bl_label = "Remove Asset"
    bl_description = "Remove asset from library"
    bl_idname = "wm.jewelcraft_asset_remove_from_library"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        asset_list = dynamic_list.assets(self, context)
        last = self.asset_name == asset_list[-1][0]
        iterable = len(asset_list) > 1

        if os.path.exists(self.filepath + ".blend"):
            os.remove(self.filepath + ".blend")

        if os.path.exists(self.filepath + ".png"):
            os.remove(self.filepath + ".png")

        dynamic_list.asset_list_refresh(preview_id=self.folder_name + self.asset_name)

        if last and iterable:
            self.props.asset_list = asset_list[-2][0]

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_asset_rename(Operator, Setup):
    bl_label = "Rename Asset"
    bl_description = "Rename asset"
    bl_idname = "wm.jewelcraft_asset_rename"
    bl_options = {"INTERNAL"}

    asset_name: StringProperty(name="Asset Name", description="Asset name", options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.prop(self, "asset_name")
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

        dynamic_list.asset_list_refresh()
        self.props.asset_list = self.asset_name

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_asset_replace(Operator, Setup):
    bl_label = "Replace Asset"
    bl_description = "Replace current asset with selected objects"
    bl_idname = "wm.jewelcraft_asset_replace"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        filepath = os.path.join(self.folder, self.asset_name)
        asset.asset_export(filepath + ".blend")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_asset_preview_replace(Operator, Setup):
    bl_label = "Replace Asset Preview"
    bl_description = "Replace asset preview image"
    bl_idname = "wm.jewelcraft_asset_preview_replace"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        asset.render_preview(256, 256, self.filepath + ".png")
        dynamic_list.asset_list_refresh(preview_id=self.folder_name + self.asset_name)
        context.area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_asset_import(Operator, Setup):
    bl_label = "JewelCraft Import Asset"
    bl_description = "Import selected asset"
    bl_idname = "wm.jewelcraft_asset_import"
    bl_options = {"REGISTER", "UNDO"}

    use_parent: BoolProperty(
        name="Parent to selected",
        description="Parent imported asset to selected objects (Shortcut: hold Alt when using the tool)",
    )

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_list)

    def execute(self, context):
        space_data = context.space_data
        use_local_view = bool(space_data.local_view)
        collection = context.collection
        selected = list(context.selected_objects)

        for ob in selected:
            ob.select_set(False)

        imported = asset.asset_import_batch(self.filepath + ".blend")
        obs = imported.objects

        for ob in obs:
            collection.objects.link(ob)
            ob.select_set(True)

            if use_local_view:
                ob.local_view_set(space_data, True)

        if len(obs) == 1:
            ob.location = context.scene.cursor.location

            if self.use_parent and selected:
                collection.objects.unlink(ob)
                asset.ob_copy_and_parent(ob, selected)
            elif context.mode == "EDIT_MESH":
                asset.ob_copy_to_faces(ob)
                bpy.ops.object.mode_set(mode="OBJECT")

        context.view_layer.objects.active = ob

        return {"FINISHED"}

    def invoke(self, context, event):
        self.use_parent = event.alt

        return self.execute(context)
