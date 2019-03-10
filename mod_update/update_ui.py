# ##### BEGIN GPL LICENSE BLOCK #####
#
#  mod_update automatic add-on updates.
#  Copyright (C) 2019  Mikhail Rachinskiy
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

from .. import var
from . import update_ops


def prefs_ui(self, layout):
    col = layout.column()
    col.prop(self, "update_use_auto_check")
    col.prop(self, "update_use_prerelease")
    sub = col.column()
    sub.active = self.update_use_auto_check
    sub.prop(self, "update_interval")

    layout.separator()

    row = layout.row(align=True)
    row.alignment = "CENTER"

    if var.update_completed:
        row.label(text="Update completed")
        row.operator(update_ops.OP_IDNAME_WHATS_NEW)

        row = layout.row(align=True)
        row.alignment = "CENTER"
        row.label(text="Close Blender to complete the installation", icon="ERROR")

    elif var.update_in_progress:
        if var.update_available:
            row.label(text="Installing...")
        else:
            row.label(text="Checking...")

    elif var.update_available:
        row.label(text=_("Update {} is available").format(var.update_version))

    else:
        if var.update_days_passed is None:
            msg_date = _("never")
        elif var.update_days_passed == 0:
            msg_date = _("today")
        elif var.update_days_passed == 1:
            msg_date = _("yesterday")
        else:
            msg_date = "{} {}".format(var.update_days_passed, _("days ago"))

        row.label(text="{} {}".format(_("Last checked"), msg_date))

    col = layout.row()
    col.alignment = "CENTER"
    col.scale_y = 1.5
    col.enabled = not var.update_in_progress and not var.update_completed

    if var.update_available:
        col.operator(update_ops.OP_IDNAME_DOWNLOAD)
    else:
        col.operator(update_ops.OP_IDNAME_CHECK)


def sidebar_ui(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    row = layout.row(align=True)
    row.alignment = "CENTER"

    if var.update_completed:
        row.label(text="Update completed")
        row.operator(update_ops.OP_IDNAME_WHATS_NEW)

        row = layout.row(align=True)
        row.alignment = "CENTER"
        row.label(text="Close Blender to complete the installation", icon="ERROR")

    elif var.update_in_progress:
        row.label(text="Installing...")

    elif var.update_available:
        row.label(text=_("Update {} is available").format(var.update_version))

    col = layout.row()
    col.alignment = "CENTER"
    col.scale_y = 1.5
    col.enabled = not var.update_in_progress and not var.update_completed
    col.operator(update_ops.OP_IDNAME_DOWNLOAD)
