# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import bpy


ADDON_ID = __package__
ADDON_DIR = Path(__file__).parent

ICONS_DIR = ADDON_DIR / "assets" / "icons"
GEM_ASSET_DIR = ADDON_DIR / "assets" / "gems"
GEM_ASSET_FILEPATH = GEM_ASSET_DIR / "gems.blend"
WEIGHTING_LISTS_DIR = ADDON_DIR / "assets" / "weighting"
HTML_REPORT_DIR = ADDON_DIR / "assets" / "templates" / "report_html"
ENTRIES_FILEPATH = ADDON_DIR / "assets" / "templates" / "report_entries.json"
NODES_ASSET_FILEPATH = ADDON_DIR / "assets" / "nodes_4_2.blend"


def config_dir_versioning() -> None:
    old_config_dir = Path(bpy.utils.resource_path("USER")).parent / "JewelCraft"

    if old_config_dir.exists():
        new_config_dir = Path(bpy.utils.extension_path_user(ADDON_ID))
        new_config_dir.parent.mkdir(parents=True, exist_ok=True)
        old_config_dir.rename(new_config_dir)


def config_naming_versioning() -> None:
    prefs = bpy.context.preferences.addons[ADDON_ID].preferences
    config_dir = Path(prefs.config_dir)

    paths = (
        (config_dir / "Weighting Library", config_dir / "weighting_library"),
        (config_dir / "libraries.json", config_dir / "asset_libraries.json"),
        (config_dir / "favorites.json", config_dir / "asset_favorites.json"),
    )

    for path_old, path_new in paths:
        if path_old.exists():
            path_old.rename(path_new)
