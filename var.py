# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from pathlib import Path


preview_collections = {}


# Paths
# --------------------------------


ADDON_ID = __package__
ADDON_DIR = Path(__file__).parent
CONFIG_DIR = ADDON_DIR / ".config"

if not CONFIG_DIR.exists():
    import sys

    if sys.platform == "win32":
        CONFIG_DIR = Path.home() / "AppData" / "Roaming" / "Blender Foundation" / "Blender" / "JewelCraft"
    elif sys.platform == "darwin":
        CONFIG_DIR = Path.home() / "Library" / "Application Support" / "Blender" / "JewelCraft"
    else:
        CONFIG_DIR = Path.home() / ".config" / "blender" / "JewelCraft"

GEM_ASSET_DIR = ADDON_DIR / "assets" / "gems"
GEM_ASSET_FILEPATH = GEM_ASSET_DIR / "gems.blend"
ICONS_DIR = ADDON_DIR / "assets" / "icons"
HTML_DESIGN_REPORT_DIR = ADDON_DIR / "assets" / "templates" / "design_report"
WEIGHTING_LIB_BUILTIN_DIR = ADDON_DIR / "assets" / "weighting"

WEIGHTING_LIB_USER_DIR = CONFIG_DIR / "Weighting Library"
ASSET_LIBS_FILEPATH = CONFIG_DIR / "libraries.json"
ASSET_FAVS_FILEPATH = CONFIG_DIR / "favorites.json"
