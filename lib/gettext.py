# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

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
