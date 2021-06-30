# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


import pickle
from pathlib import Path
from collections.abc import Iterator


def _po_parse(text: str) -> dict[tuple[str, str], str]:
    import re
    concat_multiline = text.replace('"\n"', "")
    entries = re.findall(r'(?:msgctxt\s*"(.+)")?\s*msgid\s*"(.+)"\s*msgstr\s*"(.*)"', concat_multiline)

    return {
        (ctxt or "*", key.replace("\\n", "\n")): msg.replace("\\n", "\n")
        for ctxt, key, msg in entries
        if msg
    }


def _walk() -> Iterator[tuple[str, dict[tuple[str, str], str]]]:
    for child in Path(__file__).parent.iterdir():
        if child.is_file() and child.suffix == ".po":
            with open(child, "r", encoding="utf-8") as file:
                yield child.stem, _po_parse(file.read())


def _init() -> dict[str, dict[tuple[str, str], str]]:
    path = Path(__file__).parent / "__cache__.pickle"

    if path.exists():
        with open(path, "rb") as file:
            return pickle.load(file)

    dictionary = {locale: trnsl for locale, trnsl in _walk()}

    from ..mod_update import localization
    localization.extend(dictionary)

    with open(path, "wb") as file:
        pickle.dump(dictionary, file, pickle.HIGHEST_PROTOCOL)

    return dictionary


DICTIONARY = _init()
