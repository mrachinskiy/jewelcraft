# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path


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

ICONS_DIR = ADDON_DIR / "assets" / "icons"
GEM_ASSET_DIR = ADDON_DIR / "assets" / "gems"
GEM_ASSET_FILEPATH = GEM_ASSET_DIR / "gems.blend"
NODES_ASSET_FILEPATH = ADDON_DIR / "assets" / "nodes.blend"
WEIGHTING_LIB_BUILTIN_DIR = ADDON_DIR / "assets" / "weighting"
HTML_DESIGN_REPORT_DIR = ADDON_DIR / "assets" / "templates" / "report_html"
REPORT_METADATA_BUILTIN_FILEPATH = ADDON_DIR / "assets" / "templates" / "report_metadata.json"

ASSET_LIBS_FILEPATH = CONFIG_DIR / "libraries.json"
ASSET_FAVS_FILEPATH = CONFIG_DIR / "favorites.json"
WEIGHTING_LIB_USER_DIR = CONFIG_DIR / "Weighting Library"
REPORT_METADATA_USER_FILEPATH = CONFIG_DIR / "report_metadata.json"
