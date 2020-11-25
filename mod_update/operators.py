# ##### BEGIN GPL LICENSE BLOCK #####
#
#  mod_update automatic add-on updates.
#  Copyright (C) 2019-2020  Mikhail Rachinskiy
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

from .. import var
from . import state, updatelib


class WM_OT_update_check(Operator):
    bl_label = "Check for Updates"
    bl_description = "Check for new add-on release"
    bl_idname = f"wm.{var.ADDON_ID}_update_check"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        if (
            state.status is state.CHECKING or
            state.status is state.INSTALLING or
            state.status is state.COMPLETED
        ):
            return {"CANCELLED"}

        updatelib.update_init_check(use_force_check=True)

        return {"FINISHED"}


class WM_OT_update_download(Operator):
    bl_label = "Install Update"
    bl_description = "Download and install new version of the add-on"
    bl_idname = f"wm.{var.ADDON_ID}_update_download"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        if (
            state.status is state.CHECKING or
            state.status is state.INSTALLING or
            state.status is state.COMPLETED
        ):
            return {"CANCELLED"}

        updatelib.update_init_download()

        return {"FINISHED"}


class WM_OT_update_whats_new(Operator):
    bl_label = "See What's New"
    bl_description = "Open release notes in web browser"
    bl_idname = f"wm.{var.ADDON_ID}_update_whats_new"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        import webbrowser
        webbrowser.open(state.changelog_url)
        return {"FINISHED"}
