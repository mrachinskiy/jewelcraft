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

from ..localization import DICTIONARY


class GetText:
    __slots__ = ("use_gettext", "lang")

    def __init__(self, context, lang):
        if lang == "AUTO":
            lang = bpy.app.translations.locale

        if lang == "es_ES":
            lang = "es"

        self.use_gettext = lang in DICTIONARY.keys()
        self.lang = lang

    def gettext(self, text, ctxt="*"):
        if self.use_gettext:
            return DICTIONARY[self.lang].get((ctxt, text), text)
        return text
