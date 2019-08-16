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


from . import (
    es,
    fr,
    ru,
    zh_cn,
)


def _translation_dict(dictionary):
    d = {}

    for ctxt, msgs in dictionary.items():
        for msg_key, msg_translation in msgs.items():
            d[(ctxt, msg_key)] = msg_translation

    return d


DICTIONARY = {
    "es": _translation_dict(es.dictionary),
    "fr_FR": _translation_dict(fr.dictionary),
    "ru_RU": _translation_dict(ru.dictionary),
    "zh_CN": _translation_dict(zh_cn.dictionary),
}

es.dictionary.clear()
fr.dictionary.clear()
ru.dictionary.clear()
zh_cn.dictionary.clear()
