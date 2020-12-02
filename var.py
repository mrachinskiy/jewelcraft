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

DEFAULT_WEIGHTING_SET_DIR = os.path.join(CONFIG_DIR, "Weighting Sets")
ASSET_LIBS_FILEPATH = os.path.join(CONFIG_DIR, "libraries.json")
ASSET_FAVS_FILEPATH = os.path.join(CONFIG_DIR, "favorites.json")

HTML_DESIGN_REPORT_DIR = os.path.join(ADDON_DIR, "assets", "templates", "design_report")


# Weighting
# --------------------------------


DEFAULT_WEIGHTING_SETS = {
    "JCASSET_PRECIOUS": (
        ("Yellow Gold 24K", 19.32, "Au 99.9%"),
        ("Yellow Gold 22K", 17.86, "Au 91.6%, Ag 4.9%, Cu 3.5%"),
        ("Yellow Gold 18K", 15.53, "Au 75.3%, Ag 16.5%, Cu 6.7%, Zn 1.5%"),
        ("Yellow Gold 14K", 13.05, "Au 58.4%, Ag 9.8%, Cu 28%, Zn 3.8%"),
        ("Yellow Gold 10K", 11.47, "Au 41.7%, Ag 11.2%, Cu 40.5%, Zn 6.6%"),
        ("White Gold 18K Pd", 15.66, "Au 78.7%, Cu 8.3%, Pd 13%"),
        ("White Gold 18K Ni", 14.69, "Au 75.15%, Cu 8.75%, Ni 12%, Zn 4.1%"),
        ("White Gold 14K Pd", 14.6, "Au 58.55%, Cu 7.2%, Ag 20%, Pd 13.5%, Zn 0.75%"),
        ("White Gold 14K Ni", 12.61, "Au 58.43%, Cu 21%, Ni 12.73%, Zn 7.84%"),
        ("White Gold 10K", 10.99, "Au 41.7%, Cu 35.7%, Ni 10.3%, Zn 12.3%"),
        ("Rose Gold 18K", 15.02, "Au 75.3%, Cu 23.3%, Ag 1.2%, Zn 0.2%"),
        ("Rose Gold 14K", 13.03, "Au 58.4%, Cu 39.2%, Ag 2%, Zn 0.4%"),
        ("Rose Gold 10K", 11.52, "Au 41.5%, Cu 55%, Ag 3%, Zn 0.5%"),
        ("Platinum 950", 20.7, "Pt 95%, Ru 5%"),
        ("Platinum 900", 21.54, "Pt 90%, Ir 10%"),
        ("Palladium 950", 12.16, "Pd 95%, Ru 5%"),
        ("Silver Sterling", 10.36, "Ag 92.5%, Cu 7.5%"),
    ),
    "JCASSET_PRECIOUS_RU": (
        ("Yellow Gold 999", 19.3, "Зл 999,9"),
        ("Yellow Gold 958", 18.52, "ЗлСрМ 958-20"),
        ("Yellow Gold 750", 15.53, "ЗлСрМ 750-150"),
        ("Yellow Gold 585", 13.92, "ЗлСрМ 585-300"),
        ("Yellow Gold 375", 11.74, "ЗлСрМ 375-250"),
        ("White Gold 750 Pd", 16.44, "ЗлСрПд 750-100-150"),
        ("White Gold 750 Ni", 15.38, "ЗлСрНЦ 750-150-7,5"),
        ("White Gold 585 Pd", 14.76, "ЗлСрПд 585-255-160"),
        ("White Gold 585 Ni", 12.85, "ЗлНЦМ 585-12,5-4"),
        ("Red Gold 585", 13.24, "ЗлСрМ 585-80"),
        ("Red Gold 375", 11.54, "ЗлСрМ 375-160"),
        ("Platinum 950", 20.7, "ПлРд 950-50"),
        ("Platinum 900", 21.54, "ПлИ 900-100"),
        ("Palladium 950", 12.16, "ПдРу 950-50"),
        ("Silver 925", 10.36, "СрМ 925"),
    ),
    "JCASSET_BASE": (
        ("Brass", 8.75, "Cu 85%, Zn 15%"),
        ("Bronze", 8.8, "Cu 92%, Sn 8%"),
        ("Steel Stainless", 7.75, "Grade 420"),
        ("Titanium", 4.43, "Ti6Al4V"),
    ),
}


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
