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

import bpy.utils.previews
from bpy.app.translations import pgettext_iface as _

from .. import var
from . import asset


_cache = {}


def _iface_lang(context):
    view = context.preferences.view

    if view.use_international_fonts and view.use_translate_interface:
        return view.language

    return "DEFAULT"


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
        (k, _(_(v.name, "JewelCraft")), "", pcoll[theme + k].icon_id, i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(var.CUTS.items())
    )

    _cache["cuts__RESULT"] = list_
    _cache["cuts__LANG"] = lang
    _cache["cuts__THEME"] = theme

    return list_


def stones(self, context):
    lang = _iface_lang(context)

    if lang == _cache.get("stones__LANG"):
        return _cache["stones__RESULT"]

    list_ = [
        (k, _(_(v.name, "JewelCraft")), "", i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(var.STONES.items())
    ]

    list_.sort(key=lambda x: x[1])
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
    list_ = []

    if not prefs.weighting_hide_default_sets:
        list_ += [
            (
                "JCASSET_PRECIOUS",
                "[JewelCraft] Precious",
                "Commonly used precious alloys, physical properties taken directly from suppliers",
                "BLANK1",
                0,
            ),
            (
                "JCASSET_PRECIOUS_RU",
                "[JewelCraft] Precious RU (ГОСТ 30649-99)",
                "Set of precious alloys according to Russian regulations",
                "BLANK1",
                1,
            ),
            (
                "JCASSET_BASE",
                "[JewelCraft] Base",
                "Set of base metal alloys, physical properties taken directly from suppliers",
                "BLANK1",
                2,
            ),
        ]

    lib_path = asset.get_weighting_lib_path()

    if os.path.exists(lib_path):
        for i, entry in enumerate(
            (x for x in os.scandir(lib_path) if x.is_file() and x.name.endswith(".json")),
            start=len(list_)
        ):
            id_ = entry.name
            name = os.path.splitext(entry.name)[0] + " "  # Add trailing space to deny UI translation
            list_.append((id_, name, "", "BLANK1", i))

    if list_:
        for id_, name, desc, icon, i in list_:
            if id_ == prefs.weighting_set_autoload:
                list_[i] = (id_, name, desc, "DOT", i)
                break
        else:
            id_, name, desc, icon, i = list_[0]
            list_[0] = (id_, name, desc, "DOT", i)
            prefs.weighting_set_autoload = id_
            context.preferences.is_dirty = True

    list_ = tuple(list_)
    _cache["weighting_set__RESULT"] = list_

    return list_


def weighting_set_refresh(self=None, context=None):
    if "weighting_set__RESULT" in _cache:
        del _cache["weighting_set__RESULT"]


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

    for entry in os.scandir(folder):
        if entry.is_file() and entry.name.endswith(".blend"):
            filename = os.path.splitext(entry.name)[0]
            filepath = os.path.splitext(entry.path)[0]

            if os.path.exists(filepath + ".png"):
                preview_id = str(hash(filepath))
                if preview_id not in pcoll:
                    pcoll.load(preview_id, filepath + ".png", "IMAGE")
                preview = pcoll[preview_id].icon_id
            else:
                preview = no_preview

            app((filename, preview))

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    return tuple(list_)


def assets_refresh(preview_id=None, hard=False):
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
