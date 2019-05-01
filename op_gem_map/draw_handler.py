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


import bgl
import gpu
from gpu_extras.batch import batch_for_shader


shader_img = gpu.shader.from_builtin("2D_IMAGE")


def draw(self, context):
    width = self.region.width
    height = self.region.height
    x = self.view_padding_left
    y = height - self.view_padding_top

    # Gem map
    # -----------------------------

    if not self.use_navigate:
        bgl.glEnable(bgl.GL_BLEND)

        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.offscreen.color_texture)

        shader_img.bind()
        shader_img.uniform_int("image", 0)

        args = {
            "pos": self.rect_coords(0, 0, width, height),
            "texCoord": self.rect_coords(0, 0, 1, 1),
        }

        batch = batch_for_shader(shader_img, "TRI_FAN", args)
        batch.draw(shader_img)

    # Onscreen text
    # -----------------------------

    y = self.onscreen_gem_table(x, y)
    y -= self.view_margin

    if self.show_warn:
        y = self.onscreen_warning(x, y)
        y -= self.view_margin

    self.onscreen_options(x, y)

    # Restore OpenGL defaults
    # ----------------------------

    bgl.glDisable(bgl.GL_BLEND)
