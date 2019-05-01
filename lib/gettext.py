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


import bpy

from .. import var
from ..localization import DICTIONARY


class GetText:

    def __init__(self, context):
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.lang = prefs.product_report_lang

        if self.lang == "AUTO":
            self.lang = bpy.app.translations.locale

        if self.lang == "es_ES":
            self.lang = "es"

        self.use_gettext = self.lang in DICTIONARY.keys()

    def gettext(self, text, ctxt="*"):
        if self.use_gettext:
            return DICTIONARY[self.lang].get((ctxt, text), text)
        return text
