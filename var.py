# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import bpy


ADDON_ID = __package__
ADDON_DIR = Path(__file__).parent
CONFIG_DIR = ADDON_DIR / ".config"

if not CONFIG_DIR.exists():
    CONFIG_DIR = Path(bpy.utils.resource_path("USER")).parent / "JewelCraft"

ICONS_DIR = ADDON_DIR / "assets" / "icons"
GEM_ASSET_DIR = ADDON_DIR / "assets" / "gems"
GEM_ASSET_FILEPATH = GEM_ASSET_DIR / "gems.blend"
WEIGHTING_LISTS_DIR = ADDON_DIR / "assets" / "weighting"
HTML_REPORT_DIR = ADDON_DIR / "assets" / "templates" / "report_html"
METADATA_FILEPATH = ADDON_DIR / "assets" / "templates" / "report_metadata.json"

if bpy.app.version >= (4, 2, 0):
    NODES_ASSET_FILEPATH = ADDON_DIR / "assets" / "nodes_4_2.blend"
else:
    NODES_ASSET_FILEPATH = ADDON_DIR / "assets" / "nodes_4_1.blend"
