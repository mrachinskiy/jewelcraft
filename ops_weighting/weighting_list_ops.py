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


import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty, FloatProperty

from .. import var


class Setup:

    def __init__(self):
        prefs = bpy.context.user_preferences.addons[var.ADDON_ID].preferences
        self.materials = prefs.weighting_materials


class WM_OT_jewelcraft_ul_item_add(Operator, Setup):
    bl_label = "Add New Material"
    bl_description = "Add new material to the list"
    bl_idname = "wm.jewelcraft_ul_item_add"
    bl_options = {"INTERNAL"}

    name = StringProperty(name="Name", description="Material name", options={"SKIP_SAVE"})
    composition = StringProperty(name="Composition", description="Material composition", options={"SKIP_SAVE"})
    density = FloatProperty(name="Density", description="Density g/cm³", default=0.01, min=0.01, step=1, precision=2, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.separator()

        split = layout.split(percentage=1 / 3)
        split.label("Name")
        split.prop(self, "name", text="")

        split = layout.split(percentage=1 / 3)
        split.label("Composition")
        split.prop(self, "composition", text="")

        split = layout.split(percentage=1 / 3)
        split.label("Density")
        split.prop(self, "density", text="")

        layout.separator()

    def execute(self, context):
        item = self.materials.add()
        if self.name:
            item.name = self.name
        if self.composition:
            item.composition = self.composition
        item.density = self.density
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_jewelcraft_ul_item_del(Operator, Setup):
    bl_label = "Remove Material"
    bl_description = "Remove material from the list"
    bl_idname = "wm.jewelcraft_ul_item_del"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        self.materials.remove()
        return {"FINISHED"}


class WM_OT_jewelcraft_ul_item_clear(Operator, Setup):
    bl_label = "Clear List"
    bl_description = "Clear materials list"
    bl_idname = "wm.jewelcraft_ul_item_clear"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        self.materials.clear()
        return {"FINISHED"}


class WM_OT_jewelcraft_ul_item_move(Operator, Setup):
    bl_label = "Move List Item"
    bl_description = "Move the active material up/down in the list"
    bl_idname = "wm.jewelcraft_ul_item_move"
    bl_options = {"INTERNAL"}

    move_up = BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        self.materials.move(self.move_up)
        return {"FINISHED"}
