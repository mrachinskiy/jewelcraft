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

from ..lib import dynamic_list


class Setup:

    def __init__(self):
        props = bpy.context.scene.jewelcraft
        self.list = props.measurements


class WM_OT_ul_measurements_add(Operator, Setup):
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
            ("WEIGHT", "Weight", "", "FILE_3D", 1),
            ("RING_SIZE", "Ring Size", "", "MESH_CIRCLE", 2),
        ),
    )
    ring_size: EnumProperty(
        name="Format",
        items=(
            ("DIA", "Diameter", ""),
            ("CIR", "Circumference", ""),
            ("US", "USA", ""),
            ("UK", "Britain", ""),
            ("CH", "Swiss", ""),
            ("JP", "Japan", ""),
        ),
        options={"SKIP_SAVE"},
    )
    axis: EnumProperty(
        name="Axis",
        items=(
            ("0", "X", ""),
            ("1", "Y", ""),
            ("2", "Z", ""),
        ),
        options={"SKIP_SAVE"},
    )
    material: EnumProperty(
        name="Material",
        items=dynamic_list.weighting_materials,
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

        row = layout.row(align=True)
        row.prop(self, "type", text="Type", icon_only=True)
        row.prop(self, "item_name", text="")

        if self.type == "DIMENSIONS":
            col = layout.column(align=True)
            col.prop(self, "x")
            col.prop(self, "y")
            col.prop(self, "z")
        elif self.type == "WEIGHT":
            layout.prop(self, "material")
        elif self.type == "RING_SIZE":
            layout.prop(self, "ring_size")
            layout.prop(self, "axis")

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
        elif self.type == "WEIGHT":
            materials = context.scene.jewelcraft.weighting_materials
            mat = materials.values()[int(self.material)]
            item.material_name = mat.name
            item.material_density = mat.density
        elif self.type == "RING_SIZE":
            item.ring_size = self.ring_size
            item.axis = self.axis

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.object:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}

        dynamic_list.weighting_materials_refresh()
        self.item_name = context.object.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_ul_measurements_material_select(Operator, Setup):
    bl_label = "Select Material"
    bl_description = "Select material"
    bl_idname = "wm.jewelcraft_ul_measurements_material_select"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    material: EnumProperty(
        name="Material",
        items=dynamic_list.weighting_materials,
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.prop(self, "material")
        layout.separator()

    def execute(self, context):
        item = self.list.values()[self.list.index]

        materials = context.scene.jewelcraft.weighting_materials
        mat = materials.values()[int(self.material)]
        item.material_name = mat.name
        item.material_density = mat.density

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        dynamic_list.weighting_materials_refresh()

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_ul_measurements_del(Operator, Setup):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "wm.jewelcraft_ul_measurements_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        self.list.remove()
        return {"FINISHED"}


class WM_OT_ul_measurements_move(Operator, Setup):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "wm.jewelcraft_ul_measurements_move"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        self.list.move(self.move_up)
        return {"FINISHED"}
