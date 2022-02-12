# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from .. import var


class WM_OT_goto_prefs(Operator):
    bl_label = "Open Add-on Preferences"
    bl_description = "Open add-on preferences window"
    bl_idname = "wm.jewelcraft_goto_prefs"
    bl_options = {"INTERNAL"}

    active_tab: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        prefs = context.preferences
        wm = context.window_manager

        prefs.active_section = "ADDONS"
        wm.addon_support = {"OFFICIAL", "COMMUNITY"}
        wm.addon_filter = "All"
        wm.addon_search = "JewelCraft"
        wm.jewelcraft.prefs_active_tab = self.active_tab

        bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        bpy.ops.preferences.addon_show(module=var.ADDON_ID)

        return {"FINISHED"}
