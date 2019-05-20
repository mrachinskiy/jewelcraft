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


from bpy.types import Operator
from bpy.app.translations import pgettext_iface as _

from ..lib import unit, mesh, ui_lib


class OBJECT_OT_weight_display(Operator):
    bl_label = "JewelCraft Display Weight"
    bl_description = "Display weight and volume for selected mesh objects"
    bl_idname = "object.jewelcraft_weight_display"

    def execute(self, context):
        obs = [ob for ob in context.selected_objects if ob.type == "MESH"]

        if not obs:
            self.report({"ERROR"}, "At least one mesh object must be selected")
            return {"CANCELLED"}

        materials = context.scene.jewelcraft.weighting_materials
        vol = unit.Scale(context).from_scene(mesh.est_volume(obs), volume=True)

        weight_report = []

        volume_fmt = "{} {}  {}".format(round(vol, 4), _("mm³"), _("Volume"))
        weight_report.append(volume_fmt)

        for mat in materials.values():
            if mat.enabled:
                density = unit.convert(mat.density, "CM3_TO_MM3")
                weight = round(vol * density, 2)
                weight_fmt = "{} {}  {}".format(weight, _("g"), mat.name)
                weight_report.append(weight_fmt)

        ui_lib.popup_report_batch(self, context, data=weight_report, title=_("Weighting"))

        return {"FINISHED"}
