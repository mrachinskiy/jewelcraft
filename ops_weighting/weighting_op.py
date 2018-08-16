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


from bpy.types import Operator
from bpy.app.translations import pgettext_iface as _

from .. import var
from ..lib import unit, mesh, ui_lib


class OBJECT_OT_jewelcraft_weight_display(Operator):
    bl_label = "JewelCraft Display Weight"
    bl_description = "Display weight and volume for active mesh object"
    bl_idname = "object.jewelcraft_weight_display"

    def execute(self, context):
        ob = context.active_object

        if not ob or ob.type != "MESH":
            self.report({"ERROR"}, "Active object must be a mesh")
            return {"CANCELLED"}

        prefs = context.user_preferences.addons[var.ADDON_ID].preferences
        materials = prefs.weighting_materials

        vol = unit.to_metric(mesh.volume(ob), volume=True)

        weight_report = []

        volume_fmt = "{} {}  {}".format(round(vol, 4), _("mm³"), _("Volume"))
        weight_report.append(volume_fmt)

        for mat in materials.values():
            if mat.enabled:
                density = unit.convert(mat.density, "CM3_TO_MM3")
                weight = round(vol * density, 2)
                weight_fmt = "{} {}  {}".format(weight, _("g"), mat.name)
                weight_report.append(weight_fmt)

        ui_lib.popup_report_batch(self, weight_report, title=_("Weighting"))

        return {"FINISHED"}
