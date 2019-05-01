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


import blf
import gpu
from gpu_extras.batch import batch_for_shader


shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class OnscreenText:

    def onscreen_gem_table(self, x, y, color=(0.97, 0.97, 0.97, 1.0)):
        fontid = 1
        blf.size(fontid, self.prefs.view_font_size_report, 72)
        blf.color(fontid, *color)

        _, font_h = blf.dimensions(fontid, "Row Height")
        font_baseline = font_h * 0.4
        font_row_height = font_h * 2
        box_size = font_h * 1.5
        y += font_baseline

        for row, color in self.gems_fmt:
            y -= font_row_height

            shader.bind()
            shader.uniform_float("color", color)
            batch_font = batch_for_shader(shader, "TRI_FAN", {"pos": self.rect_coords(x, y, box_size, box_size)})
            batch_font.draw(shader)

            blf.position(fontid, x + font_row_height, y + font_baseline, 0.0)
            blf.draw(fontid, row)

        return y

    def onscreen_warning(self, x, y):
        fontid = 1
        blf.size(fontid, self.prefs.view_font_size_report, 72)
        blf.color(fontid, 1.0, 0.3, 0.3, 1.0)

        _, font_h = blf.dimensions(fontid, "Row Height")
        font_row_height = font_h * 2
        y += font_h

        for row in self.warn:
            y -= font_row_height

            blf.position(fontid, x, y, 0.0)
            blf.draw(fontid, row)

        return y

    def onscreen_options(self, x, y):
        fontid = 1
        blf.size(fontid, self.prefs.view_font_size_option, 72)

        font_w_1, font_h = blf.dimensions(fontid, self.option_col_1_max)
        font_w_2, _ = blf.dimensions(fontid, self.option_col_2_max)
        font_row_height = font_h * 1.5

        for option, hotkey, value, prop_type in self.option_list:
            y -= font_row_height
            x_ofst = x

            blf.position(fontid, x, y, 0.0)
            blf.color(fontid, 0.97, 0.97, 0.97, 1.0)
            blf.draw(fontid, option)

            x_ofst += font_w_1 + 20
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, 0.7, 0.7, 0.7, 1.0)
            blf.draw(fontid, hotkey)

            if prop_type == self.TYPE_BOOL:
                x_ofst += font_w_2 + 10
                blf.position(fontid, x_ofst, y, 0.0)
                blf.color(fontid, 0.97, 0.97, 0.97, 1.0)
                blf.draw(fontid, ":")

                x_ofst += 20
                blf.position(fontid, x_ofst, y, 0.0)
                if getattr(self, value):
                    blf.color(fontid, 0.3, 1.0, 0.3, 1.0)
                    blf.draw(fontid, "ON")
                else:
                    blf.color(fontid, 1.0, 0.3, 0.3, 1.0)
                    blf.draw(fontid, "OFF")
            else:
                if getattr(self, value):
                    x_ofst += font_w_2 + 10
                    blf.position(fontid, x_ofst, y, 0.0)
                    blf.color(fontid, 0.97, 0.97, 0.97, 1.0)
                    blf.draw(fontid, ":")

                    x_ofst += 20
                    blf.position(fontid, x_ofst, y, 0.0)
                    blf.color(fontid, 0.9, 0.9, 0.0, 1.0)
                    blf.draw(fontid, "PROCESSING...")
