# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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
