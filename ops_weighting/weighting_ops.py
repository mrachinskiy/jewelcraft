# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.app.translations import pgettext_iface as _
from bpy.props import FloatProperty, StringProperty
from bpy.types import Operator


class WM_OT_ul_material_add(Operator):
    bl_label = "Add New Material"
    bl_description = "Add new material to the list"
    bl_idname = "wm.jewelcraft_ul_material_add"
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
        item = context.scene.jewelcraft.weighting_materials.add()

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


class OBJECT_OT_weight_display(Operator):
    bl_label = "Display Weight"
    bl_description = "Display weight and volume for selected mesh objects"
    bl_idname = "object.jewelcraft_weight_display"

    def execute(self, context):
        from ..lib import mesh, ui_lib, unit

        obs = [
            ob for ob in context.selected_objects
            if ob.type in {"MESH", "CURVE", "SURFACE", "FONT", "META"}
        ]

        if not obs:
            self.report({"ERROR"}, "At least one mesh object must be selected")
            return {"CANCELLED"}

        materials = context.scene.jewelcraft.weighting_materials
        vol = unit.Scale().from_scene_vol(mesh.est_volume(obs))

        weight_report = []

        volume_fmt = "{} {}  {}".format(round(vol, 4), _("mm³"), _("Volume"))
        weight_report.append(volume_fmt)

        for mat in materials.values():
            if mat.enabled:
                density = unit.convert_cm3_mm3(mat.density)
                weight = round(vol * density, 2)
                weight_fmt = "{} {}  {}".format(weight, _("g"), mat.name)
                weight_report.append(weight_fmt)

        ui_lib.popup_list(self, _("Weighting"), weight_report)

        return {"FINISHED"}
