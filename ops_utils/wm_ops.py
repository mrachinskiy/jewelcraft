# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from .. import var


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
