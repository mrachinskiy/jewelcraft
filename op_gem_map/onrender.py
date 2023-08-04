# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import tempfile
from pathlib import Path

import bpy
from bpy_extras.image_utils import load_image
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Color

from ..lib import asset
from . import onscreen_text
from .offscreen import draw_gems


def srgb_to_linear(color) -> Color:
    return Color(x ** (1.0 / 2.2) for x in color)  # NOTE T74139


def _text_color(use_background: bool) -> tuple[float, float, float]:
    if use_background:
        shading = bpy.context.space_data.shading

        if shading.background_type == "THEME":
            gradients = bpy.context.preferences.themes[0].view_3d.space.gradients

            if gradients.background_type == "RADIAL":
                bgc = gradients.gradient
            else:
                bgc = gradients.high_gradient

        elif shading.background_type == "WORLD":
            bgc = srgb_to_linear(bpy.context.scene.world.color)
        elif shading.background_type == "VIEWPORT":
            bgc = srgb_to_linear(shading.background_color)

        if bgc.v < 0.5:
            return (1.0, 1.0, 1.0)

    return (0.0, 0.0, 0.0)


def render_map(self):
    image_name = "Gem Map"
    temp_filepath = Path(tempfile.gettempdir()) / "gem_map_temp.png"

    width, height = self.get_resolution()
    padding = 30
    x = padding
    y = height - padding

    asset.render_preview(width, height, temp_filepath, compression=15, gamma=2.2, use_transparent=not self.use_background)
    render_image = load_image(str(temp_filepath))

    mat_offscreen = Matrix()
    mat_offscreen[0][0] = 2 / width
    mat_offscreen[0][3] = -1
    mat_offscreen[1][1] = 2 / height
    mat_offscreen[1][3] = -1

    gpu.state.blend_set("ALPHA")

    shader = gpu.shader.from_builtin("IMAGE")
    offscreen = gpu.types.GPUOffScreen(width, height)

    with offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(1.0, 1.0, 1.0, 1.0))

        with gpu.matrix.push_pop():
            gpu.matrix.load_matrix(mat_offscreen)
            gpu.matrix.load_projection_matrix(Matrix())

            # Render result
            # --------------------------------

            tex = gpu.texture.from_image(render_image)

            shader.bind()
            shader.uniform_sampler("image", tex)

            args = {
                "pos": ((0, 0), (width, 0), (width, height), (0, height)),
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            }
            indices = ((0, 1, 2), (0, 2, 3))

            batch = batch_for_shader(shader, "TRIS", args, indices=indices)
            batch.draw(shader)

            # Gem map
            # --------------------------------

            draw_gems(self)
            onscreen_text.onscreen_gem_table(self, x, y, color=_text_color(self.use_background))

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
