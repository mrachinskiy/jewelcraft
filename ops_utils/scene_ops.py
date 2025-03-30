# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Operator


class SCENE_OT_scene_units_set(Operator):
    bl_label = "Set Units"
    bl_description = "Set optimal unit settings for jewelry modelling"
    bl_idname = "scene.jewelcraft_scene_units_set"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        unit = context.scene.unit_settings
        unit.system = "METRIC"
        unit.length_unit = "MILLIMETERS"
        unit.scale_length = 0.001
        context.space_data.overlay.grid_scale = 0.001

        self.report({"INFO"}, "Optimal unit settings are in use")

        return {"FINISHED"}
