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
WEIGHTING_LIB_BUILTIN_DIR = os.path.join(ADDON_DIR, "assets", "weighting")

WEIGHTING_LIB_USER_DIR = os.path.join(CONFIG_DIR, "Weighting Library")
WEIGHTING_LIB_USER_DIR_LEGACY = os.path.join(CONFIG_DIR, "Weighting Sets")  # TODO remove
ASSET_LIBS_FILEPATH = os.path.join(CONFIG_DIR, "libraries.json")
ASSET_FAVS_FILEPATH = os.path.join(CONFIG_DIR, "favorites.json")


# Versioning
# --------------------------------


USE_POLYLINE = bpy.app.version >= (2, 92, 0)
