# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
from pathlib import Path

import bpy
import gpu
from bpy_extras.image_utils import load_image
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix

from ...lib import asset, colorlib, overlays
from ..gem_map import onscreen


def _get_resolution(region, region_3d, render) -> tuple[int, int]:
    resolution_scale = render.resolution_percentage / 100

    if region_3d.view_perspective == "CAMERA":
        return round(render.resolution_x * resolution_scale), round(render.resolution_y * resolution_scale)
    return round(region.width * resolution_scale), round(region.height * resolution_scale)


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
            bgc = [colorlib.linear_to_srgb(x) for x in bpy.context.scene.world.color]

        elif shading.background_type == "VIEWPORT":
            bgc = [colorlib.linear_to_srgb(x) for x in shading.background_color]

        if colorlib.luma(bgc) < 0.4:
            return (1.0, 1.0, 1.0)

    return (0.0, 0.0, 0.0)


def render_map(self) -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        _render_map(self, tempdir)


def _render_map(self, tempdir: str) -> None:
    image_name = "Gem Map 2"

    render = bpy.context.scene.render
    width, height = _get_resolution(self.region, self.region_3d, render)
    padding = 30
    x = padding
    y = height - padding

    render_filepath = Path(tempdir) / "gem_map_2_temp.png"

    asset.render_preview(width, height, render_filepath, compression=15, gamma=2.2, use_transparent=not self.use_background)
    render_image = load_image(str(render_filepath))

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

        if self.region_3d.view_perspective == "CAMERA":
            view_matrix = bpy.context.scene.camera.matrix_world.inverted()
            projection_matrix = bpy.context.scene.camera.calc_matrix_camera(
                bpy.context.evaluated_depsgraph_get(), x=width, y=height
            )
        else:
            view_matrix = self.region_3d.view_matrix
            projection_matrix = self.region_3d.window_matrix

        overlays.gem_map_2._draw(
            self,
            bpy.context,
            is_overlay=False,
            use_select=self.use_select,
            use_mat_color=self.use_mat_color,
            view_matrix_override=view_matrix,
            projection_matrix_override=projection_matrix,
            viewport_size_override=(width, height),
        )

        with gpu.matrix.push_pop():
            gpu.matrix.load_matrix(mat_offscreen)
            gpu.matrix.load_projection_matrix(Matrix())
            onscreen.gem_table(self, x, y, color=_text_color(self.use_background))

        buffer = fb.read_color(0, 0, width, height, 4, 0, "UBYTE")
        buffer.dimensions = width * height * 4

    offscreen.free()

    if image_name not in bpy.data.images:
        bpy.data.images.new(image_name, width, height)

    image = bpy.data.images[image_name]
    image.scale(width, height)
    image.pixels = [v / 255 for v in buffer]

    if self.use_save and bpy.data.is_saved:
        image.filepath_raw = str(Path(bpy.data.filepath).with_suffix("")) + " Gem Map 2.png"
        image.file_format = "PNG"
        image.save()

    bpy.data.images.remove(render_image)
    gpu.state.blend_set("NONE")

    asset.show_window(width, height, space_data={"image": image})
