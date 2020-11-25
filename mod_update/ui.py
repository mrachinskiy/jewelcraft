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


from bpy.app.translations import pgettext_iface as _

from . import state, operators


class SidebarPanel:

    @classmethod
    def poll(cls, context):
        return state.update_available

    def draw(self, context):
        sidebar_ui(self.layout)


def sidebar_ui(layout):
    row = layout.row(align=True)
    row.alignment = "CENTER"

    if state.status is state.COMPLETED:
        row.label(text="Update completed")
        row.operator(operators.WM_OT_update_whats_new.bl_idname)

        row = layout.row(align=True)
        row.alignment = "CENTER"
        row.label(text="Close Blender to complete the installation", icon="ERROR")

    elif state.status is state.INSTALLING:
        row.label(text="Installing...")

    elif state.status is state.ERROR:
        row.label(text=state.error_msg)

    else:
        row.label(text=_("Update {} is available").format(state.update_version))

    col = layout.row()
    col.alignment = "CENTER"
    col.scale_y = 1.5
    col.enabled = state.status is None or state.status is state.ERROR
    col.operator(operators.WM_OT_update_download.bl_idname)


def prefs_ui(self, layout):
    col = layout.column()
    col.prop(self, "mod_update_autocheck")
    col.prop(self, "mod_update_prerelease")
    sub = col.column()
    sub.active = self.mod_update_autocheck
    sub.prop(self, "mod_update_interval")

    layout.separator()

    row = layout.row(align=True)
    row.alignment = "CENTER"

    if state.status is state.COMPLETED:
        row.label(text="Update completed")
        row.operator(operators.WM_OT_update_whats_new.bl_idname)

        row = layout.row(align=True)
        row.alignment = "CENTER"
        row.label(text="Close Blender to complete the installation", icon="ERROR")

    elif state.status is state.CHECKING:
        row.label(text="Checking...")

    elif state.status is state.INSTALLING:
        row.label(text="Installing...")

    elif state.status is state.ERROR:
        row.label(text=state.error_msg)

    elif state.update_available:
        row.label(text=_("Update {} is available").format(state.update_version))

    else:
        if state.days_passed is None:
            msg_date = _("never")
        elif state.days_passed == 0:
            msg_date = _("today")
        elif state.days_passed == 1:
            msg_date = _("yesterday")
        else:
            msg_date = "{} {}".format(state.days_passed, _("days ago"))

        row.label(text="{} {}".format(_("Last checked"), msg_date))

    col = layout.row()
    col.alignment = "CENTER"
    col.scale_y = 1.5
    col.enabled = state.status is None or state.status is state.ERROR

    if state.update_available:
        col.operator(operators.WM_OT_update_download.bl_idname)
    else:
        col.operator(operators.WM_OT_update_check.bl_idname)
