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

from .. import var
from ..localization import DICTIONARY
from .report_get import DataCollect
from .report_fmt import DataFormat


class WM_OT_jewelcraft_product_report(Operator, DataCollect, DataFormat):
    bl_label = "JewelCraft Product Report"
    bl_description = "Save product report to text file"
    bl_idname = "wm.jewelcraft_product_report"

    def execute(self, context):
        data_raw = self.data_collect(context)
        data_fmt = self.data_format(data_raw)
        warnf = [_(x) for x in data_raw["warn"]]

        # Compose text datablock
        # ---------------------------

        if warnf:
            sep = "—" * max(40, len(max(warnf)) + 2)
            warn_fmt = "{}\n{}\n".format(_("WARNING"), sep)

            for msg in warnf:
                warn_fmt += "-{}\n".format(_(msg))

            warn_fmt += f"{sep}\n\n"
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

        if self.prefs.product_report_save and bpy.data.is_saved:

            filepath = bpy.data.filepath
            filename = os.path.splitext(os.path.basename(filepath))[0]
            save_path = os.path.join(os.path.dirname(filepath), filename + " Report.txt")

            with open(save_path, "w", encoding="utf-8") as file:
                file.write(data_fmt)

        # Display
        # ---------------------------

        if self.prefs.product_report_display:

            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")

            area = bpy.context.window_manager.windows[-1].screen.areas[0]
            area.type = "TEXT_EDITOR"

            space = area.spaces[0]
            space.text = txt

        elif warnf or self.prefs.product_report_save:

            def draw(self_local, context):

                for msg in warnf:
                    self_local.layout.label(text=msg, icon="ERROR")
                    self.report({"WARNING"}, msg)

                if self.prefs.product_report_save:

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

    def gettext(self, text, ctxt="*"):
        if self.use_gettext:
            return DICTIONARY[self.lang].get((ctxt, text), text)
        return text

    def invoke(self, context, event):
        self.prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.lang = self.prefs.product_report_lang

        if self.lang == "AUTO":
            self.lang = bpy.app.translations.locale

        if self.lang == "es_ES":
            self.lang = "es"

        self.use_gettext = self.lang in DICTIONARY.keys()

        return self.execute(context)
