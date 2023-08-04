# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

def init_presets(self):

    # Defaults
    # ---------------------------

    self.detalization = 32

    self.use_handle = True
    self.handle_dim.x = self.gem_dim.x * 0.66
    self.handle_dim.y = self.gem_dim.y * 0.66
    self.handle_dim.z1 = self.gem_dim.z * 1.5
    self.handle_dim.z2 = self.gem_dim.z * 0.3

    self.girdle_dim.x = self.gem_dim.x * 0.01
    self.girdle_dim.y = self.gem_dim.y * 0.01
    self.girdle_dim.z1 = self.gem_dim.z * 0.05
    self.girdle_dim.z2 = 0.0
    self.table_z = self.gem_dim.z * 0.5

    self.use_hole = True
    self.hole_dim.x = self.gem_dim.x * 0.66
    self.hole_dim.y = self.gem_dim.y * 0.66
    self.hole_dim.z1 = self.gem_dim.z * 0.4
    self.hole_dim.z2 = self.gem_dim.z * 2
    self.hole_shift = self.handle_shift = 0.0
    self.culet_z = self.gem_dim.z * 0.8
    self.culet_size = self.gem_dim.y * 0.62

    self.use_curve_seat = False
    self.curve_seat_profile = 0.5
    self.curve_seat_segments = 15

    self.curve_profile_factor = 0.0
    self.curve_profile_segments = 10

    self.bevel_corners_width = 0.0
    self.bevel_corners_percent = 0.0
    self.bevel_corners_segments = 1
    self.bevel_corners_profile = 0.5

    # Cuts
    # ---------------------------

    if self.cut == "ROUND":
        self.hole_dim.z1 = self.gem_dim.y * 0.2

    elif self.cut == "OVAL":
        self.detalization = 64
        self.girdle_dim.z1 = self.gem_dim.z * 0.08
        self.hole_dim.z1 = self.gem_dim.z * 0.25

    elif self.cut == "CUSHION":
        self.handle_dim.z2 = self.gem_dim.z * 0.28
        self.hole_dim.z1 = self.gem_dim.z * 0.3
        self.hole_dim.y = self.gem_dim.y * 0.76
        self.use_curve_seat = True
        self.curve_seat_segments = 10
        self.bevel_corners_percent = 48.0
        self.bevel_corners_segments = 28
        self.bevel_corners_profile = 0.72

    elif self.cut == "PEAR":
        self.handle_dim.z2 = self.gem_dim.z * 0.35
        self.girdle_dim.z1 = self.gem_dim.z * 0.08
        self.hole_dim.z1 = self.gem_dim.z * 0.3
        self.hole_shift = self.handle_shift = self.gem_dim.y * 0.07
        self.mul_1 = 1.82
        self.mul_2 = 0.64
        self.detalization = 64

    elif self.cut == "MARQUISE":
        self.handle_dim.z2 = self.gem_dim.z * 0.32
        self.girdle_dim.z1 = self.gem_dim.z * 0.08
        self.hole_dim.z1 = self.gem_dim.z * 0.3
        self.mul_1 = 0.47
        self.mul_2 = 1.4
        self.detalization = 64

    elif self.cut == "PRINCESS":
        self.handle_dim.z2 = self.gem_dim.z * 0.25

    elif self.cut == "BAGUETTE":
        self.handle_dim.y = self.gem_dim.y * 0.83
        self.handle_dim.z2 = self.gem_dim.z * 0.35
        self.girdle_dim.z1 = self.gem_dim.z * 0.08
        self.hole_dim.y = self.gem_dim.y * 0.83
        self.culet_z = self.gem_dim.z * 0.7

    elif self.cut == "SQUARE":
        self.hole_dim.y = self.gem_dim.y * 0.68

    elif self.cut == "EMERALD":
        self.handle_dim.y = self.gem_dim.y * 0.75
        self.handle_dim.z2 = self.gem_dim.z * 0.25
        self.girdle_dim.z1 = self.gem_dim.z * 0.06
        self.hole_dim.y = self.gem_dim.y * 0.77
        self.culet_size = self.gem_dim.y * 0.33
        self.bevel_corners_width = self.gem_dim.y * 0.093

    elif self.cut == "ASSCHER":
        self.bevel_corners_percent = 18.0

    elif self.cut == "RADIANT":
        self.handle_dim.z2 = self.gem_dim.z * 0.25
        self.bevel_corners_percent = 15.0

    elif self.cut == "FLANDERS":
        self.handle_dim.y = self.gem_dim.y * 0.75
        self.bevel_corners_percent = 22.0

    elif self.cut == "OCTAGON":
        self.girdle_dim.z1 = self.gem_dim.z * 0.08
        self.bevel_corners_percent = 29.3

    elif self.cut == "HEART":
        self.handle_dim.z2 = self.gem_dim.z * 0.35
        self.girdle_dim.z1 = self.gem_dim.z * 0.08
        self.hole_shift = self.handle_shift = self.gem_dim.y * 0.03
        self.mul_1 = 0.54
        self.mul_2 = 0.45
        self.mul_3 = self.gem_dim.z * 0.3
        self.detalization = 64

    elif self.cut == "TRILLION":
        self.handle_dim.y = self.gem_dim.y * 0.6
        self.handle_dim.x = self.gem_dim.x * 0.6
        self.handle_dim.z2 = self.gem_dim.z * 0.28
        self.girdle_dim.z1 = self.gem_dim.z * 0.1
        self.girdle_dim.y = -self.gem_dim.y * 0.1
        self.girdle_dim.x = self.gem_dim.x * 0.005
        self.hole_dim.z1 = self.gem_dim.z * 0.28
        self.curve_profile_factor = 0.38
        self.curve_profile_segments = 30

    elif self.cut == "TRILLIANT":
        self.handle_dim.y = self.gem_dim.y * 0.8
        self.handle_dim.x = self.gem_dim.x * 0.8
        self.handle_dim.z2 = self.gem_dim.z * 0.4
        self.girdle_dim.z1 = self.gem_dim.z * 0.1
        self.girdle_dim.y = self.gem_dim.y * 0.12
        self.girdle_dim.x = self.gem_dim.x * 0.11
        self.hole_dim.z1 = self.gem_dim.z * 0.34
        self.curve_profile_factor = 0.1
        self.bevel_corners_percent = 18.0
        self.bevel_corners_segments = 10

    elif self.cut == "TRIANGLE":
        self.handle_dim.y = self.gem_dim.y * 0.6
        self.handle_dim.x = self.gem_dim.x * 0.6
        self.girdle_dim.z1 = self.gem_dim.z * 0.1
        self.hole_dim.y = self.gem_dim.y * 0.7
        self.hole_dim.x = self.gem_dim.x * 0.7
