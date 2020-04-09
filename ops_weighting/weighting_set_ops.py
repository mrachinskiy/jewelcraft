# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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

from bpy.types import Operator
from bpy.props import StringProperty

from .. import var
from ..lib import asset, dynamic_list


class EditCheck:

    @classmethod
    def poll(cls, context):
        props = context.window_manager.jewelcraft
        return bool(props.weighting_set) and not props.weighting_set.startswith("JCASSET")


class WM_OT_weighting_set_add(Operator):
    bl_label = "Create Set"
    bl_description = "Create weighting set from materials list"
    bl_idname = "wm.jewelcraft_weighting_set_add"
    bl_options = {"INTERNAL"}

    set_name: StringProperty(name="Set Name", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.prop(self, "set_name")
        layout.separator()

    def execute(self, context):
        if not self.set_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        lib_path = asset.get_weighting_lib_path()
        set_path = os.path.join(lib_path, self.set_name + ".json")

        if not os.path.exists(lib_path):
            os.makedirs(lib_path)

        materials = context.scene.jewelcraft.weighting_materials
        asset.weighting_set_export(materials, set_path)

        dynamic_list.weighting_set_refresh()
        props = context.window_manager.jewelcraft
        props.weighting_set = self.set_name + ".json"

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_weighting_set_replace(EditCheck, Operator):
    bl_label = "Replace Set"
    bl_description = "Replace selected weighting set with current materials list"
    bl_idname = "wm.jewelcraft_weighting_set_replace"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        set_path = asset.get_weighting_set_path()
        if os.path.exists(set_path):
            materials = context.scene.jewelcraft.weighting_materials
            asset.weighting_set_export(materials, set_path)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_weighting_set_del(EditCheck, Operator):
    bl_label = "Remove Set"
    bl_description = "Remove weighting set"
    bl_idname = "wm.jewelcraft_weighting_set_del"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        props = context.window_manager.jewelcraft
        set_path = asset.get_weighting_set_path()

        list_ = [x[0] for x in dynamic_list.weighting_set(self, context)]
        index = max(0, list_.index(props.weighting_set) - 1)

        if os.path.exists(set_path):
            os.remove(set_path)

        dynamic_list.weighting_set_refresh()

        list_ = [x[0] for x in dynamic_list.weighting_set(self, context)]
        if list_:
            props.weighting_set = list_[index]

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_weighting_set_rename(EditCheck, Operator):
    bl_label = "Rename Set"
    bl_description = "Rename weighting set"
    bl_idname = "wm.jewelcraft_weighting_set_rename"
    bl_options = {"INTERNAL"}

    set_name: StringProperty(name="Set Name", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.prop(self, "set_name")
        layout.separator()

    def execute(self, context):
        if not self.set_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        set_path_current = asset.get_weighting_set_path()
        set_path_new = os.path.join(asset.get_weighting_lib_path(), self.set_name + ".json")

        if not os.path.exists(set_path_current):
            self.report({"ERROR"}, "File not found")
            return {"CANCELLED"}

        os.rename(set_path_current, set_path_new)
        dynamic_list.weighting_set_refresh()
        props = context.window_manager.jewelcraft
        props.weighting_set = self.set_name + ".json"

        return {"FINISHED"}

    def invoke(self, context, event):
        props = context.window_manager.jewelcraft
        self.set_name = os.path.splitext(props.weighting_set)[0]

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_weighting_set_refresh(Operator):
    bl_label = "Refresh"
    bl_description = "Refresh asset UI"
    bl_idname = "wm.jewelcraft_weighting_set_refresh"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        dynamic_list.weighting_set_refresh()
        return {"FINISHED"}


class WM_OT_weighting_set_autoload_mark(Operator):
    bl_label = "Mark Autoload"
    bl_description = (
        "Autoload marked weighting set on File > Open/New "
        "if materials list for given blend file is empty"
    )
    bl_idname = "wm.jewelcraft_weighting_set_autoload_mark"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        props = context.window_manager.jewelcraft
        return bool(props.weighting_set)

    def execute(self, context):
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        props = context.window_manager.jewelcraft

        prefs.weighting_set_autoload = props.weighting_set

        dynamic_list.weighting_set_refresh()
        context.preferences.is_dirty = True

        return {"FINISHED"}


class WeightingSetLoad:

    @classmethod
    def poll(cls, context):
        props = context.window_manager.jewelcraft
        return bool(props.weighting_set)

    def execute(self, context):
        props = context.window_manager.jewelcraft
        materials = context.scene.jewelcraft.weighting_materials
        set_path = asset.get_weighting_set_path()

        if self.clear_materials:
            materials.clear()

        asset.weighting_set_import(materials, props.weighting_set, set_path)

        return {"FINISHED"}


class WM_OT_weighting_set_load(WeightingSetLoad, Operator):
    bl_label = "Load"
    bl_description = "Load weighting set to the materials list by replacing existing materials"
    bl_idname = "wm.jewelcraft_weighting_set_load"
    bl_options = {"INTERNAL"}

    clear_materials = True


class WM_OT_weighting_set_load_append(WeightingSetLoad, Operator):
    bl_label = "Append"
    bl_description = "Append weighting set at the end of the current materials list"
    bl_idname = "wm.jewelcraft_weighting_set_load_append"
    bl_options = {"INTERNAL"}

    clear_materials = False
