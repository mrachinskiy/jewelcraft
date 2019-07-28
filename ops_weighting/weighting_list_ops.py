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


import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty, FloatProperty


class Setup:

    def __init__(self):
        self.list = bpy.context.scene.jewelcraft.weighting_materials


class WM_OT_ul_materials_add(Operator, Setup):
    bl_label = "Add New Material"
    bl_description = "Add new material to the list"
    bl_idname = "wm.jewelcraft_ul_materials_add"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    name: StringProperty(
        name="Name",
        description="Material name",
        options={"SKIP_SAVE"},
    )
    composition: StringProperty(
        name="Composition",
        description="Material composition",
        options={"SKIP_SAVE"},
    )
    density: FloatProperty(
        name="Density",
        description="Density g/cm³",
        default=0.01,
        min=0.01,
        step=1,
        precision=2,
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.prop(self, "name")
        layout.prop(self, "composition")
        layout.prop(self, "density")
        layout.separator()

    def execute(self, context):
        item = self.list.add()

        if self.name:
            item.name = self.name
        if self.composition:
            item.composition = self.composition
        item.density = self.density

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_ul_materials_del(Operator, Setup):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "wm.jewelcraft_ul_materials_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        self.list.remove()
        return {"FINISHED"}


class WM_OT_ul_materials_clear(Operator, Setup):
    bl_label = "Clear List"
    bl_description = "Remove all list items"
    bl_idname = "wm.jewelcraft_ul_materials_clear"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        self.list.clear()
        return {"FINISHED"}


class WM_OT_ul_materials_move(Operator, Setup):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "wm.jewelcraft_ul_materials_move"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        self.list.move(self.move_up)
        return {"FINISHED"}
