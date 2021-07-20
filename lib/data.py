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


import json
from pathlib import Path
from collections.abc import Callable

import bpy
from bpy.app.translations import pgettext_iface as _

from .. import var
from . import pathutils


def _translate_item_name(k, v):
    if k == "name":
        return _(v)
    return v


def ul_serialize(ul, filepath: Path, keys: tuple[str], fmt: Callable = lambda k, v: v) -> None:
    data = [
        {k: fmt(k, getattr(item, k)) for k in keys}
        for item in ul.values()
    ]

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def ul_deserialize(ul, filepath: Path, fmt: Callable = lambda k, v: v) -> None:
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

        for data_item in data:
            item = ul.add()
            for k, v in data_item.items():
                setattr(item, k, fmt(k, v))

        ul.index = 0


def asset_libs_serialize() -> None:
    if not var.CONFIG_DIR.exists():
        var.CONFIG_DIR.mkdir(parents=True)

    ul_serialize(
        bpy.context.window_manager.jewelcraft.asset_libs,
        var.ASSET_LIBS_FILEPATH,
        ("name", "path"),
    )


def asset_libs_deserialize() -> None:
    if var.ASSET_LIBS_FILEPATH.exists():
        libs = bpy.context.window_manager.jewelcraft.asset_libs
        libs.clear()
        ul_deserialize(libs, var.ASSET_LIBS_FILEPATH)


def weighting_list_serialize(filepath: Path) -> None:
    ul_serialize(
        bpy.context.scene.jewelcraft.weighting_materials,
        filepath,
        ("name", "composition", "density"),
        lambda k, v: round(v, 2) if k == "density" else v,
    )


def weighting_list_deserialize(name: str) -> None:
    mats = bpy.context.scene.jewelcraft.weighting_materials

    if name.startswith("BUILTIN/"):
        filepath = var.WEIGHTING_LIB_BUILTIN_DIR / (name[len("BUILTIN/"):] + ".json")
        ul_deserialize(mats, filepath, fmt=_translate_item_name)
    else:
        filepath = pathutils.get_weighting_list_filepath(name)
        ul_deserialize(mats, filepath)
