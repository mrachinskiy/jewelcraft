# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty

from .. import var


class WM_OT_design_report(Operator):
    bl_label = "Save Design Report"
    bl_description = "Present summary information about the design, including gems, sizes and weight"
    bl_idname = "wm.jewelcraft_design_report"

    lang: EnumProperty(
        name="Report Language",
        description="Report language",
        items=(
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
            ("ar_EG", "Arabic (ﺔﻴﺑﺮﻌﻟﺍ)", ""),
            ("en_US", "English (English)", ""),
            ("es", "Spanish (Español)", ""),
            ("fr_FR", "French (Français)", ""),
            ("it_IT", "Italian (Italiano)", ""),
            ("ru_RU", "Russian (Русский)", ""),
            ("zh_CN", "Simplified Chinese (简体中文)", ""),
        ),
    )
    show_warnings: BoolProperty(
        name="Warnings",
        default=True,
    )
    filepath: StringProperty(
        subtype="FILE_PATH",
        options={"SKIP_SAVE", "HIDDEN"},
    )
    first_run: BoolProperty(default=True, options={"HIDDEN"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "lang")
        layout.prop(self, "show_warnings")

    def execute(self, context):
        import webbrowser
        from ..lib import gettext
        from . import report_get, report_fmt, html_doc

        Report = report_get.data_collect(show_warnings=self.show_warnings)

        if Report.is_empty():
            self.report({"ERROR"}, "Nothing to report")
            return {"CANCELLED"}

        _gettext = gettext.GetText(self.lang).gettext
        report_fmt.data_format(Report, _gettext)
        doc = html_doc.make(Report, self.filename, _gettext)

        with open(self.filepath, "w", encoding="utf-8") as file:
            file.write(doc)
            webbrowser.open(self.filepath)

        return {"FINISHED"}

    def invoke(self, context, event):
        if self.first_run:
            self.first_run = False
            prefs = context.preferences.addons[var.ADDON_ID].preferences
            self.lang = prefs.design_report_lang

        if bpy.data.is_saved:
            blend_path = Path(bpy.data.filepath)
            self.filename = blend_path.stem + " Report"
            self.filepath = str(blend_path.parent / (self.filename + ".html"))
        else:
            self.filename = "Design Report"
            self.filepath = str(Path.home() / "Design Report.html")

        if event.ctrl or not bpy.data.is_saved:
            wm = context.window_manager
            wm.fileselect_add(self)
            return {"RUNNING_MODAL"}

        return self.execute(context)
