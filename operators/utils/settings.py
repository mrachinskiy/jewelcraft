# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from ... import var


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


class WM_OT_goto_prefs(Operator):
    bl_label = "Open Add-on Preferences"
    bl_description = "Open add-on preferences window"
    bl_idname = "wm.jewelcraft_goto_prefs"
    bl_options = {"INTERNAL"}

    show: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        wm = context.window_manager

        for pref in dir(wm.jewelcraft):
            if pref.startswith("prefs_"):
                setattr(wm.jewelcraft, pref, False)

        setattr(wm.jewelcraft, self.show, True)

        bpy.ops.preferences.addon_show(module=var.ADDON_ID)
        return {"FINISHED"}
