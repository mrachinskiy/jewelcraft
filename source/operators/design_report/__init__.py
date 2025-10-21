# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty
from bpy.types import Operator

from ... import preferences, var


def _render_preview_base64(resolution: int) -> str:
    import base64
    import tempfile
    from ...lib import asset

    w = bpy.context.region.width
    h = bpy.context.region.height

    if h > resolution:
        w = round(w / (h / resolution))
    else:
        w = round(w * (resolution / h))

    with tempfile.TemporaryDirectory() as tempdir:
        filepath = Path(tempdir) / "design_report_temp.png"
        asset.render_preview(w, resolution, filepath, compression=100)
        with open(filepath, "rb") as f:
            image_string = base64.b64encode(f.read()).decode("utf-8")

    return image_string


class WM_OT_design_report(preferences.ReportLangEnum, Operator):
    bl_label = "Save Design Report"
    bl_description = "Present summary information about the design, including gems, sizes and weight"
    bl_idname = "wm.jewelcraft_design_report"

    file_format: EnumProperty(
        name="Format",
        items=(
            ("HTML", "HTML", ""),
            ("JSON", "JSON", ""),
        ),
    )
    use_preview: BoolProperty(
        name="Preview",
        description="Include viewport preview image in report",
        default=True,
    )
    preview_resolution: IntProperty(
        name="Preview Resolution",
        default=512,
        subtype="PIXEL",
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

        layout.prop(self, "file_format")
        layout.prop(self, "report_lang")

        row = layout.row(heading="Preview")
        row.prop(self, "use_preview", text="")
        sub = row.row()
        sub.enabled = self.use_preview
        sub.prop(self, "preview_resolution", text="")

        layout.prop(self, "show_warnings")

    def execute(self, context):
        import webbrowser
        from ...lib import gettext
        from . import html_doc, report_fmt, report_get

        Report = report_get.data_collect(show_warnings=self.show_warnings)

        if Report.is_empty():
            self.report({"ERROR"}, "Nothing to report")
            return {"CANCELLED"}

        _gettext = gettext.GetText(self.report_lang).gettext
        report_fmt.data_format(Report, _gettext, self.file_format == "HTML")

        self.filepath = str(Path(self.filepath).with_suffix("." + self.file_format.lower()))

        if self.file_format == "HTML":
            preview = None
            if self.use_preview:
                preview = _render_preview_base64(self.preview_resolution)

            doc = html_doc.make(Report, preview, Path(self.filepath).stem, _gettext)
            with open(self.filepath, "w", encoding="utf-8") as file:
                file.write(doc)
        else:
            import json
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(Report.asdict(), file, indent=4, ensure_ascii=False)

        if not bpy.app.background:
            webbrowser.open(f"file://{self.filepath}")

        return {"FINISHED"}

    def invoke(self, context, event):
        if self.first_run:
            self.first_run = False
            prefs = context.preferences.addons[var.ADDON_ID].preferences
            self.report_lang = prefs.report_lang
            self.use_preview = prefs.report_use_preview
            self.preview_resolution = prefs.report_preview_resolution
            self.file_format = prefs.file_format

        if bpy.data.is_saved:
            blend_path = Path(bpy.data.filepath)
            self.filepath = str(blend_path.parent / f"{blend_path.stem} Report.{self.file_format.lower()}")
        else:
            self.filepath = str(Path.home() / f"Design Report.{self.file_format.lower()}")

        if event.ctrl or not bpy.data.is_saved:
            wm = context.window_manager
            wm.fileselect_add(self)
            return {"RUNNING_MODAL"}

        return self.execute(context)
