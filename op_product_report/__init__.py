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


import os

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty
from bpy.app.translations import pgettext_tip as _

from . import report_fmt, report_get
from .. import var
from ..lib import asset


class WM_OT_product_report(Operator):
    bl_label = "JewelCraft Product Report"
    bl_description = "Present summary information about the product, including gems, sizes and weight"
    bl_idname = "wm.jewelcraft_product_report"

    lang: EnumProperty(
        name="Report Language",
        description="Product report language",
        items=(
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
            ("en_US", "English (English)", ""),
            ("es", "Spanish (Español)", ""),
            ("fr_FR", "French (Français)", ""),
            ("ru_RU", "Russian (Русский)", ""),
            ("zh_CN", "Simplified Chinese (简体中文)", ""),
        ),
    )
    use_save: BoolProperty(
        name="Save To File",
        description="Save product report to file in project folder",
        default=True,
    )
    show_total_ct: BoolProperty(
        name="Total (ct.)",
        description="Include or exclude given column",
    )
    use_hidden_gems: BoolProperty(
        name="Hidden Gems",
        description="Enable or disable given warning",
        default=True,
    )
    use_overlap: BoolProperty(
        name="Overlapping Gems",
        description="Enable or disable given warning",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.prop(self, "use_save")
        layout.prop(self, "lang")

        layout.label(text="Report")
        layout.prop(self, "show_total_ct")

        layout.label(text="Warnings")
        col = layout.column()
        col.prop(self, "use_hidden_gems")
        col.prop(self, "use_overlap")

        layout.separator()

    def execute(self, context):
        version_281 = bpy.app.version >= (2, 81, 14)
        data_raw = report_get.data_collect(self, context)
        data_fmt = report_fmt.data_format(self, context, data_raw)

        # Compose text datablock
        # ---------------------------

        if data_raw["warn"]:
            sep = "-" * 30
            warn_fmt = sep + "\n"
            warn_fmt += _("WARNING") + "\n"

            for msg in data_raw["warn"]:
                warn_fmt += f"* {_(msg)}\n"

            warn_fmt += sep + "\n\n"
            data_fmt = warn_fmt + data_fmt

        if "Product Report" in bpy.data.texts:
            txt = bpy.data.texts["Product Report"]
            txt.clear()
        else:
            txt = bpy.data.texts.new("Product Report")

        txt.write(data_fmt)

        if version_281:
            txt.cursor_set(0)
        else:
            txt.current_line_index = 0

        # Save to file
        # ---------------------------

        if self.use_save and bpy.data.is_saved:
            filepath = bpy.data.filepath
            filename = os.path.splitext(os.path.basename(filepath))[0]
            save_path = os.path.join(os.path.dirname(filepath), filename + " Report.txt")

            with open(save_path, "w", encoding="utf-8") as file:
                file.write(data_fmt)

        # Display, workaround for T64439
        # ---------------------------

        self.txt = txt
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        space_data = {
            "show_line_numbers": False,
            "show_word_wrap": False,
            "show_syntax_highlight": False,
            "text": self.txt,
        }

        asset.show_window(800, 540, area_type="TEXT_EDITOR", space_data=space_data)

        return {"FINISHED"}

    def invoke(self, context, event):
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.lang = prefs.product_report_lang
        self.use_save = prefs.product_report_save
        self.show_total_ct = prefs.product_report_show_total_ct
        self.use_hidden_gems = prefs.product_report_use_hidden_gems
        self.use_overlap = prefs.product_report_use_overlap

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)
