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

    if _cache.get("cuts__lang") == lang:
        return _cache["cuts__list"]

    pcoll = var.preview_collections.get("cuts")

    if not pcoll:
        pcoll = bpy.utils.previews.new()

        for entry in os.scandir(var.GEM_ASSET_DIR):
            if entry.name.endswith(".png"):
                name = os.path.splitext(entry.name)[0]
                pcoll.load(name.upper(), entry.path, "IMAGE")

        var.preview_collections["cuts"] = pcoll

    list_ = tuple(
        (k, _(_(v.name, "JewelCraft")), "", pcoll[k].icon_id, i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(var.CUTS.items())
    )

    _cache["cuts__list"] = list_
    _cache["cuts__lang"] = lang

    return list_


def stones(self, context):
    lang = _iface_lang(context)

    if _cache.get("stones__lang") == lang:
        return _cache["stones__list"]

    list_ = [
        (k, _(_(v.name, "JewelCraft")), "", i)  # _(_()) default return value workaround
        for i, (k, v) in enumerate(var.STONES.items())
    ]

    list_.sort(key=lambda x: x[1])
    list_ = tuple(list_)

    _cache["stones__list"] = list_
    _cache["stones__lang"] = lang

    return list_


# Weighting
# ---------------------------


def weighting_set(self, context):

    if "weighting_set__list" in _cache:
        return _cache["weighting_set__list"]

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

    folder = asset.user_asset_library_folder_weighting()

    if os.path.exists(folder):
        for i, entry in enumerate(
            (x for x in os.scandir(folder) if x.is_file() and x.name.endswith(".json")),
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
    else:
        list_ = (("", "", "", "BLANK1", 0),)

    list_ = tuple(list_)
    _cache["weighting_set__list"] = list_

    return list_


def weighting_materials(self, context):

    if "weighting_materials__list" in _cache:
        return _cache["weighting_materials__list"]

    props = context.scene.jewelcraft

    list_ = tuple(
        (str(i), mat.name + " ", "")  # Add trailing space to deny UI translation
        for i, mat in enumerate(props.weighting_materials.values())
    )

    if not list_:
        list_ = (("", "", ""),)

    _cache["weighting_materials__list"] = list_

    return list_


def weighting_set_refresh(self=None, context=None):
    if "weighting_set__list" in _cache:
        del _cache["weighting_set__list"]


def weighting_materials_refresh(self=None, context=None):
    if "weighting_materials__list" in _cache:
        del _cache["weighting_materials__list"]


# Assets
# ---------------------------


def asset_folders(self, context):

    if "asset_folders__list" in _cache:
        return _cache["asset_folders__list"]

    folder = asset.user_asset_library_folder_object()

    if not os.path.exists(folder):
        _cache["asset_folders__list"] = (("", "", ""),)
        return (("", "", ""),)

    list_ = tuple(
        (entry.name, entry.name + " ", "")  # Add trailing space to deny UI translation
        for entry in os.scandir(folder)
        if entry.is_dir() and not entry.name.startswith(".")
    )

    if not list_:
        list_ = (("", "", ""),)

    _cache["asset_folders__list"] = list_

    return list_


def assets(self, context):
    category = context.window_manager.jewelcraft.asset_folder

    if "assets__list" in _cache and category == _cache.get("assets__category"):
        return _cache["assets__list"]

    _cache["assets__category"] = category
    folder = os.path.join(asset.user_asset_library_folder_object(), category)

    if not os.path.exists(folder):
        _cache["assets__list"] = (("", "", ""),)
        return (("", "", ""),)

    pcoll = var.preview_collections.get("assets")

    if not pcoll:
        pcoll = bpy.utils.previews.new()

    list_ = []
    app = list_.append
    no_preview = var.preview_collections["icons"]["NO_PREVIEW"].icon_id

    for i, entry in enumerate(x for x in os.scandir(folder) if x.is_file() and x.name.endswith(".blend")):
        filename = os.path.splitext(entry.name)[0]
        preview_id = category + filename
        preview_path = os.path.splitext(entry.path)[0] + ".png"

        if os.path.exists(preview_path):
            if preview_id not in pcoll:
                pcoll.load(preview_id, preview_path, "IMAGE")
            preview = pcoll[preview_id].icon_id
        else:
            preview = no_preview

        app((filename, filename + " ", "", preview, i))  # Add trailing space to deny UI translation

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    if not list_:
        list_ = (("", "", ""),)

    list_ = tuple(list_)
    _cache["assets__list"] = list_

    return list_


def asset_folder_list_refresh():
    if "asset_folders__list" in _cache:
        del _cache["asset_folders__list"]


def asset_list_refresh(preview_id=False, hard=False):
    pcoll = var.preview_collections.get("assets")

    if pcoll:

        if preview_id and preview_id in pcoll:
            del pcoll[preview_id]

            if not pcoll:
                bpy.utils.previews.remove(pcoll)
                del var.preview_collections["assets"]

        elif hard:
            bpy.utils.previews.remove(pcoll)
            del var.preview_collections["assets"]

    if "assets__list" in _cache:
        del _cache["assets__list"]


# Other
# ---------------------------


def abc(self, context):
    if "abc__list" in _cache:
        return _cache["abc__list"]

    import string

    list_ = tuple((str(i), char, "") for i, char in enumerate(string.ascii_uppercase))
    _cache["abc__list"] = list_

    return list_
