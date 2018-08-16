# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
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


def init_presets(self):

    # Defaults
    # ---------------------------

    self.detalization = 32

    self.girdle_l_ofst = 0.01
    self.girdle_w_ofst = 0.01

    self.mul_1 = 0.47
    self.mul_2 = 1.4

    self.handle = True
    self.handle_l_size = self.gem_l * 0.66
    self.handle_w_size = self.gem_w * 0.66
    self.handle_z_top = self.gem_h * 1.5
    self.handle_z_btm = self.gem_h * 0.3

    self.table_z = self.gem_h * 0.5
    self.girdle_z_top = self.gem_h * 0.05
    self.girdle_z_btm = 0.0

    self.hole = True
    self.culet_z = self.gem_h * 0.8
    self.hole_z_top = self.gem_h * 0.4
    self.hole_z_btm = self.gem_h * 2
    self.hole_l_size = self.gem_l * 0.66
    self.hole_w_size = self.gem_w * 0.66

    self.hole_pos_ofst = 0.0

    self.curve_seat = False
    self.curve_seat_segments = 15
    self.curve_seat_profile = 0.5

    self.curve_profile = False
    self.curve_profile_segments = 10
    self.curve_profile_factor = 0.1

    self.bevel_corners = False
    self.bevel_corners_width = 0.1
    self.bevel_corners_percent = 18.0
    self.bevel_corners_segments = 1
    self.bevel_corners_profile = 0.5

    # Cuts
    # ---------------------------

    if self.cut == "ROUND":
        self.hole_z_top = self.gem_l * 0.2

    elif self.cut == "OVAL":
        self.detalization = 64
        self.girdle_z_top = self.gem_h * 0.08
        self.hole_z_top = self.gem_h * 0.25

    elif self.cut == "CUSHION":
        self.handle_z_btm = self.gem_h * 0.28
        self.hole_z_top = self.gem_h * 0.3
        self.hole_l_size = self.gem_l * 0.76
        self.curve_seat = True
        self.curve_seat_segments = 10
        self.bevel_corners = True
        self.bevel_corners_percent = 48.0
        self.bevel_corners_segments = 28
        self.bevel_corners_profile = 0.72

    elif self.cut == "PEAR":
        self.handle_z_btm = self.gem_h * 0.35
        self.girdle_z_top = self.gem_h * 0.08
        self.hole_z_top = self.gem_h * 0.3
        self.hole_pos_ofst = self.gem_l * 0.07

    elif self.cut == "MARQUISE":
        self.detalization = 64
        self.handle_z_btm = self.gem_h * 0.32
        self.girdle_z_top = self.gem_h * 0.08
        self.hole_z_top = self.gem_h * 0.3

    elif self.cut == "PRINCESS":
        self.handle_z_btm = self.gem_h * 0.25

    elif self.cut == "BAGUETTE":
        self.handle_l_size = self.gem_l * 0.83
        self.handle_z_btm = self.gem_h * 0.35
        self.girdle_z_top = self.gem_h * 0.08
        self.hole_l_size = self.gem_l * 0.83

    elif self.cut == "SQUARE":
        self.hole_l_size = self.gem_l * 0.68

    elif self.cut == "EMERALD":
        self.handle_l_size = self.gem_l * 0.75
        self.handle_z_btm = self.gem_h * 0.25
        self.girdle_z_top = self.gem_h * 0.06
        self.hole_l_size = self.gem_l * 0.77
        self.bevel_corners = True
        self.bevel_corners_width = self.gem_l * 0.093

    elif self.cut == "ASSCHER":
        self.bevel_corners = True

    elif self.cut == "RADIANT":
        self.handle_z_btm = self.gem_h * 0.25
        self.bevel_corners = True
        self.bevel_corners_percent = 15.0

    elif self.cut == "FLANDERS":
        self.handle_l_size = self.gem_l * 0.75
        self.bevel_corners = True
        self.bevel_corners_percent = 22.0

    elif self.cut == "OCTAGON":
        self.girdle_z_top = self.gem_h * 0.08
        self.bevel_corners = True
        self.bevel_corners_percent = 29.3

    elif self.cut == "HEART":
        self.girdle_z_top = self.gem_h * 0.08
        self.handle_z_btm = self.gem_h * 0.35
        self.hole_pos_ofst = self.gem_l * 0.03

    elif self.cut == "TRILLION":
        self.handle_l_size = self.gem_l * 0.6
        self.handle_w_size = self.gem_w * 0.6
        self.handle_z_btm = self.gem_h * 0.28
        self.girdle_z_top = self.gem_h * 0.1
        self.girdle_l_ofst = -self.gem_l * 0.1
        self.girdle_w_ofst = self.gem_w * 0.005
        self.hole_z_top = self.gem_h * 0.28
        self.curve_profile = True
        self.curve_profile_factor = 0.38

    elif self.cut == "TRILLIANT":
        self.handle_l_size = self.gem_l * 0.8
        self.handle_w_size = self.gem_w * 0.8
        self.handle_z_btm = self.gem_h * 0.4
        self.girdle_z_top = self.gem_h * 0.1
        self.girdle_l_ofst = self.gem_l * 0.12
        self.girdle_w_ofst = self.gem_w * 0.11
        self.hole_z_top = self.gem_h * 0.34
        self.curve_profile = True
        self.bevel_corners = True
        self.bevel_corners_segments = 10

    elif self.cut == "TRIANGLE":
        self.handle_l_size = self.gem_l * 0.6
        self.handle_w_size = self.gem_w * 0.6
        self.girdle_z_top = self.gem_h * 0.1
        self.hole_l_size = self.gem_l * 0.7
        self.hole_w_size = self.gem_w * 0.7
