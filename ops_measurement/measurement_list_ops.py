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
from bpy.props import BoolProperty, StringProperty, EnumProperty


class Setup:

    def __init__(self):
        props = bpy.context.scene.jewelcraft
        self.list = props.measurements


class WM_OT_jewelcraft_ul_measurements_add(Operator, Setup):
    bl_label = "Add New Measurement"
    bl_description = "Add a new measurement"
    bl_idname = "wm.jewelcraft_ul_measurements_add"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    item_name: StringProperty(name="Name", options={"SKIP_SAVE"})
    type: EnumProperty(
        name="Type",
        description="Measurement type",
        items=(
            ("DIMENSIONS", "Dimensions", "", "SHADING_BBOX", 0),
            ("VOLUME", "Volume", "", "VOLUME", 1),
        ),
        default="DIMENSIONS",
        options={"SKIP_SAVE"},
    )
    x: BoolProperty(name="X", default=True, options={"SKIP_SAVE"})
    y: BoolProperty(name="Y", default=True, options={"SKIP_SAVE"})
    z: BoolProperty(name="Z", default=True, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.prop(self, "item_name")
        layout.prop(self, "type")

        if self.type == "DIMENSIONS":
            col = layout.column(align=True)
            col.prop(self, "x")
            col.prop(self, "y")
            col.prop(self, "z")

        layout.separator()

    def execute(self, context):
        item = self.list.add()

        item.name = self.item_name
        item.object = context.object
        item.type = self.type

        if self.type == "DIMENSIONS":
            item.x = self.x
            item.y = self.y
            item.z = self.z

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.object:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}

        self.item_name = context.object.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_jewelcraft_ul_measurements_del(Operator, Setup):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "wm.jewelcraft_ul_measurements_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        self.list.remove()
        return {"FINISHED"}


class WM_OT_jewelcraft_ul_measurements_move(Operator, Setup):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "wm.jewelcraft_ul_measurements_move"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        self.list.move(self.move_up)
        return {"FINISHED"}
