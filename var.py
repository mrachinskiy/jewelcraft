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
import sys
import collections


preview_collections = {}


# Paths
# --------------------------------


ADDON_ID = __package__
ADDON_DIR = os.path.dirname(__file__)

ICONS_DIR = os.path.join(ADDON_DIR, "assets", "icons")
GEM_ASSET_DIR = os.path.join(ADDON_DIR, "assets", "gems")
GEM_ASSET_FILEPATH = os.path.join(GEM_ASSET_DIR, "gems.blend")

if sys.platform == "win32":
    LOCAL_PATH = os.getenv("LOCALAPPDATA")
elif sys.platform == "darwin":
    LOCAL_PATH = os.path.expanduser("~/Library/Application Support")
else:
    LOCAL_PATH = os.path.expanduser("~/.local/share")

ADDON_CONFIG_DIR = os.path.join(LOCAL_PATH, "Blender", "JewelCraft")
USER_ASSET_DIR = os.path.join(ADDON_CONFIG_DIR, "Asset Library")
USER_ASSET_OBJECT_DIR = os.path.join(USER_ASSET_DIR, "Object")
USER_ASSET_WEIGHTING_DIR = os.path.join(USER_ASSET_DIR, "Weighting")


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


# Gems
# --------------------------------


Stone = collections.namedtuple("Stone", ("name", "density", "color"), defaults=(None,))
Cut = collections.namedtuple("Cut", ("name", "shape", "vol_shape", "vol_correction", "xy_symmetry"), defaults=(False,))

CORUNDUM = 4.1
BERYL = 2.76
QUARTZ = 2.65

WHITE = (1.0, 1.0, 1.0, 1.0)
RED = (0.57, 0.011, 0.005, 1.0)
BLUE = (0.004, 0.019, 0.214, 1.0)

SHAPE_ROUND = 0
SHAPE_SQUARE = 1
SHAPE_RECTANGLE = 2
SHAPE_TRIANGLE = 3
SHAPE_FANTASY = 4

VOL_CONE = 0
VOL_PYRAMID = 1
VOL_PRISM = 2
VOL_TETRAHEDRON = 3

STONES = {
    "DIAMOND": Stone("Diamond", 3.53, WHITE),
    "ALEXANDRITE": Stone("Alexandrite", 3.73, (0.153, 0.0705, 0.595, 1.0)),
    "AMETHYST": Stone("Amethyst", QUARTZ, (0.415, 0.041, 0.523, 1.0)),
    "AQUAMARINE": Stone("Aquamarine", BERYL, (0.0, 0.748, 1.0, 1.0)),
    "CITRINE": Stone("Citrine", QUARTZ, (1.0, 0.355, 0.0, 1.0)),
    "CUBIC_ZIRCONIA": Stone("Cubic Zirconia", 5.9, WHITE),
    "EMERALD": Stone("Emerald", BERYL, (0.062, 0.748, 0.057, 1.0)),
    "GARNET": Stone("Garnet", 4.3, (0.319, 0.0, 0.0, 1.0)),
    "MORGANITE": Stone("Morganite", BERYL, (0.41, 0.21, 0.09, 1.0)),
    "PERIDOT": Stone("Peridot", 3.34, (0.201, 0.748, 0.026, 1.0)),
    "QUARTZ": Stone("Quartz", QUARTZ),
    "RUBY": Stone("Ruby", CORUNDUM, RED),
    "SAPPHIRE": Stone("Sapphire", CORUNDUM, BLUE),
    "SPINEL": Stone("Spinel", 3.8, RED),
    "TANZANITE": Stone("Tanzanite", 3.38, BLUE),
    "TOPAZ": Stone("Topaz", 3.57),
    "TOURMALINE": Stone("Tourmaline", 3.22),
    "ZIRCON": Stone("Zircon", 4.73),
}

CUTS = {
    "ROUND": Cut("Round", SHAPE_ROUND, VOL_CONE, 1.3056, True),
    "OVAL": Cut("Oval", SHAPE_FANTASY, VOL_CONE, 1.34455),
    "CUSHION": Cut("Cushion", SHAPE_SQUARE, VOL_PYRAMID, 1.2852),
    "PEAR": Cut("Pear", SHAPE_FANTASY, VOL_CONE, 1.24936),
    "MARQUISE": Cut("Marquise", SHAPE_FANTASY, VOL_CONE, 1.20412),
    "PRINCESS": Cut("Princess", SHAPE_SQUARE, VOL_PYRAMID, 1.43301),
    "BAGUETTE": Cut("Baguette", SHAPE_RECTANGLE, VOL_PRISM, 1.197),
    "SQUARE": Cut("Square", SHAPE_SQUARE, VOL_PYRAMID, 1.6, True),
    "EMERALD": Cut("Emerald", SHAPE_RECTANGLE, VOL_PRISM, 1.025),
    "ASSCHER": Cut("Asscher", SHAPE_SQUARE, VOL_PYRAMID, 1.379, True),
    "RADIANT": Cut("Radiant", SHAPE_SQUARE, VOL_PYRAMID, 1.3494),
    "FLANDERS": Cut("Flanders", SHAPE_SQUARE, VOL_PYRAMID, 1.2407, True),
    "OCTAGON": Cut("Octagon", SHAPE_SQUARE, VOL_CONE, 1.479, True),
    "HEART": Cut("Heart", SHAPE_FANTASY, VOL_CONE, 1.29),
    "TRILLION": Cut("Trillion", SHAPE_TRIANGLE, VOL_TETRAHEDRON, 1.644),
    "TRILLIANT": Cut("Trilliant", SHAPE_TRIANGLE, VOL_TETRAHEDRON, 1.888),
    "TRIANGLE": Cut("Triangle", SHAPE_TRIANGLE, VOL_TETRAHEDRON, 1.531),
}


# Ring Size
# --------------------------------


CIR_BASE_US = 36.537
CIR_STEP_US = 2.5535
CIR_BASE_UK = 37.5
CIR_STEP_UK = 1.25
MAP_SIZE_JP_TO_US = (1, 2, 2.5, 3, 3.25, 3.75, 4, 4.5, 5, 5.5, 6, 6.25, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.25, 10.5, 11, 11.5, 12, 12.5, 13)


# mod_update
# --------------------------------


UPDATE_OPERATOR_ID_AFFIX = "jewelcraft"
UPDATE_SAVE_STATE_FILEPATH = os.path.join(ADDON_CONFIG_DIR, "update_state.json")
UPDATE_URL_RELEASES = "https://api.github.com/repos/mrachinskiy/jewelcraft/releases"
UPDATE_VERSION_CURRENT = None
UPDATE_VERSION_MAX = None

update_available = False
