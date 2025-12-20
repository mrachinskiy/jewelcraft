# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.app.translations import pgettext_iface as _
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator, UILayout

from ...lib import dynamic_list


class WM_OT_ul_measurements_add(Operator):
    bl_label = "Add New Measurement"
    bl_description = "Add a new measurement"
    bl_idname = "wm.jewelcraft_ul_measurements_add"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    meta_name: StringProperty(name="Name", options={"SKIP_SAVE"})
    meta_value: StringProperty(name="Value", options={"SKIP_SAVE"})
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})
    object_name: StringProperty(name="Object", options={"SKIP_SAVE"})
    type: EnumProperty(
        name="Type",
        items=(
            ("WEIGHT", "Weight", "", "FILE_3D", 0),
            ("VOLUME", "Volume", "", "FILE_VOLUME", 1),
            ("RING_SIZE", "Ring Size", "", "MESH_CIRCLE", 2),
            ("DIMENSIONS", "Dimensions", "", "SHADING_BBOX", 3),
            ("METADATA", "Metadata", "", "DOT", 4),
        ),
    )
    datablock_type: EnumProperty(
        name="Target type",
        items=(
            ("OBJECT", "Object", ""),
            ("COLLECTION", "Collection", ""),
        ),
    )
    ring_size: EnumProperty(
        name="Format",
        items=(
            ("DIAMETER", "Diameter", ""),
            ("CIRCUMFERENCE", "Circumference", ""),
            ("US", "USA", ""),
            ("UK", "Britain", ""),
            ("CH", "Swiss", ""),
            ("JP", "Japan", ""),
            ("HK", "Hong Kong", ""),
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
    )
    x: BoolProperty(name="X", default=True, options={"SKIP_SAVE"})
    y: BoolProperty(name="Y", default=True, options={"SKIP_SAVE"})
    z: BoolProperty(name="Z", default=True, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.prop(self, "type")

        layout.separator()

        if self.type == "METADATA":
            layout.prop(self, "meta_name")
            layout.prop(self, "meta_value")
            layout.separator()
            return

        col = layout.column()
        col.row().prop(self, "datablock_type", expand=True)

        if self.datablock_type == "OBJECT":
            col.alert = not self.object_name
            col.prop_search(self, "object_name", bpy.data, "objects")
        else:
            col.alert = not self.collection_name
            col.prop_search(self, "collection_name", bpy.data, "collections")

        layout.separator()

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
        item.datablock_type = self.datablock_type

        if self.type == "METADATA":
            item.name = self.meta_name
            item.value = self.meta_value
            context.area.tag_redraw()
            return {"FINISHED"}

        if self.datablock_type == "OBJECT" and self.object_name:
            item.object = bpy.data.objects[self.object_name]
        elif self.datablock_type == "COLLECTION" and self.collection_name:
            item.collection = bpy.data.collections[self.collection_name]

        if self.type == "WEIGHT":
            materials = context.scene.jewelcraft.weighting_materials
            mat = materials.values()[int(self.material)]
            item.name = mat.name
            item.material_name = mat.name
            item.material_density = mat.density
        elif self.type == "VOLUME":
            target_name = self.object_name if self.datablock_type == "OBJECT" else self.collection_name
            item.name = "{} {}".format(target_name, _("Volume"))
        elif self.type == "DIMENSIONS":
            target_name = self.object_name if self.datablock_type == "OBJECT" else self.collection_name
            item.name = "{} {}".format(target_name, _("Dimensions"))
            item.x = self.x
            item.y = self.y
            item.z = self.z
        elif self.type == "RING_SIZE":
            size_format = UILayout.enum_item_name(self, "ring_size", self.ring_size)
            item.name = "{} ({})".format(_("Ring Size"), size_format)
            item.ring_size = self.ring_size
            item.axis = self.axis

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        dynamic_list.weighting_materials_refresh()

        if context.collection is not None:
            self.collection_name = context.collection.name
        if context.object is not None:
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
