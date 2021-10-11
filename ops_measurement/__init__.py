# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


class WM_OT_ul_measurements_add(Operator):
    bl_label = "Add New Measurement"
    bl_description = "Add a new measurement"
    bl_idname = "wm.jewelcraft_ul_measurements_add"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})
    object_name: StringProperty(name="Object", options={"SKIP_SAVE"})
    type: EnumProperty(
        name="Type",
        description="Measurement type",
        items=(
            ("RING_SIZE", "Ring Size", "", "MESH_CIRCLE", 0),
            ("WEIGHT", "Weight", "", "FILE_3D", 1),
            ("DIMENSIONS", "Dimensions", "", "SHADING_BBOX", 2),
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

        layout.prop(self, "type", text="Type", icon_only=True)

        col = layout.column()

        if self.type == "WEIGHT":
            col.alert = not self.collection_name
            col.prop_search(self, "collection_name", bpy.data, "collections")
        else:
            col.alert = not self.object_name
            col.prop_search(self, "object_name", bpy.data, "objects")

        if self.type == "WEIGHT":
            layout.prop(self, "material")
        elif self.type == "DIMENSIONS":
            col = layout.column(heading="Dimensions", align=True)
            col.prop(self, "x")
            col.prop(self, "y")
            col.prop(self, "z")
        elif self.type == "RING_SIZE":
            layout.prop(self, "ring_size")
            layout.prop(self, "axis", expand=True)

        layout.separator()

    def execute(self, context):
        item = context.scene.jewelcraft.measurements.add()

        item.type = self.type

        if self.type == "WEIGHT":
            item.collection = bpy.data.collections[self.collection_name]
        else:
            item.name = self.object_name
            item.object = bpy.data.objects[self.object_name]

        if self.type == "WEIGHT":
            materials = context.scene.jewelcraft.weighting_materials
            mat = materials.values()[int(self.material)]
            item.name = mat.name
            item.material_name = mat.name
            item.material_density = mat.density
        elif self.type == "DIMENSIONS":
            item.x = self.x
            item.y = self.y
            item.z = self.z
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
        self.collection_name = context.collection.name
        self.object_name = context.object.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_ul_measurements_material_select(Operator):
    bl_label = "Select Material"
    bl_description = "Select material"
    bl_idname = "wm.jewelcraft_ul_measurements_material_select"
    bl_options = {"UNDO", "INTERNAL"}
    bl_property = "material"

    material: EnumProperty(
        name="Material",
        items=dynamic_list.weighting_materials,
        options={"SKIP_SAVE"},
    )

    def execute(self, context):
        item = context.scene.jewelcraft.measurements.active_item()

        materials = context.scene.jewelcraft.weighting_materials
        mat = materials.values()[int(self.material)]
        item.name = mat.name
        item.material_name = mat.name
        item.material_density = mat.density

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        dynamic_list.weighting_materials_refresh()
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}
