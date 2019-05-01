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
from bpy.app.translations import pgettext_tip as _

from . import report_fmt, report_get
from .. import var
from ..lib import asset


class WM_OT_jewelcraft_product_report(Operator):
    bl_label = "JewelCraft Product Report"
    bl_description = "Present summary information about product, including sizes, weight and used gems"
    bl_idname = "wm.jewelcraft_product_report"

    def execute(self, context):
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        use_save = prefs.product_report_save
        data_raw = report_get.data_collect(context)
        data_fmt = report_fmt.data_format(context, data_raw)
        warnf = [_(x) for x in data_raw["warn"]]

        # Compose text datablock
        # ---------------------------

        if warnf:
            sep = "-" * 30
            warn_fmt = _("WARNING") + "\n"
            warn_fmt = sep + "\n"

            for msg in warnf:
                warn_fmt += f"* {msg}\n"

            warn_fmt += sep + "\n\n"
            data_fmt = warn_fmt + data_fmt

        if "JewelCraft Product Report" in bpy.data.texts:
            txt = bpy.data.texts["JewelCraft Product Report"]
            txt.clear()
        else:
            txt = bpy.data.texts.new("JewelCraft Product Report")

        txt.write(data_fmt)
        txt.current_line_index = 0

        # Save to file
        # ---------------------------

        if use_save and bpy.data.is_saved:
            filepath = bpy.data.filepath
            filename = os.path.splitext(os.path.basename(filepath))[0]
            save_path = os.path.join(os.path.dirname(filepath), filename + " Report.txt")

            with open(save_path, "w", encoding="utf-8") as file:
                file.write(data_fmt)

        # Display
        # ---------------------------

        if prefs.product_report_display:
            asset.show_window(800, 540, area_type="TEXT_EDITOR", space_data={"text": txt})

        elif warnf or use_save:

            def draw(self_local, context):
                for msg in warnf:
                    self_local.layout.label(text=msg, icon="ERROR")
                    self.report({"WARNING"}, msg)

                if use_save:
                    if bpy.data.is_saved:
                        msg = _("Text file successfully created in the project folder")
                        report_icon = "BLANK1"
                        report_type = {"INFO"}
                    else:
                        msg = _("Could not create text file, project folder does not exist")
                        report_icon = "ERROR"
                        report_type = {"WARNING"}

                    self_local.layout.label(text=msg, icon=report_icon)
                    self.report(report_type, msg)

            context.window_manager.popup_menu(draw, title=_("Product Report"))

        return {"FINISHED"}
