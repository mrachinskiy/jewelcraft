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


class SCENE_OT_jewelcraft_scene_units_set(Operator):
    bl_label = "Set Units"
    bl_description = "Set optimal unit settings for jewelry modelling"
    bl_idname = "scene.jewelcraft_scene_units_set"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        unit_settings = context.scene.unit_settings
        unit_settings.system = "METRIC"
        unit_settings.length_unit = "MILLIMETERS"
        unit_settings.scale_length = 0.001
        context.space_data.overlay.grid_scale = 0.001

        self.report({"INFO"}, "Optimal unit settings are in use")

        return {"FINISHED"}
