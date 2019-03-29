# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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


def convert(x, units):
    if units == "CM3_TO_MM3":
        return x / 1000
    if units == "G_TO_CT":
        return x * 5


class Scale:

    def __init__(self):
        unit = bpy.context.scene.unit_settings
        self.scale = unit.scale_length
        self.use_conversion = unit.system == "METRIC" and self.scale != 0.001

    def from_scene(self, x, volume=False, batch=False):
        if self.use_conversion:

            if batch:
                return tuple(v * 1000 * self.scale for v in x)
            if volume:
                return x * 1000 ** 3 * self.scale ** 3

            return x * 1000 * self.scale

        return x

    def to_scene(self, x, volume=False, batch=False):
        if self.use_conversion:

            if batch:
                return tuple(v / 1000 / self.scale for v in x)
            if volume:
                return x / 1000 ** 3 / self.scale ** 3

            return x / 1000 / self.scale

        return x
