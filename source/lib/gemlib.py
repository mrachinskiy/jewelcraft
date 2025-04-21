# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from math import pi
from typing import NamedTuple

from . import unit


class Stone(NamedTuple):
    name: str
    density: float
    color: str


class Cut(NamedTuple):
    name: str
    shape: int
    vol_shape: int
    vol_correction: float
    trait: int = 0


DENSITY_CORUNDUM = 4.1
DENSITY_BERYL = 2.76
DENSITY_QUARTZ = 2.65

SHAPE_ROUND = 1
SHAPE_SQUARE = 2
SHAPE_RECTANGLE = 3
SHAPE_TRIANGLE = 4
SHAPE_FANTASY = 5

VOL_CONE = 1
VOL_PYRAMID = 2
VOL_PRISM = 3
VOL_TETRAHEDRON = 4

TRAIT_XY_SYMMETRY = 1
TRAIT_X_SIZE = 2

STONES = {
    "DIAMOND": Stone("Diamond", 3.53, "Colorless"),
    "ALEXANDRITE": Stone("Alexandrite", 3.73, "Reddish Purple"),
    "AMETHYST": Stone("Amethyst", DENSITY_QUARTZ, "Purple"),
    "AQUAMARINE": Stone("Aquamarine", DENSITY_BERYL, "Greenish Blue"),
    "CITRINE": Stone("Citrine", DENSITY_QUARTZ, "Yellow"),
    "CUBIC_ZIRCONIA": Stone("Cubic Zirconia", 5.9, "Colorless"),
    "EMERALD": Stone("Emerald", DENSITY_BERYL, "Green"),
    "GARNET": Stone("Garnet", 4.3, "Red"),
    "MORGANITE": Stone("Morganite", DENSITY_BERYL, "Pink"),
    "PERIDOT": Stone("Peridot", 3.34, "Yellowish Green"),
    "QUARTZ": Stone("Quartz", DENSITY_QUARTZ, "Pink"),
    "RUBY": Stone("Ruby", DENSITY_CORUNDUM, "Red"),
    "SAPPHIRE": Stone("Sapphire", DENSITY_CORUNDUM, "Blue"),
    "SPINEL": Stone("Spinel", 3.8, "Reddish Purple"),
    "TANZANITE": Stone("Tanzanite", 3.38, "Violetish Blue"),
    "TOPAZ": Stone("Topaz", 3.57, "Greenish Blue"),
    "TOURMALINE": Stone("Tourmaline", 3.22, "Bluish Green"),
    "ZIRCON": Stone("Zircon", 4.73, "Greenish Blue"),
}

CUTS = {
    "ROUND": Cut("Round", SHAPE_ROUND, VOL_CONE, 1.3056, TRAIT_XY_SYMMETRY),
    "OVAL": Cut("Oval", SHAPE_FANTASY, VOL_CONE, 1.34455),
    "CUSHION": Cut("Cushion", SHAPE_SQUARE, VOL_PYRAMID, 1.2852),
    "PEAR": Cut("Pear", SHAPE_FANTASY, VOL_CONE, 1.24936),
    "MARQUISE": Cut("Marquise", SHAPE_FANTASY, VOL_CONE, 1.20412),
    "PRINCESS": Cut("Princess", SHAPE_SQUARE, VOL_PYRAMID, 1.43301),
    "BAGUETTE": Cut("Baguette", SHAPE_RECTANGLE, VOL_PRISM, 1.197),
    "SQUARE": Cut("Square", SHAPE_SQUARE, VOL_PYRAMID, 1.6, TRAIT_XY_SYMMETRY),
    "EMERALD": Cut("Emerald", SHAPE_RECTANGLE, VOL_PRISM, 1.025),
    "ASSCHER": Cut("Asscher", SHAPE_SQUARE, VOL_PYRAMID, 1.379, TRAIT_XY_SYMMETRY),
    "RADIANT": Cut("Radiant", SHAPE_SQUARE, VOL_PYRAMID, 1.3494),
    "FLANDERS": Cut("Flanders", SHAPE_SQUARE, VOL_PYRAMID, 1.2407, TRAIT_XY_SYMMETRY),
    "OCTAGON": Cut("Octagon", SHAPE_SQUARE, VOL_CONE, 1.479, TRAIT_XY_SYMMETRY),
    "HEART": Cut("Heart", SHAPE_FANTASY, VOL_CONE, 1.29, TRAIT_X_SIZE),
    "TRILLION": Cut("Trillion", SHAPE_TRIANGLE, VOL_TETRAHEDRON, 1.644, TRAIT_X_SIZE),
    "TRILLIANT": Cut("Trilliant", SHAPE_TRIANGLE, VOL_TETRAHEDRON, 1.888, TRAIT_X_SIZE),
    "TRIANGLE": Cut("Triangle", SHAPE_TRIANGLE, VOL_TETRAHEDRON, 1.531),
}


def ct_calc(stone: str, cut: str, size: tuple[float, float, float]) -> float:
    try:
        dens = unit.convert_cm3_mm3(STONES[stone].density)
        _cut = CUTS[cut]
        vol_corr = _cut.vol_correction
        shape = _cut.vol_shape
    except KeyError:
        return 0

    a, b, h = size

    if shape is VOL_CONE:
        vol = pi * (a / 2) * (b / 2) * (h / 3)
    elif shape is VOL_PYRAMID:
        vol = (a * b * h) / 3
    elif shape is VOL_TETRAHEDRON:
        vol = (a * b * h) / 6
    elif shape is VOL_PRISM:
        vol = a * b * (h / 2)

    g = vol * vol_corr * dens
    ct = unit.convert_g_ct(g)

    return round(ct, 3)
