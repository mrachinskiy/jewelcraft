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


import os
import json

import bpy
from bpy.app.translations import pgettext_iface as _

from .. import var
from . import pathutils


def ul_serialize(ul, filepath, keys, fmt=lambda k, v: v):
    data = [
        {k: fmt(k, getattr(item, k)) for k in keys}
        for item in ul.values()
    ]

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def ul_deserialize(ul, filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

        for data_item in data:
            item = ul.add()
            for k, v in data_item.items():
                setattr(item, k, v)

        ul.index = 0


def asset_libs_serialize():
    if not os.path.exists(var.CONFIG_DIR):
        os.makedirs(var.CONFIG_DIR)

    ul_serialize(
        bpy.context.window_manager.jewelcraft.asset_libs,
        var.ASSET_LIBS_FILEPATH,
        ("name", "path"),
    )


def asset_libs_deserialize():
    if os.path.exists(var.ASSET_LIBS_FILEPATH):
        libs = bpy.context.window_manager.jewelcraft.asset_libs
        libs.clear()
        ul_deserialize(libs, var.ASSET_LIBS_FILEPATH)


def weighting_set_serialize(filepath):
    ul_serialize(
        bpy.context.scene.jewelcraft.weighting_materials,
        filepath,
        ("name", "composition", "density"),
        lambda k, v: round(v, 2) if k == "density" else v,
    )


def weighting_set_deserialize(filename):
    mats = bpy.context.scene.jewelcraft.weighting_materials

    if filename.startswith("JCASSET"):
        for name, dens, comp in var.DEFAULT_WEIGHTING_SETS[filename]:
            item = mats.add()
            item.name = _(name)
            item.composition = comp
            item.density = dens
        mats.index = 0
    else:
        filepath = os.path.join(pathutils.get_weighting_lib_path(), filename)
        ul_deserialize(mats, filepath)
