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


from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty
from bpy.app.translations import pgettext_iface as _


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
        from ..lib import unit, mesh, ui_lib

        obs = [
            ob for ob in context.selected_objects
            if ob.type in {"MESH", "CURVE", "SURFACE", "FONT", "META"}
        ]

        if not obs:
            self.report({"ERROR"}, "At least one mesh object must be selected")
            return {"CANCELLED"}

        materials = context.scene.jewelcraft.weighting_materials
        vol = unit.Scale(context).from_scene_vol(mesh.est_volume(obs))

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
