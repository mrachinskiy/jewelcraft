# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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


from . import (
    es,
    fr,
    it,
    ru,
    zh_cn,
)


def _convert(dictionary):
    d = {}

    for ctxt, msgs in dictionary.items():
        for msg_key, msg_translation in msgs.items():
            d[(ctxt, msg_key)] = msg_translation

    return d


DICTIONARY = {}

for k, v in (
    ("es", es),
    ("fr_FR", fr),
    ("it_IT", it),
    ("ru_RU", ru),
    ("zh_CN", zh_cn),
):
    DICTIONARY[k] = _convert(v.dictionary)
    v.dictionary.clear()
