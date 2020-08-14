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

import bpy
import bpy.utils.previews
from bpy.app.translations import pgettext_iface as _

from .. import var
from . import asset


_cache = {}


def _iface_lang(context):
    view = context.preferences.view

    if view.use_translate_interface:
        return view.language

    return "en_US"


# Gems
# ---------------------------


def cuts(self, context):
    lang = _iface_lang(context)
    theme = context.preferences.addons[var.ADDON_ID].preferences.theme_icon

    if lang == _cache.get("cuts__LANG") and theme == _cache.get("cuts__THEME"):
        return _cache["cuts__RESULT"]

    pcoll = var.preview_collections.get("cuts")

    if not pcoll:
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
        for i, (k, v) in enumerate(var.CUTS.items())
    )

    _cache["cuts__RESULT"] = list_
    _cache["cuts__LANG"] = lang
    _cache["cuts__THEME"] = theme

    return list_


def stones(self, context):
    import operator

    lang = _iface_lang(context)

    if lang == _cache.get("stones__LANG"):
        return _cache["stones__RESULT"]

    list_ = [
        (k, _(_(v.name, "Jewelry")), "", i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(var.STONES.items())
    ]

    list_.sort(key=operator.itemgetter(1))
    list_ = tuple(list_)

    _cache["stones__RESULT"] = list_
    _cache["stones__LANG"] = lang

    return list_


# Weighting
# ---------------------------


def weighting_set(self, context):
    if "weighting_set__RESULT" in _cache:
        return _cache["weighting_set__RESULT"]

    prefs = context.preferences.addons[var.ADDON_ID].preferences
    lib_path = asset.get_weighting_lib_path()
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


def weighting_set_refresh(self=None, context=None):
    if "weighting_set__RESULT" in _cache:
        del _cache["weighting_set__RESULT"]

    if context is not None:
        context.window_manager.jewelcraft.property_unset("weighting_set")


def weighting_materials(self, context):
    if "weighting_materials__RESULT" in _cache:
        return _cache["weighting_materials__RESULT"]

    props = context.scene.jewelcraft

    list_ = tuple(
        (str(i), mat.name + " ", "")  # Add trailing space to deny UI translation
        for i, mat in enumerate(props.weighting_materials.values())
    )

    _cache["weighting_materials__RESULT"] = list_

    return list_


def weighting_materials_refresh(self=None, context=None):
    if "weighting_materials__RESULT" in _cache:
        del _cache["weighting_materials__RESULT"]


# Assets
# ---------------------------


def asset_folders(self, context):
    if "asset_folders__RESULT" in _cache:
        return _cache["asset_folders__RESULT"]

    folder = asset.get_asset_lib_path()

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


def asset_folders_refresh():
    if "asset_folders__RESULT" in _cache:
        del _cache["asset_folders__RESULT"]


def _preview_get(filepath, pcoll):
    if os.path.exists(filepath + ".png"):
        preview_id = str(hash(filepath))
        if preview_id not in pcoll:
            pcoll.load(preview_id, filepath + ".png", "IMAGE")
        return pcoll[preview_id].icon_id


@lru_cache(maxsize=32)
def assets(lib_path, category):
    folder = os.path.join(lib_path, category)

    if not os.path.exists(folder):
        return ()

    pcoll = var.preview_collections.get("assets")

    if not pcoll:
        pcoll = bpy.utils.previews.new()

    list_ = []
    app = list_.append
    no_preview = var.preview_collections["icons"]["NO_PREVIEW"].icon_id
    favs = _favs_deserialize()

    for entry in os.scandir(folder):
        if entry.is_file() and entry.name.endswith(".blend"):
            filename = os.path.splitext(entry.name)[0]
            filepath = os.path.splitext(entry.path)[0]
            app((filepath, filename, _preview_get(filepath, pcoll) or no_preview, filepath in favs))

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    return tuple(list_)


@lru_cache(maxsize=1)
def favorites():
    if not os.path.exists(var.ASSET_FAVS_FILEPATH):
        return ()

    import json

    pcoll = var.preview_collections.get("assets")

    if not pcoll:
        pcoll = bpy.utils.previews.new()

    list_ = []
    app = list_.append
    no_preview = var.preview_collections["icons"]["NO_PREVIEW"].icon_id

    with open(var.ASSET_FAVS_FILEPATH, "r", encoding="utf-8") as file:
        for filepath in json.load(file):
            filename = os.path.basename(filepath)
            app((filepath, filename, _preview_get(filepath, pcoll) or no_preview, True))

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    return tuple(list_)


@lru_cache(maxsize=1)
def _favs_deserialize():
    if not os.path.exists(var.ASSET_FAVS_FILEPATH):
        return ()

    import json

    with open(var.ASSET_FAVS_FILEPATH, "r", encoding="utf-8") as file:
        return frozenset(json.load(file))


def assets_refresh(preview_id=None, hard=False, favs=False):
    if preview_id or hard:
        pcoll = var.preview_collections.get("assets")

        if pcoll:

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


def abc(self, context):
    if "abc__RESULT" in _cache:
        return _cache["abc__RESULT"]

    import string

    list_ = tuple((str(i), char, "") for i, char in enumerate(string.ascii_uppercase))
    _cache["abc__RESULT"] = list_

    return list_
