# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
from pathlib import Path

import bpy
import gpu
from bpy_extras.image_utils import load_image
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from ...lib import asset, colorlib, overlays
from . import onscreen


def _get_resolution(region, region_3d, render) -> tuple[int, int]:
    resolution_scale = render.resolution_percentage / 100

    if region_3d.view_perspective == "CAMERA":
        return round(render.resolution_x * resolution_scale), round(render.resolution_y * resolution_scale)
    else:
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


def render_map(self):
    image_name = "Gem Map"
    temp_filepath = Path(tempfile.gettempdir()) / "gem_map_temp.png"

    render = bpy.context.scene.render
    width, height = _get_resolution(self.region, self.region_3d, render)
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

        # Render result
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

        # Gems
        with gpu.matrix.push_pop():
            if self.region_3d.view_perspective == "CAMERA":
                view_matrix = bpy.context.scene.camera.matrix_world.inverted()
                projection_matrix = bpy.context.scene.camera.calc_matrix_camera(
                    bpy.context.evaluated_depsgraph_get(), x=width, y=height
                )
            else:
                view_matrix = self.region_3d.view_matrix
                projection_matrix = self.region_3d.window_matrix

            gpu.matrix.load_matrix(view_matrix)
            gpu.matrix.load_projection_matrix(projection_matrix)
            overlays.gem_map._draw(self, bpy.context, is_overlay=False, use_select=self.use_select, use_mat_color=self.use_mat_color)

        # Text
        with gpu.matrix.push_pop():
            gpu.matrix.load_matrix(mat_offscreen)
            gpu.matrix.load_projection_matrix(Matrix())

            to_2d = _ViewToCamLoc(self.region, self.region_3d, render).to_2d
            overlays.gem_map._draw_font(self, bpy.context, to_2d)
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



class _ViewToCamLoc:
    __slots__ = "scale", "offset"

    def __init__(self, region, region_3d, render) -> None:
        self.scale = Vector((1.0, 1.0))
        self.offset = Vector((0.0, 0.0))

        if region_3d.view_perspective == "CAMERA":
            width, height = _get_resolution(region, region_3d, render)
            frame_width, frame_height, frame_offset = self._get_frame(region, region_3d)
            self.scale.xy = width / frame_width, height / frame_height
            self.offset = frame_offset.xy
        else:
            self.scale.xy = render.resolution_percentage / 100

    def to_2d(self, region, region_3d, loc: Vector) -> Vector:
        v = location_3d_to_region_2d(region, region_3d, loc)
        return (v - self.offset) * self.scale

    @staticmethod
    def _get_frame(region, region_3d) -> tuple[float, float, Vector]:
        scene = bpy.context.scene
        cam = scene.camera
        frame = [
            location_3d_to_region_2d(region, region_3d, cam.matrix_world @ p)
            for p in cam.data.view_frame(scene=scene)
        ]
        return frame[1].x - frame[2].x, frame[0].y - frame[1].y, frame[2]
