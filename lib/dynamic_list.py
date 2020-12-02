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
from functools import lru_cache
from typing import Mapping, Optional, Tuple, FrozenSet, Union

from bpy.app.translations import pgettext_iface as _
from bpy.types import ImagePreview

from .. import var
from . import pathutils


EnumItems3 = Tuple[Tuple[str, str, str], ...]
EnumItems4 = Tuple[Tuple[str, str, str, int], ...]
EnumItems5 = Tuple[Tuple[str, str, str, Union[str, int], int], ...]
AssetItems = Tuple[Tuple[str, str, int, bool], ...]

_cache = {}


def _iface_lang(context) -> str:
    view = context.preferences.view

    if view.use_translate_interface:
        return view.language

    return "en_US"


def scan_icons() -> None:
    import bpy.utils.previews

    pcoll = bpy.utils.previews.new()

    for entry in os.scandir(var.ICONS_DIR):
        if entry.is_file() and entry.name.endswith(".png"):
            filename = os.path.splitext(entry.name)[0]
            pcoll.load(filename.upper(), entry.path, "IMAGE")
        elif entry.is_dir():
            for subentry in os.scandir(entry.path):
                if subentry.is_file() and subentry.name.endswith(".png"):
                    filename = entry.name + os.path.splitext(subentry.name)[0]
                    pcoll.load(filename.upper(), subentry.path, "IMAGE")

    var.preview_collections["icons"] = pcoll


def _get_icon(name: str) -> int:
    if "icons" not in var.preview_collections:
        scan_icons()

    return var.preview_collections["icons"][name].icon_id


def _preview_get(filepath: str, pcoll: Mapping[str, ImagePreview], default: int) -> int:
    if os.path.exists(filepath + ".png"):
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

    if lang == _cache.get("cuts__LANG") and color == _cache.get("cuts__COLOR"):
        return _cache["cuts__RESULT"]

    from . import gemlib

    theme = "DARK" if color < 0.5 else "LIGHT"
    pcoll = var.preview_collections.get("cuts")

    if not pcoll:
        import bpy.utils.previews

        pcoll = bpy.utils.previews.new()

        for entry in os.scandir(var.GEM_ASSET_DIR):
            if entry.is_dir():
                for subentry in os.scandir(entry.path):
                    if subentry.is_file() and subentry.name.endswith(".png"):
                        preview_id = entry.name + os.path.splitext(subentry.name)[0]
                        pcoll.load(preview_id.upper(), subentry.path, "IMAGE")

        var.preview_collections["cuts"] = pcoll

    list_ = tuple(
        (k, _(_(v.name, "Jewelry")), "", pcoll[theme + k].icon_id, i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(gemlib.CUTS.items())
    )

    _cache["cuts__RESULT"] = list_
    _cache["cuts__LANG"] = lang
    _cache["cuts__COLOR"] = color

    return list_


def stones(self, context) -> EnumItems4:
    lang = _iface_lang(context)

    if lang == _cache.get("stones__LANG"):
        return _cache["stones__RESULT"]

    import operator
    from . import gemlib

    list_ = [
        (k, _(_(v.name, "Jewelry")), "", i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(gemlib.STONES.items())
    ]

    list_.sort(key=operator.itemgetter(1))
    list_ = tuple(list_)

    _cache["stones__RESULT"] = list_
    _cache["stones__LANG"] = lang

    return list_


# Weighting
# ---------------------------


def weighting_set(self, context) -> EnumItems4:
    if "weighting_set__RESULT" in _cache:
        return _cache["weighting_set__RESULT"]

    prefs = context.preferences.addons[var.ADDON_ID].preferences
    lib_path = pathutils.get_weighting_lib_path()
    wsets = {}
    list_ = []

    if not prefs.weighting_hide_default_sets:
        wsets["JCASSET_PRECIOUS"] = (
            "Precious",
            "Commonly used precious alloys, physical properties taken directly from suppliers",
        )
        wsets["JCASSET_PRECIOUS_RU"] = (
            "Precious RU (ГОСТ 30649-99)",
            "Set of precious alloys according to Russian regulations",
        )
        wsets["JCASSET_BASE"] = (
            _("Base", "Jewelry"),
            "Set of base metal alloys, physical properties taken directly from suppliers",
        )

    if os.path.exists(lib_path):
        for entry in os.scandir(lib_path):
            if entry.is_file() and entry.name.endswith(".json"):
                name = os.path.splitext(entry.name)[0] + " "  # Add trailing space to deny UI translation
                wsets[entry.name] = (name, "")

    if wsets:

        if prefs.weighting_set_autoload not in wsets:
            prefs.weighting_set_autoload = next(iter(wsets))
            context.preferences.is_dirty = True

        i = 1

        for k, v in wsets.items():
            if k == prefs.weighting_set_autoload:
                list_.append((k, *v, "DOT", 0))
            else:
                list_.append((k, *v, "BLANK1", i))
                i += 1

    list_ = tuple(list_)
    _cache["weighting_set__RESULT"] = list_

    return list_


def weighting_set_refresh(self=None, context=None) -> None:
    if "weighting_set__RESULT" in _cache:
        del _cache["weighting_set__RESULT"]

    if context is not None:
        context.window_manager.jewelcraft.property_unset("weighting_set")


def weighting_materials(self, context) -> EnumItems3:
    if "weighting_materials__RESULT" in _cache:
        return _cache["weighting_materials__RESULT"]

    props = context.scene.jewelcraft

    list_ = tuple(
        (str(i), mat.name + " ", "")  # Add trailing space to deny UI translation
        for i, mat in enumerate(props.weighting_materials.values())
    )

    _cache["weighting_materials__RESULT"] = list_

    return list_


def weighting_materials_refresh(self=None, context=None) -> None:
    if "weighting_materials__RESULT" in _cache:
        del _cache["weighting_materials__RESULT"]


# Assets
# ---------------------------


def asset_folders(self, context) -> EnumItems3:
    if "asset_folders__RESULT" in _cache:
        return _cache["asset_folders__RESULT"]

    folder = pathutils.get_asset_lib_path()

    if not os.path.exists(folder):
        _cache["asset_folders__RESULT"] = ()
        return ()

    list_ = tuple(
        (entry.name, entry.name + " ", "")  # Add trailing space to deny UI translation
        for entry in os.scandir(folder)
        if entry.is_dir() and not entry.name.startswith(".")
    )

    _cache["asset_folders__RESULT"] = list_

    return list_


def asset_folders_refresh() -> None:
    if "asset_folders__RESULT" in _cache:
        del _cache["asset_folders__RESULT"]


@lru_cache(maxsize=32)
def assets(lib_path: str, category: str) -> AssetItems:
    folder = os.path.join(lib_path, category)

    if not os.path.exists(folder):
        return ()

    pcoll = var.preview_collections.get("assets")

    if not pcoll:
        import bpy.utils.previews
        pcoll = bpy.utils.previews.new()

    list_ = []
    app = list_.append
    no_preview = _get_icon("NO_PREVIEW")
    favs = _favs_deserialize()

    for entry in os.scandir(folder):
        if entry.is_file() and entry.name.endswith(".blend"):
            filename = os.path.splitext(entry.name)[0]
            filepath = os.path.splitext(entry.path)[0]
            app((filepath, filename, _preview_get(filepath, pcoll, no_preview), filepath in favs))

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    return tuple(list_)


@lru_cache(maxsize=1)
def favorites() -> AssetItems:
    if not os.path.exists(var.ASSET_FAVS_FILEPATH):
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
            filename = os.path.basename(filepath)
            app((filepath, filename, _preview_get(filepath, pcoll, no_preview), True))

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    return tuple(list_)


@lru_cache(maxsize=1)
def _favs_deserialize() -> FrozenSet[str]:
    if not os.path.exists(var.ASSET_FAVS_FILEPATH):
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
    if "abc__RESULT" in _cache:
        return _cache["abc__RESULT"]

    import string

    list_ = tuple((str(i), char, "") for i, char in enumerate(string.ascii_uppercase))
    _cache["abc__RESULT"] = list_

    return list_
