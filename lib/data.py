# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from collections.abc import Callable
from pathlib import Path

import bpy
from bpy.app.translations import pgettext_iface as _

from .. import var
from . import pathutils


def ul_serialize(ul, filepath: Path) -> None:
    data = [item.serialize() for item in ul.values() if hasattr(item, "builtin") and not item.builtin]

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def ul_deserialize(ul, filepath: Path, fmt: Callable = lambda k, v: v, is_builtin=False) -> None:
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

        for data_item in data:
            item = ul.add()
            for k, v in data_item.items():
                item[k] = fmt(k, v)
            if is_builtin:
                item["builtin"] = True

        ul["index"] = 0


def gem_colors_serialize() -> None:
    if not var.CONFIG_DIR.exists():
        var.CONFIG_DIR.mkdir(parents=True)

    ul_serialize(
        bpy.context.window_manager.jewelcraft.gem_colors,
        var.COLORS_FILEPATH,
    )


def gem_colors_deserialize() -> None:

    def _hex_to_rgb(k, v):
        from . import colorlib
        if k == "color":
            return colorlib.hex_to_rgb(v)
        return v

    colors = bpy.context.window_manager.jewelcraft.gem_colors

    if colors.coll:
        return

    colors.clear()
    ul_deserialize(colors, var.GEM_ASSET_DIR / "colors.json", fmt=_hex_to_rgb, is_builtin=True)

    if var.COLORS_FILEPATH.exists():
        ul_deserialize(colors, var.COLORS_FILEPATH, fmt=_hex_to_rgb)


def asset_libs_serialize() -> None:
    if not var.CONFIG_DIR.exists():
        var.CONFIG_DIR.mkdir(parents=True)

    ul_serialize(
        bpy.context.window_manager.jewelcraft.asset_libs,
        var.ASSET_LIBS_FILEPATH,
    )


def asset_libs_deserialize(is_on_load=False) -> None:
    if var.ASSET_LIBS_FILEPATH.exists():
        libs = bpy.context.window_manager.jewelcraft.asset_libs

        if is_on_load and libs.coll:
            return

        libs.clear()
        ul_deserialize(libs, var.ASSET_LIBS_FILEPATH)


def report_metadata_serialize(self=None, context=None) -> None:
    if not var.CONFIG_DIR.exists():
        var.CONFIG_DIR.mkdir(parents=True)

    ul_serialize(
        bpy.context.window_manager.jewelcraft.report_metadata,
        var.REPORT_METADATA_USER_FILEPATH,
    )


def report_metadata_deserialize() -> None:
    if var.REPORT_METADATA_USER_FILEPATH.exists():
        filepath = var.REPORT_METADATA_USER_FILEPATH
    else:
        filepath = var.REPORT_METADATA_BUILTIN_FILEPATH

    ul = bpy.context.window_manager.jewelcraft.report_metadata

    if ul.coll:
        return

    ul.clear()
    ul_deserialize(ul, filepath)


def weighting_list_deserialize(name: str) -> None:

    def _translate_item_name(k, v):
        if k == "name":
            return _(v)
        return v

    mats = bpy.context.scene.jewelcraft.weighting_materials

    if name.startswith("BUILTIN/"):
        filepath = var.WEIGHTING_LIB_BUILTIN_DIR / (name[len("BUILTIN/"):] + ".json")
        ul_deserialize(mats, filepath, fmt=_translate_item_name)
    else:
        filepath = pathutils.get_weighting_list_filepath(name)
        ul_deserialize(mats, filepath)


def versioning_asset_favs():
    if not var.ASSET_FAVS_FILEPATH.exists():
        return

    with open(var.ASSET_FAVS_FILEPATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not (data and Path(data[0]).suffix == ""):
        return

    data_new = [str(Path(x).with_suffix(".blend")) for x in data]

    with open(var.ASSET_FAVS_FILEPATH, "w", encoding="utf-8") as file:
        json.dump(data_new, file, indent=4, ensure_ascii=False)
