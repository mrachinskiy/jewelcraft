# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from math import radians

from mathutils import Vector

from ...lib import gemlib


def init_presets(self, gem_dim: Vector):

    # Defaults
    # ---------------------------

    self.number = 2
    self.diameter = 0.4 * gem_dim.y
    self.z1 = 0.15 * gem_dim.y
    self.z2 = 0.3 * gem_dim.y
    self.position = radians(45.0)
    self.intersection = 0.0
    self.alignment = 0.0
    self.use_symmetry = True
    self.symmetry_pivot = 0.0
    self.bump_scale = 0.5
    self.taper = 0.0
    self.detalization = 32

    # Sizes
    # ---------------------------

    if gem_dim.y >= 2.5:
        self.diameter = 0.8
    elif gem_dim.y >= 1.7:
        self.diameter = 0.7
    elif gem_dim.y >= 1.5:
        self.diameter = 0.6
    elif gem_dim.y >= 1.2:
        self.diameter = 0.5
    elif gem_dim.y >= 1.0:
        self.diameter = 0.4

    # Shapes
    # ---------------------------

    if self.shape is gemlib.SHAPE_ROUND:
        self.number = 1
        self.position = radians(60.0)

    elif self.shape is gemlib.SHAPE_TRIANGLE or self.cut == "HEART":
        self.number = 3
        self.position = radians(60.0)
        self.intersection = 0.0
        self.alignment = radians(10.0)
        self.use_symmetry = False

    elif self.shape is gemlib.SHAPE_SQUARE:
        self.intersection = -20.0

        if self.cut == "OCTAGON":
            self.intersection = 0.0

    elif self.shape is gemlib.SHAPE_RECTANGLE:
        self.number = 2
        self.position = radians(36.0)
        self.intersection = -20.0
        self.use_symmetry = True

        if self.cut == "BAGUETTE":
            self.position = radians(29.0)
            self.intersection = -10.0

    elif self.shape is gemlib.SHAPE_FANTASY:
        self.diameter = 0.28 * gem_dim.x
        self.z1 = 0.15 * gem_dim.x
        self.z2 = 0.3 * gem_dim.x

        if self.cut == "OVAL":
            self.position = radians(30.0)
            self.intersection = 40.0

        elif self.cut == "PEAR":
            self.number = 1
            self.position = radians(50.0)
            self.intersection = 40.0
            self.symmetry_pivot = radians(-90.0)

        elif self.cut == "MARQUISE":
            self.position = radians(16.0)
            self.intersection = 70.0
