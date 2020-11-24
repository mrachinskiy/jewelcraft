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


from typing import Union, Tuple


WARN_SCALE = 1
WARN_SYSTEM = 2


def check(context) -> Union[int, bool]:
    unit = context.scene.unit_settings

    if unit.system == "METRIC" and round(unit.scale_length, 4) != 0.001:
        return WARN_SCALE

    if unit.system == "IMPERIAL":
        return WARN_SYSTEM

    return False


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
    __slots__ = ("scale", "from_scene", "to_scene")

    def __init__(self, context) -> None:
        unit = context.scene.unit_settings
        self.scale = round(unit.scale_length, 4)

        if unit.system == "METRIC" and self.scale != 0.001:
            self.from_scene = self._from_scene
            self.to_scene = self._to_scene
        else:
            self.from_scene = self._blank
            self.to_scene = self._blank

    def _from_scene(self, x: float, volume: bool = False, batch: bool = False) -> Union[float, Tuple[float, ...]]:
        if volume:
            return x * 1000 ** 3 * self.scale ** 3
        if batch:
            return tuple(v * 1000 * self.scale for v in x)

        return x * 1000 * self.scale

    def _to_scene(self, x: float, volume: bool = False, batch: bool = False) -> Union[float, Tuple[float, ...]]:
        if volume:
            return x / 1000 ** 3 / self.scale ** 3
        if batch:
            return tuple(v / 1000 / self.scale for v in x)

        return x / 1000 / self.scale

    @staticmethod
    def _blank(x, y=False, z=False):
        return x
