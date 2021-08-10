# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


import tempfile
from pathlib import Path

import bpy
from bpy_extras.image_utils import load_image
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix

from ..lib import asset
from . import onscreen_text
from .offscreen import draw_gems


def render_map(self, context):
    image_name = "Gem Map"
    width, height = self.get_resolution()
    padding = 30
    x = padding
    y = height - padding
    temp_filepath = Path(tempfile.gettempdir()) / "gem_map_temp.png"

    asset.render_preview(width, height, temp_filepath, compression=15, gamma=2.2)
    render_image = load_image(str(temp_filepath))

    mat_offscreen = Matrix()
    mat_offscreen[0][0] = 2 / width
    mat_offscreen[0][3] = -1
    mat_offscreen[1][1] = 2 / height
    mat_offscreen[1][3] = -1

    gpu.state.blend_set("ALPHA")

    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    shader_img = gpu.shader.from_builtin("2D_IMAGE")
    offscreen = gpu.types.GPUOffScreen(width, height)

    with offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 0.0))

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

            tex = gpu.texture.from_image(render_image)

            shader_img.bind()
            shader_img.uniform_sampler("image", tex)

            args = {
                "pos": self.rect_coords(0, 0, width, height),
                "texCoord": self.rect_coords(0, 0, 1, 1),
            }

            batch = batch_for_shader(shader_img, "TRI_FAN", args)
            batch.draw(shader_img)

            # Gem map
            # --------------------------------

            draw_gems(self, context)
            onscreen_text.onscreen_gem_table(self, x, y, color=(0.0, 0.0, 0.0))

        buffer = fb.read_color(0, 0, width, height, 4, 0, "UBYTE")
        buffer.dimensions = width * height * 4

    offscreen.free()

    if image_name not in bpy.data.images:
        bpy.data.images.new(image_name, width, height)

    image = bpy.data.images[image_name]
    image.scale(width, height)
    image.pixels = [v / 255 for v in buffer]

    if self.use_save and bpy.data.is_saved:
        image.filepath_raw = str(Path(bpy.data.filepath).with_suffix("")) + " Gem Map.png"
        image.file_format = "PNG"
        image.save()

    # Cleanup
    # ----------------------------

    bpy.data.images.remove(render_image)
    temp_filepath.unlink(missing_ok=True)

    gpu.state.blend_set("NONE")

    # Show in a new window
    # ----------------------------

    asset.show_window(width, height, space_data={"image": image})
