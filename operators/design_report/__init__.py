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

    temp_filepath = Path(tempfile.gettempdir()) / "design_report_temp.png"
    w = bpy.context.region.width
    h = bpy.context.region.height

    if h > resolution:
        w = round(w / (h / resolution))
    else:
        w = round(w * (resolution / h))

    asset.render_preview(w, resolution, temp_filepath, compression=100)

    with open(temp_filepath, "rb") as f:
        image_string = base64.b64encode(f.read()).decode("utf-8")

    # Cleanup
    # ----------------------------

    temp_filepath.unlink(missing_ok=True)

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
    use_metadata: BoolProperty(
        name="Metadata",
        description="Include metadata in report",
        default=True,
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

        layout.prop(self, "use_metadata")
        layout.prop(self, "show_warnings")

    def execute(self, context):
        import webbrowser
        from ...lib import gettext
        from . import html_doc, report_fmt, report_get

        Report = report_get.data_collect(show_warnings=self.show_warnings, show_metadata=self.use_metadata)

        if Report.is_empty():
            self.report({"ERROR"}, "Nothing to report")
            return {"CANCELLED"}

        _gettext = gettext.GetText(self.report_lang).gettext
        report_fmt.data_format(Report, _gettext)

        self.filepath = str(Path(self.filepath).with_suffix(f".{self.file_format.lower()}"))

        if self.file_format == "HTML":
            preview = None
            if self.use_preview:
                preview = _render_preview_base64(self.preview_resolution)

            doc = html_doc.make(Report, preview, self.filename, _gettext)

            with open(self.filepath, "w", encoding="utf-8") as file:
                file.write(doc)
        else:
            import json
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(Report.asdict(), file, indent=4, ensure_ascii=False)

        webbrowser.open(f"file://{self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        if self.first_run:
            self.first_run = False
            prefs = context.preferences.addons[var.ADDON_ID].preferences
            self.report_lang = prefs.report_lang
            self.use_preview = prefs.report_use_preview
            self.preview_resolution = prefs.report_preview_resolution
            self.use_metadata = prefs.report_use_metadata
            self.file_format = prefs.file_format

        if bpy.data.is_saved:
            blend_path = Path(bpy.data.filepath)
            self.filename = blend_path.stem + " Report"
            self.filepath = str(blend_path.parent / f"{self.filename}.{self.file_format.lower()}")
        else:
            self.filename = "Design Report"
            self.filepath = str(Path.home() / f"Design Report.{self.file_format.lower()}")

        if event.ctrl or not bpy.data.is_saved:
            wm = context.window_manager
            wm.fileselect_add(self)
            return {"RUNNING_MODAL"}

        return self.execute(context)
