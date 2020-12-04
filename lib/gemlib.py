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


from typing import NamedTuple, Tuple, Optional
from math import pi

from . import unit


class Stone(NamedTuple):
    name: str
    density: float
    color: Optional[Tuple[float, float, float, float]] = None


class Cut(NamedTuple):
    name: str
    shape: int
    vol_shape: int
    vol_correction: float
    xy_symmetry: bool = False


DENSITY_CORUNDUM = 4.1
DENSITY_BERYL = 2.76
DENSITY_QUARTZ = 2.65

COLOR_WHITE = (1.0, 1.0, 1.0, 1.0)
COLOR_RED = (0.57, 0.011, 0.005, 1.0)
COLOR_BLUE = (0.004, 0.019, 0.214, 1.0)

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
    "DIAMOND": Stone("Diamond", 3.53, COLOR_WHITE),
    "ALEXANDRITE": Stone("Alexandrite", 3.73, (0.153, 0.0705, 0.595, 1.0)),
    "AMETHYST": Stone("Amethyst", DENSITY_QUARTZ, (0.415, 0.041, 0.523, 1.0)),
    "AQUAMARINE": Stone("Aquamarine", DENSITY_BERYL, (0.0, 0.748, 1.0, 1.0)),
    "CITRINE": Stone("Citrine", DENSITY_QUARTZ, (1.0, 0.355, 0.0, 1.0)),
    "CUBIC_ZIRCONIA": Stone("Cubic Zirconia", 5.9, COLOR_WHITE),
    "EMERALD": Stone("Emerald", DENSITY_BERYL, (0.062, 0.748, 0.057, 1.0)),
    "GARNET": Stone("Garnet", 4.3, (0.319, 0.0, 0.0, 1.0)),
    "MORGANITE": Stone("Morganite", DENSITY_BERYL, (0.41, 0.21, 0.09, 1.0)),
    "PERIDOT": Stone("Peridot", 3.34, (0.201, 0.748, 0.026, 1.0)),
    "QUARTZ": Stone("Quartz", DENSITY_QUARTZ),
    "RUBY": Stone("Ruby", DENSITY_CORUNDUM, COLOR_RED),
    "SAPPHIRE": Stone("Sapphire", DENSITY_CORUNDUM, COLOR_BLUE),
    "SPINEL": Stone("Spinel", 3.8, COLOR_RED),
    "TANZANITE": Stone("Tanzanite", 3.38, COLOR_BLUE),
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


def ct_calc(stone: str, cut: str, size: Tuple[float, float, float]) -> float:
    try:
        dens = unit.convert_cm3_mm3(STONES[stone].density)
        _cut = CUTS[cut]
        vol_corr = _cut.vol_correction
        shape = _cut.vol_shape
    except KeyError:
        return 0

    w, l, h = size

    if shape is VOL_CONE:
        vol = pi * (l / 2) * (w / 2) * (h / 3)
    elif shape is VOL_PYRAMID:
        vol = (l * w * h) / 3
    elif shape is VOL_PRISM:
        vol = l * w * (h / 2)
    elif shape is VOL_TETRAHEDRON:
        vol = (l * w * h) / 6

    g = vol * vol_corr * dens
    ct = unit.convert_g_ct(g)

    return round(ct, 3)
