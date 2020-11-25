# ##### BEGIN GPL LICENSE BLOCK #####
#
#  mod_update automatic add-on updates.
#  Copyright (C) 2019-2020  Mikhail Rachinskiy
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
import json
from typing import Dict, Tuple, Iterator


Translation = Dict[Tuple[str, str], str]


def _convert(d: Dict[str, Dict[str, str]]) -> Translation:
    return {
        (ctxt, msg_key): msg_translation
        for ctxt, msgs in d.items()
        for msg_key, msg_translation in msgs.items()
    }


def _walk() -> Iterator[Tuple[str, Translation]]:
    for entry in os.scandir(os.path.dirname(__file__)):
        if entry.is_file() and entry.name.endswith(".json"):
            with open(entry, "r", encoding="utf-8") as file:
                yield os.path.splitext(entry.name)[0], _convert(json.load(file))


def extend(d: Dict[str, Translation]) -> None:
    for k, v in _walk():
        if k in d.keys():
            d[k].update(v)
        else:
            d[k] = v
