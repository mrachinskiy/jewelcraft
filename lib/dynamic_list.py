# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from pathlib import Path
from functools import lru_cache
from typing import Optional, Union

import bpy
from bpy.app.translations import pgettext_iface as _

from .. import var
from . import pathutils, previewlib


EnumItems3 = tuple[tuple[str, str, str], ...]
EnumItems4 = tuple[tuple[str, str, str, int], ...]
EnumItems5 = tuple[tuple[str, str, str, Union[str, int], int], ...]
AssetItems = tuple[tuple[str, str, int, bool], ...]


def _iface_lang(context) -> str:
    view = context.preferences.view

    if view.use_translate_interface:
        return view.language

    return "en_US"


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

    pcoll = previewlib.scan_icons("cuts", var.GEM_ASSET_DIR)
    theme = "DARK" if color < 0.5 else "LIGHT"

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


def weighting_lib_refresh(self=None, context=None) -> None:
    bpy.context.window_manager.jewelcraft.weighting_lists.clear()


def weighting_lib() -> None:
    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
    lib = bpy.context.window_manager.jewelcraft.weighting_lists

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

    list_ = []
    app = list_.append
    favs = _favs_deserialize()

    for child in folder.iterdir():
        if child.is_file() and child.suffix == ".blend":
            filepath = str(child)
            app((filepath, child.stem, previewlib.asset_img(filepath), filepath in favs))

    return tuple(list_)


@lru_cache(maxsize=1)
def favorites() -> AssetItems:
    if not var.ASSET_FAVS_FILEPATH.exists():
        return ()

    import json

    list_ = []
    app = list_.append

    with open(var.ASSET_FAVS_FILEPATH, "r", encoding="utf-8") as file:
        for filepath in json.load(file):
            app((filepath, Path(filepath).stem, previewlib.asset_img(filepath), True))

    return tuple(list_)


@lru_cache(maxsize=1)
def _favs_deserialize() -> frozenset[str]:
    if not var.ASSET_FAVS_FILEPATH.exists():
        return ()

    import json

    with open(var.ASSET_FAVS_FILEPATH, "r", encoding="utf-8") as file:
        return frozenset(json.load(file))


def assets_refresh(preview_id: Optional[str] = None, favs: bool = False) -> None:
    if preview_id is not None:
        previewlib.asset_img_del(preview_id)

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
