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


from math import radians


def init_presets(self):

    # Defaults
    # ---------------------------

    self.number = 4
    self.diameter = 0.4 * self.gem_l
    self.z_top = 0.3 * self.gem_l
    self.z_btm = 0.5 * self.gem_l
    self.position = radians(45.0)
    self.intersection = 30.0
    self.alignment = 0.0
    self.use_symmetry = False
    self.symmetry_pivot = 0.0
    self.bump_scale = 0.5
    self.taper = 0.0
    self.detalization = 32

    # Sizes
    # ---------------------------

    if self.gem_l >= 2.5:
        self.diameter = 0.8
        self.z_top = 0.8
        self.z_btm = 1.2

    elif self.gem_l >= 1.7:
        self.diameter = 0.7
        self.z_top = 0.6
        self.z_btm = 0.9

    elif self.gem_l >= 1.5:
        self.diameter = 0.6
        self.z_top = 0.5
        self.z_btm = 0.7

    elif self.gem_l >= 1.2:
        self.diameter = 0.5
        self.z_top = 0.4
        self.z_btm = 0.6

    elif self.gem_l >= 1.0:
        self.diameter = 0.4
        self.z_top = 0.3
        self.z_btm = 0.5

    # Shapes
    # ---------------------------

    if self.shape_rnd:
        self.number = 2
        self.position = radians(-30.0)
        self.intersection = 30.0

        if self.cut == "OVAL":
            self.position = radians(30.0)
            self.intersection = 40.0
            self.use_symmetry = True

    elif self.shape_tri:
        self.number = 3
        self.position = radians(60.0)
        self.intersection = 0.0
        self.alignment = radians(10.0)

    elif self.shape_sq:
        self.intersection = -20.0

        if self.cut == "OCTAGON":
            self.intersection = 0.0

    elif self.shape_rect:
        self.number = 2
        self.position = radians(36.0)
        self.intersection = -20.0
        self.use_symmetry = True

        if self.cut == "BAGUETTE":
            self.position = radians(29.0)
            self.intersection = -10.0

    elif self.shape_fant:
        self.number = 2
        self.position = radians(0.0)
        self.intersection = 0.0
        self.alignment = radians(10.0)

        if self.cut == "HEART":
            self.number = 3
            self.position = radians(60.0)
            self.intersection = -10.0

        elif self.cut == "PEAR":
            self.number = 1
            self.position = radians(50.0)
            self.intersection = 40.0
            self.use_symmetry = True
            self.symmetry_pivot = radians(-90.0)
