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
from bpy.app.translations import pgettext_iface as _

from .. import var
from ..lib import asset, dynamic_list


class Setup:

    def __init__(self):
        self.prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
        self.props = bpy.context.window_manager.jewelcraft
        self.materials = self.prefs.weighting_materials
        self.filename = self.props.weighting_set
        self.folder = asset.user_asset_library_folder_weighting()
        self.filepath = os.path.join(self.folder, self.filename)


class EditCheck:

    @classmethod
    def poll(cls, context):
        props = context.window_manager.jewelcraft
        return bool(props.weighting_set) and not props.weighting_set.startswith("JCASSET")


def materials_export_to_file(materials, filepath):
    import json

    with open(filepath, "w", encoding="utf-8") as file:

        data = []
        mat_fmt = {
            "name": "",
            "composition": "",
            "density": 0.0,
        }

        for mat in materials.values():
            mat_dict = {k: v for k, v in mat.items() if k in mat_fmt.keys()}

            mat_exp = mat_fmt.copy()
            mat_exp.update(mat_dict)
            mat_exp["density"] = round(mat_exp["density"], 2)

            data.append(mat_exp)

        json.dump(data, file, indent=4, ensure_ascii=False)


class WM_OT_jewelcraft_weighting_set_add(Operator, Setup):
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

        set_name = self.set_name + ".json"
        filepath = os.path.join(self.folder, set_name)

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        materials_export_to_file(self.materials, filepath)

        dynamic_list.weighting_set_refresh()
        self.props.weighting_set = set_name

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_jewelcraft_weighting_set_replace(Operator, Setup, EditCheck):
    bl_label = "Replace Set"
    bl_description = "Replace selected weighting set with current materials list"
    bl_idname = "wm.jewelcraft_weighting_set_replace"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        if os.path.exists(self.filepath):
            materials_export_to_file(self.materials, self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_jewelcraft_weighting_set_del(Operator, Setup, EditCheck):
    bl_label = "Remove Set"
    bl_description = "Remove weighting set"
    bl_idname = "wm.jewelcraft_weighting_set_del"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        list_ = [x[0] for x in dynamic_list.weighting_set(self, context)]
        index = max(0, list_.index(self.filename) - 1)

        if os.path.exists(self.filepath):
            os.remove(self.filepath)

        dynamic_list.weighting_set_refresh()

        list_ = [x[0] for x in dynamic_list.weighting_set(self, context)]
        if list_:
            self.props.weighting_set = list_[index]

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_jewelcraft_weighting_set_rename(Operator, Setup, EditCheck):
    bl_label = "Rename Set"
    bl_description = "Rename weighting set"
    bl_idname = "wm.jewelcraft_weighting_set_rename"
    bl_options = {"INTERNAL"}

    set_name: StringProperty(name="Set Name", options={"SKIP_SAVE"})

    def __init__(self):
        super().__init__()
        self.set_name = os.path.splitext(self.filename)[0]

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

        filename_new = self.set_name + ".json"
        filepath_new = os.path.join(self.folder, filename_new)

        if not os.path.exists(self.filepath):
            self.report({"ERROR"}, "File not found")
            return {"CANCELLED"}

        os.rename(self.filepath, filepath_new)
        dynamic_list.weighting_set_refresh()
        self.props.weighting_set = filename_new

        return {"FINISHED"}


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_jewelcraft_weighting_set_refresh(Operator):
    bl_label = "Refresh"
    bl_description = "Refresh asset UI"
    bl_idname = "wm.jewelcraft_weighting_set_refresh"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        dynamic_list.weighting_set_refresh()
        return {"FINISHED"}


class WeightingSetLoad:
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        props = context.window_manager.jewelcraft
        return bool(props.weighting_set)

    def execute(self, context):
        import json

        if self.clear_materials:
            self.materials.clear()

        if self.filename.startswith("JCASSET"):
            for mat in var.DEFAULT_WEIGHTING_SETS[self.filename]:
                name, dens, comp = mat
                item = self.materials.add()
                item.name = _(name)
                item.composition = comp
                item.density = dens
        else:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)

                for mat in data:
                    item = self.materials.add()
                    if mat["name"]:
                        item.name = mat["name"]
                    if mat["composition"]:
                        item.composition = mat["composition"]
                    item.density = mat["density"]

        return {"FINISHED"}


class WM_OT_jewelcraft_weighting_set_load(Operator, Setup, WeightingSetLoad):
    bl_label = "Load"
    bl_description = "Load weighting set to the materials list by replacing existing materials"
    bl_idname = "wm.jewelcraft_weighting_set_load"

    clear_materials = True


class WM_OT_jewelcraft_weighting_set_load_append(Operator, Setup, WeightingSetLoad):
    bl_label = "Append"
    bl_description = "Append weighting set at the end of the current materials list"
    bl_idname = "wm.jewelcraft_weighting_set_load_append"

    clear_materials = False
