# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from mathutils import Vector


WARN_SCALE = 1
WARN_SYSTEM = 2


def _eq(a: float, b: float) -> bool:
    return abs(a - b) < 1e-7


def check() -> int | None:
    unit = bpy.context.scene.unit_settings

    if unit.system == "METRIC" and not _eq(unit.scale_length, 0.001):
        return WARN_SCALE

    if unit.system == "IMPERIAL":
        return WARN_SYSTEM


def convert_cm3_mm3(x: float) -> float:
    return x / 1000


def convert_g_ct(x: float) -> float:
    return x * 5


def convert_ct_mm(x: float) -> float:
    """Round diamonds only"""
    return round(x ** (1 / 3) / 0.00365 ** (1 / 3), 2)


def convert_mm_ct(x: float) -> float:
    """Round diamonds only"""
    return round(x ** 3 * 0.00365, 3)


class Scale:
    __slots__ = (
        "scale",
        "from_scene",
        "from_scene_vol",
        "to_scene",
        "to_scene_vol",
    )

    def __init__(self) -> None:
        unit = bpy.context.scene.unit_settings

        if unit.system == "METRIC" and not _eq(unit.scale_length, 0.001):
            self.scale = round(unit.scale_length, 7)
            for prop in self.__slots__[1:]:
                setattr(self, prop, getattr(self, f"_{prop}"))
            return

        for prop in self.__slots__[1:]:
            setattr(self, prop, self._blank)

    def _from_scene(self, x: float | Vector) -> float | Vector:
        return x * 1000 * self.scale

    def _from_scene_vol(self, x: float) -> float:
        return x * 1000 ** 3 * self.scale ** 3

    def _to_scene(self, x: float | Vector) -> float | Vector:
        return x / 1000 / self.scale

    def _to_scene_vol(self, x: float) -> float:
        return x / 1000 ** 3 / self.scale ** 3

    @staticmethod
    def _blank(x):
        return x
