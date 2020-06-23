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


import os

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty

from .. import var
from ..lib import gettext
from . import report_get, report_fmt, html_doc


class WM_OT_design_report(Operator):
    bl_label = "JewelCraft Design Report"
    bl_description = "Present summary information about the design, including gems, sizes and weight"
    bl_idname = "wm.jewelcraft_design_report"

    lang: EnumProperty(
        name="Report Language",
        description="Design report language",
        items=(
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
            ("en_US", "English (English)", ""),
            ("es", "Spanish (Español)", ""),
            ("fr_FR", "French (Français)", ""),
            ("it_IT", "Italian (Italiano)", ""),
            ("ru_RU", "Russian (Русский)", ""),
            ("zh_CN", "Simplified Chinese (简体中文)", ""),
        ),
    )
    warn_hidden_gems: BoolProperty(
        name="Hidden Gems",
        description="Enable or disable given warning",
        default=True,
    )
    warn_gem_overlap: BoolProperty(
        name="Overlapping Gems",
        description="Enable or disable given warning",
        default=True,
    )
    filepath: StringProperty(
        subtype="FILE_PATH",
        options={"SKIP_SAVE", "HIDDEN"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "lang")

        col = layout.column(heading="Warnings")
        col.prop(self, "warn_hidden_gems")
        col.prop(self, "warn_gem_overlap")

    def execute(self, context):
        import webbrowser

        _gettext = gettext.GetText(context, self.lang).gettext

        Report = report_get.data_collect(self, context)
        report_fmt.data_format(Report, _gettext)
        doc = html_doc.make(Report, self.filename, _gettext)

        with open(self.filepath, "w", encoding="utf-8") as file:
            file.write(doc)
            webbrowser.open(self.filepath)

        return {"FINISHED"}

    def invoke(self, context, event):
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.lang = prefs.design_report_lang
        self.warn_hidden_gems = prefs.warn_hidden_gems
        self.warn_gem_overlap = prefs.warn_gem_overlap

        if bpy.data.is_saved:
            self.filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0] + " Report"
            self.filepath = os.path.join(os.path.dirname(bpy.data.filepath), self.filename + ".html")
        else:
            self.filename = "Design Report"
            self.filepath = os.path.join(os.path.expanduser("~"), "Design Report.html")

        if event.ctrl or not bpy.data.is_saved:
            wm = context.window_manager
            wm.fileselect_add(self)
            return {"RUNNING_MODAL"}

        return self.execute(context)
