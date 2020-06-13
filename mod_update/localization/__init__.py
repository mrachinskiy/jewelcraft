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


def _get_dicts():
    import os
    import json

    for entry in os.scandir(os.path.dirname(__file__)):
        if entry.is_file() and entry.name.endswith(".json"):
            with open(entry, "r", encoding="utf-8") as file:
                yield json.load(file)


def _convert(dictionary):
    d = {}

    for ctxt, msgs in dictionary.items():
        for msg_key, msg_translation in msgs.items():
            d[(ctxt, msg_key)] = msg_translation

    return d


def dict_init():
    return {k: _convert(v) for k, v in _get_dicts()}
