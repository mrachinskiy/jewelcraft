# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2022  Mikhail Rachinskiy
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


import gpu
from gpu_extras.presets import draw_texture_2d

from ..lib import view3d_lib
from . import onscreen_text


def draw(self, context):
    width = self.region.width
    height = self.region.height
    x = self.view_padding_left
    y = self.view_padding_top

    # Gem map
    # -----------------------------

    if not self.use_navigate:
        gpu.state.blend_set("ALPHA")
        draw_texture_2d(self.offscreen.texture_color, (0, 0), width, height)

    # Onscreen text
    # -----------------------------

    y = onscreen_text.onscreen_gem_table(self, x, y)
    y -= self.view_margin

    if self.show_warn:
        y = onscreen_text.onscreen_warning(self, x, y)
        y -= self.view_margin

    view3d_lib.options_display(self, context, x, y)

    # Reset state
    # ----------------------------

    gpu.state.blend_set("NONE")
