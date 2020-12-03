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

import bpy


preview_collections = {}


# Paths
# --------------------------------


ADDON_ID = __package__
ADDON_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(ADDON_DIR, ".config")

if not os.path.exists(CONFIG_DIR):
    import sys

    if sys.platform == "win32":
        CONFIG_DIR = os.path.join(os.getenv("APPDATA"), "Blender Foundation", "Blender", "JewelCraft")
    elif sys.platform == "darwin":
        CONFIG_DIR = os.path.join(os.path.expanduser("~/Library/Application Support"), "Blender", "JewelCraft")
    else:
        CONFIG_DIR = os.path.join(os.path.expanduser("~/.config"), "blender", "JewelCraft")

ICONS_DIR = os.path.join(ADDON_DIR, "assets", "icons")
GEM_ASSET_DIR = os.path.join(ADDON_DIR, "assets", "gems")
GEM_ASSET_FILEPATH = os.path.join(GEM_ASSET_DIR, "gems.blend")
HTML_DESIGN_REPORT_DIR = os.path.join(ADDON_DIR, "assets", "templates", "design_report")
WEIGHTING_SET_DIR = os.path.join(ADDON_DIR, "assets", "weighting")

DEFAULT_WEIGHTING_SET_DIR = os.path.join(CONFIG_DIR, "Weighting Sets")
ASSET_LIBS_FILEPATH = os.path.join(CONFIG_DIR, "libraries.json")
ASSET_FAVS_FILEPATH = os.path.join(CONFIG_DIR, "favorites.json")


# Ring Size
# --------------------------------


CIR_BASE_US = 36.537
CIR_STEP_US = 2.5535
CIR_BASE_UK = 37.5
CIR_STEP_UK = 1.25
MAP_SIZE_JP_TO_US = (1, 2, 2.5, 3, 3.25, 3.75, 4, 4.5, 5, 5.5, 6, 6.25, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.25, 10.5, 11, 11.5, 12, 12.5, 13)


# Versioning
# --------------------------------


USE_POLYLINE = bpy.app.version >= (2, 92, 0)
