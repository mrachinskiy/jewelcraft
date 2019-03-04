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


from bpy.app.translations import pgettext_iface as _

from .. import var


def prefs_ui(self, layout):
    box = layout

    col = box.column()
    col.prop(self, "update_use_auto_check")
    col.prop(self, "update_use_prerelease")
    sub = col.column()
    sub.active = self.update_use_auto_check
    sub.prop(self, "update_interval")

    box.separator()

    row = box.row(align=True)
    row.alignment = "CENTER"

    if var.update_completed:
        row.label(text="Update completed")
        row.operator("wm.jewelcraft_update_whats_new")

        row = box.row(align=True)
        row.alignment = "CENTER"
        row.label(text="Close Blender to complete the installation", icon="ERROR")

    elif var.update_in_progress:

        if var.update_available:
            row.label(text="Installing...")
        else:
            row.label(text="Checking...")

    elif var.update_available:
        row.label(text=_("Update {} is available").format(var.update_version))
    elif var.update_days_passed is None:
        row.label(text="Last checked never")
    elif var.update_days_passed == 0:
        row.label(text="Last checked today")
    elif var.update_days_passed == 1:
        row.label(text="Last checked yesterday")
    else:
        row.label(text=_("Last checked {} days ago").format(var.update_days_passed))

    col = box.row()
    col.alignment = "CENTER"
    col.scale_y = 1.5
    col.enabled = not var.update_in_progress and not var.update_completed

    if var.update_available:
        col.operator("wm.jewelcraft_update_download")
    else:
        col.operator("wm.jewelcraft_update_check")


def sidebar_ui(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    row = layout.row(align=True)
    row.alignment = "CENTER"

    if var.update_completed:
        row.label(text="Update completed")
        row.operator("wm.jewelcraft_update_whats_new")

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
    col.operator("wm.jewelcraft_update_download")
