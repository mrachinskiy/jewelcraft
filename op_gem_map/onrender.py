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


import os

import bpy
from bpy_extras.image_utils import load_image
import bgl
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix

from ..lib import asset


def render_map(self, context):
    import tempfile

    image_name = "Gem Map"
    width = self.width
    height = self.height
    ratio_w = width / self.region.width
    ratio_h = height / self.region.height
    padding = 30
    x = padding
    y = height - padding
    temp_filepath = os.path.join(tempfile.gettempdir(), "gem_map_temp.png")

    asset.render_preview(width, height, temp_filepath, compression=15, gamma=2.2)
    render_image = load_image(temp_filepath)
    render_image.gl_load()

    mat_offscreen = Matrix()
    mat_offscreen[0][0] = 2 / width
    mat_offscreen[0][3] = -1
    mat_offscreen[1][1] = 2 / height
    mat_offscreen[1][3] = -1

    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    shader_img = gpu.shader.from_builtin("2D_IMAGE")
    offscreen = gpu.types.GPUOffScreen(width, height)

    with offscreen.bind():
        bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)

        with gpu.matrix.push_pop():
            gpu.matrix.load_matrix(mat_offscreen)
            gpu.matrix.load_projection_matrix(Matrix())

            # Background
            # --------------------------------

            shader.bind()
            shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
            batch = batch_for_shader(shader, "TRI_FAN", {"pos": self.rect_coords(0, 0, width, height)})
            batch.draw(shader)

            # Render result
            # --------------------------------

            bgl.glEnable(bgl.GL_BLEND)

            bgl.glActiveTexture(bgl.GL_TEXTURE0)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, render_image.bindcode)

            shader_img.bind()
            shader_img.uniform_int("image", 0)

            args = {
                "pos": self.rect_coords(0, 0, width, height),
                "texCoord": self.rect_coords(0, 0, 1, 1),
            }

            batch = batch_for_shader(shader_img, "TRI_FAN", args)
            batch.draw(shader_img)

            # Gem map
            # --------------------------------

            self.draw_gems(context, ratio_w=ratio_w, ratio_h=ratio_h)
            self.onscreen_gem_table(x, y, color=(0.0, 0.0, 0.0, 1.0))

        buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 4)
        bgl.glReadBuffer(bgl.GL_BACK)
        bgl.glReadPixels(0, 0, width, height, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)

    offscreen.free()

    if image_name not in bpy.data.images:
        bpy.data.images.new(image_name, width, height)

    image = bpy.data.images[image_name]
    image.scale(width, height)
    image.pixels = [v / 255 for v in buffer]

    if self.use_save and bpy.data.is_saved:
        filepath = bpy.data.filepath
        filename = os.path.splitext(os.path.basename(filepath))[0]
        save_path = os.path.join(os.path.dirname(filepath), filename + " Gem Map.png")

        image.filepath_raw = save_path
        image.file_format = "PNG"
        image.save()

    render_image.gl_free()
    bpy.data.images.remove(render_image)

    if os.path.exists(temp_filepath):
        os.remove(temp_filepath)

    # Restore OpenGL defaults
    # ----------------------------

    bgl.glDisable(bgl.GL_BLEND)

    # Show in a new window
    # ----------------------------

    asset.show_window(width, height, space_data={"image": image})
