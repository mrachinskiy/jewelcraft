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


from pathlib import Path
from functools import lru_cache
from typing import Optional, Union
from collections.abc import Mapping

import bpy
from bpy.app.translations import pgettext_iface as _
from bpy.types import ImagePreview

from .. import var
from . import pathutils


EnumItems3 = tuple[tuple[str, str, str], ...]
EnumItems4 = tuple[tuple[str, str, str, int], ...]
EnumItems5 = tuple[tuple[str, str, str, Union[str, int], int], ...]
AssetItems = tuple[tuple[str, str, int, bool], ...]


def _iface_lang(context) -> str:
    view = context.preferences.view

    if view.use_translate_interface:
        return view.language

    return "en_US"


def scan_icons() -> None:
    import bpy.utils.previews

    pcoll = bpy.utils.previews.new()

    for child in var.ICONS_DIR.iterdir():
        if child.is_file() and child.suffix == ".png":
            pcoll.load(child.stem.upper(), str(child), "IMAGE")
        elif child.is_dir():
            for subchild in child.iterdir():
                if subchild.is_file() and subchild.suffix == ".png":
                    filename = child.name + subchild.stem
                    pcoll.load(filename.upper(), str(subchild), "IMAGE")

    var.preview_collections["icons"] = pcoll


def _get_icon(name: str) -> int:
    if "icons" not in var.preview_collections:
        scan_icons()

    return var.preview_collections["icons"][name].icon_id


def _preview_get(filepath: str, pcoll: Mapping[str, ImagePreview], default: int) -> int:
    if Path(filepath + ".png").exists():
        preview_id = str(hash(filepath))
        if preview_id not in pcoll:
            pcoll.load(preview_id, filepath + ".png", "IMAGE")
        return pcoll[preview_id].icon_id

    return default


# Gems
# ---------------------------


def cuts(self, context) -> EnumItems5:
    lang = _iface_lang(context)
    color = context.preferences.themes[0].user_interface.wcol_menu_item.text.v

    return _cuts(lang, color)


def stones(self, context) -> EnumItems4:
    lang = _iface_lang(context)

    return _stones(lang)


@lru_cache(maxsize=1)
def _cuts(lang: str, color: float) -> EnumItems5:
    from . import gemlib

    theme = "DARK" if color < 0.5 else "LIGHT"
    pcoll = var.preview_collections.get("cuts")

    if not pcoll:
        import bpy.utils.previews

        pcoll = bpy.utils.previews.new()

        for child in var.GEM_ASSET_DIR.iterdir():
            if child.is_dir():
                for subchild in child.iterdir():
                    if subchild.is_file() and subchild.suffix == ".png":
                        preview_id = child.name + subchild.stem
                        pcoll.load(preview_id.upper(), str(subchild), "IMAGE")

        var.preview_collections["cuts"] = pcoll

    return tuple(
        (k, _(_(v.name, "Jewelry")), "", pcoll[theme + k].icon_id, i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(gemlib.CUTS.items())
    )


@lru_cache(maxsize=1)
def _stones(lang: str) -> EnumItems4:
    import operator
    from . import gemlib

    list_ = [
        (k, _(_(v.name, "Jewelry")), "", i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(gemlib.STONES.items())
    ]

    list_.sort(key=operator.itemgetter(1))

    return tuple(list_)


# Weighting
# ---------------------------


_wlib_cache = False


def weighting_lib_refresh(self=None, context=None) -> None:
    global _wlib_cache
    _wlib_cache = False


def weighting_lib() -> None:
    global _wlib_cache

    if _wlib_cache:
        return

    _wlib_cache = True
    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
    lib = bpy.context.window_manager.jewelcraft.weighting_lists
    lib.clear()

    if not prefs.weighting_hide_builtin_lists:
        for child in var.WEIGHTING_LIB_BUILTIN_DIR.iterdir():
            if child.is_file() and child.suffix == ".json":
                item = lib.add()
                item["name"] = child.stem
                item.builtin = True

    lib_path = pathutils.get_weighting_lib_path()

    if lib_path.exists():
        for child in lib_path.iterdir():
            if child.is_file() and child.suffix == ".json":
                item = lib.add()
                item["name"] = item.name_orig = child.stem

    if lib:
        for item in lib:
            if prefs.weighting_default_list == item.load_id:
                item.default = True
                return
        else:
            prefs.weighting_default_list = lib[0].load_id
            lib[0].default = True
            bpy.context.preferences.is_dirty = True


def weighting_materials(self, context) -> EnumItems3:
    return _weighting_materials()


def weighting_materials_refresh(self=None, context=None) -> None:
    _weighting_materials.cache_clear()


@lru_cache(maxsize=1)
def _weighting_materials() -> EnumItems3:
    props = bpy.context.scene.jewelcraft

    return tuple(
        (str(i), mat.name + " ", "")  # Add trailing space to deny UI translation
        for i, mat in enumerate(props.weighting_materials.values())
    )


# Assets
# ---------------------------


def asset_folders(self, context) -> EnumItems3:
    return _asset_folders()


def asset_folders_refresh() -> None:
    _asset_folders.cache_clear()


@lru_cache(maxsize=1)
def _asset_folders() -> EnumItems3:
    folder = pathutils.get_asset_lib_path()

    if not folder.exists():
        return ()

    return tuple(
        (child.name, child.name + " ", "")  # Add trailing space to deny UI translation
        for child in folder.iterdir()
        if child.is_dir() and not child.name.startswith(".")
    )


@lru_cache(maxsize=32)
def assets(lib_path: Path, category: str) -> AssetItems:
    folder = lib_path / category

    if not folder.exists():
        return ()

    pcoll = var.preview_collections.get("assets")

    if not pcoll:
        import bpy.utils.previews
        pcoll = bpy.utils.previews.new()

    list_ = []
    app = list_.append
    no_preview = _get_icon("NO_PREVIEW")
    favs = _favs_deserialize()

    for child in folder.iterdir():
        if child.is_file() and child.suffix == ".blend":
            filepath = str(child.with_suffix(""))
            app((filepath, child.stem, _preview_get(filepath, pcoll, no_preview), filepath in favs))

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    return tuple(list_)


@lru_cache(maxsize=1)
def favorites() -> AssetItems:
    if not var.ASSET_FAVS_FILEPATH.exists():
        return ()

    import json

    pcoll = var.preview_collections.get("assets")

    if not pcoll:
        import bpy.utils.previews
        pcoll = bpy.utils.previews.new()

    list_ = []
    app = list_.append
    no_preview = _get_icon("NO_PREVIEW")

    with open(var.ASSET_FAVS_FILEPATH, "r", encoding="utf-8") as file:
        for filepath in json.load(file):
            app((filepath, Path(filepath).name, _preview_get(filepath, pcoll, no_preview), True))

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    return tuple(list_)


@lru_cache(maxsize=1)
def _favs_deserialize() -> frozenset[str]:
    if not var.ASSET_FAVS_FILEPATH.exists():
        return ()

    import json

    with open(var.ASSET_FAVS_FILEPATH, "r", encoding="utf-8") as file:
        return frozenset(json.load(file))


def assets_refresh(preview_id: Optional[str] = None, hard: bool = False, favs: bool = False) -> None:
    if preview_id or hard:
        pcoll = var.preview_collections.get("assets")

        if pcoll:
            import bpy.utils.previews

            if preview_id:
                preview_id = str(hash(preview_id))

                if preview_id in pcoll:
                    del pcoll[preview_id]
                    if not pcoll:
                        bpy.utils.previews.remove(pcoll)
                        del var.preview_collections["assets"]

            elif hard:
                bpy.utils.previews.remove(pcoll)
                del var.preview_collections["assets"]

    if favs:
        _favs_deserialize.cache_clear()
        favorites.cache_clear()

    assets.cache_clear()


# Other
# ---------------------------


def abc(self, context) -> EnumItems3:
    return _abc()


@lru_cache(maxsize=1)
def _abc() -> EnumItems3:
    import string
    return tuple((str(i), char, "") for i, char in enumerate(string.ascii_uppercase))
