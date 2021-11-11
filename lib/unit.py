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


import bpy
from mathutils import Vector


WARN_NONE = 0
WARN_SCALE = 1
WARN_SYSTEM = 2


def _eq(a: float, b: float) -> bool:
    return abs(a - b) < 1e-7


def check() -> int:
    unit = bpy.context.scene.unit_settings

    if unit.system == "METRIC" and not _eq(unit.scale_length, 0.001):
        return WARN_SCALE

    if unit.system == "IMPERIAL":
        return WARN_SYSTEM

    return WARN_NONE


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
        "from_scene_vec",
        "from_scene_vol",
        "to_scene",
        "to_scene_vec",
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

    def _from_scene(self, x: float) -> float:
        return x * 1000 * self.scale

    def _from_scene_vec(self, vec: Vector) -> tuple[float, ...]:
        return tuple(x * 1000 * self.scale for x in vec)

    def _from_scene_vol(self, x: float) -> float:
        return x * 1000 ** 3 * self.scale ** 3

    def _to_scene(self, x: float) -> float:
        return x / 1000 / self.scale

    def _to_scene_vec(self, vec: Vector) -> tuple[float, ...]:
        return tuple(x / 1000 / self.scale for x in vec)

    def _to_scene_vol(self, x: float) -> float:
        return x / 1000 ** 3 / self.scale ** 3

    @staticmethod
    def _blank(x):
        return x
