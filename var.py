# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


from pathlib import Path

import bpy


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
