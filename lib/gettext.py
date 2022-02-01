# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2022  Mikhail Rachinskiy
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
    __slots__ = ("lang", "gettext")

    def __init__(self, lang: str) -> None:
        if lang == "AUTO":
            lang = bpy.app.translations.locale

        if lang in DICTIONARY.keys():
            self.lang = lang
            self.gettext = self._gettext
        else:
            self.gettext = self._blank

    def _gettext(self, text: str, ctxt: str = "*") -> str:
        return DICTIONARY[self.lang].get((ctxt, text), text)

    @staticmethod
    def _blank(text, ctxt=None):
        return text
