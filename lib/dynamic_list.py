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
                pcoll.load(name, entry.path, "IMAGE")

        var.preview_collections["cuts"] = pcoll

    list_ = (
        ("ROUND",     _("Round", "JewelCraft"), "", pcoll["round"].icon_id,     0),
        ("OVAL",      _("Oval"),                "", pcoll["oval"].icon_id,      1),
        ("CUSHION",   _("Cushion"),             "", pcoll["cushion"].icon_id,   2),
        ("PEAR",      _("Pear"),                "", pcoll["pear"].icon_id,      3),
        ("MARQUISE",  _("Marquise"),            "", pcoll["marquise"].icon_id,  4),
        ("PRINCESS",  _("Princess"),            "", pcoll["princess"].icon_id,  5),
        ("BAGUETTE",  _("Baguette"),            "", pcoll["baguette"].icon_id,  6),
        ("SQUARE",    _("Square"),              "", pcoll["square"].icon_id,    7),
        ("EMERALD",   _("Emerald"),             "", pcoll["emerald"].icon_id,   8),
        ("ASSCHER",   _("Asscher"),             "", pcoll["asscher"].icon_id,   9),
        ("RADIANT",   _("Radiant"),             "", pcoll["radiant"].icon_id,   10),
        ("FLANDERS",  _("Flanders"),            "", pcoll["flanders"].icon_id,  11),
        ("OCTAGON",   _("Octagon"),             "", pcoll["octagon"].icon_id,   12),
        ("HEART",     _("Heart"),               "", pcoll["heart"].icon_id,     13),
        ("TRILLION",  _("Trillion"),            "", pcoll["trillion"].icon_id,  14),
        ("TRILLIANT", _("Trilliant"),           "", pcoll["trilliant"].icon_id, 15),
        ("TRIANGLE",  _("Triangle"),            "", pcoll["triangle"].icon_id,  16),
    )

    _cache["cuts__list"] = list_
    _cache["cuts__lang"] = lang

    return list_


def stones(self, context):
    lang = _iface_lang(context)

    if _cache.get("stones__lang") == lang:
        return _cache["stones__list"]

    list_ = [
        ("DIAMOND",        _("Diamond"),        "", 0),
        ("ALEXANDRITE",    _("Alexandrite"),    "", 1),
        ("AMETHYST",       _("Amethyst"),       "", 2),
        ("AQUAMARINE",     _("Aquamarine"),     "", 3),
        ("CITRINE",        _("Citrine"),        "", 4),
        ("CUBIC_ZIRCONIA", _("Cubic Zirconia"), "", 5),
        ("EMERALD",        _("Emerald"),        "", 6),
        ("GARNET",         _("Garnet"),         "", 7),
        ("MORGANITE",      _("Morganite"),      "", 8),
        ("PERIDOT",        _("Peridot"),        "", 9),
        ("QUARTZ",         _("Quartz"),         "", 10),
        ("RUBY",           _("Ruby"),           "", 11),
        ("SAPPHIRE",       _("Sapphire"),       "", 12),
        ("SPINEL",         _("Spinel"),         "", 13),
        ("TANZANITE",      _("Tanzanite"),      "", 14),
        ("TOPAZ",          _("Topaz"),          "", 15),
        ("TOURMALINE",     _("Tourmaline"),     "", 16),
        ("ZIRCON",         _("Zircon"),         "", 17),
    ]

    list_.sort(key=lambda x: x[1])

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
            ),
            (
                "JCASSET_PRECIOUS_RU",
                "[JewelCraft] Precious RU (ГОСТ 30649-99)",
                "Set of precious alloys according to Russian regulations",
            ),
            (
                "JCASSET_BASE",
                "[JewelCraft] Base",
                "Set of base metal alloys, physical properties taken directly from suppliers",
            ),
        ]

    folder = asset.user_asset_library_folder_weighting()

    if os.path.exists(folder):
        for entry in os.scandir(folder):
            if entry.is_file() and entry.name.endswith(".json"):
                id_ = entry.name
                name_ = os.path.splitext(entry.name)[0] + " "  # Add trailing space to deny UI translation
                list_.append((id_, name_, ""))

    if not list_:
        list_ = [("", "", "")]

    _cache["weighting_set__list"] = list_

    return list_


def weighting_materials(self, context):

    if "weighting_materials__list" in _cache:
        return _cache["weighting_materials__list"]

    props = context.scene.jewelcraft
    list_ = []

    for i, mat in enumerate(props.weighting_materials.values()):
        id_ = str(i)
        name_ = mat.name + " "  # Add trailing space to deny UI translation
        list_.append((id_, name_, ""))

    if not list_:
        list_ = [("", "", "")]

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
        _cache["asset_folders__list"] = [("", "", "")]
        return [("", "", "")]

    list_ = []

    for entry in os.scandir(folder):

        if entry.is_dir() and not entry.name.startswith("."):
            id_ = entry.name
            name_ = entry.name + " "  # Add trailing space to deny UI translation
            list_.append((id_, name_, ""))

    if not list_:
        list_ = [("", "", "")]

    _cache["asset_folders__list"] = list_

    return list_


def assets(self, context):
    category = context.window_manager.jewelcraft.asset_folder

    if "assets__list" in _cache and category == _cache.get("assets__category"):
        return _cache["assets__list"]

    _cache["assets__category"] = category
    folder = os.path.join(asset.user_asset_library_folder_object(), category)

    if not os.path.exists(folder):
        _cache["assets__list"] = [("", "", "")]
        return [("", "", "")]

    pcoll = var.preview_collections.get("assets")

    if not pcoll:
        pcoll = bpy.utils.previews.new()

    list_ = []
    i = 0
    no_preview = var.preview_collections["icons"]["NO_PREVIEW"].icon_id

    for entry in os.scandir(folder):

        if entry.is_file() and entry.name.endswith(".blend"):
            filename = os.path.splitext(entry.name)[0]
            id_ = filename
            name_ = filename + " "  # Add trailing space to deny UI translation

            preview_id = category + filename
            preview_path = os.path.splitext(entry.path)[0] + ".png"

            if os.path.exists(preview_path):
                if preview_id not in pcoll:
                    pcoll.load(preview_id, preview_path, "IMAGE")
                preview = pcoll[preview_id].icon_id
            else:
                preview = no_preview

            list_.append((id_, name_, "", preview, i))
            i += 1

    var.preview_collections["assets"] = pcoll

    if not pcoll:
        bpy.utils.previews.remove(pcoll)
        del var.preview_collections["assets"]

    if not list_:
        list_ = [("", "", "")]

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
