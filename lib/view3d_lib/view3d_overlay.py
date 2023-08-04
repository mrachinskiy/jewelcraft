# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


def draw_axis(self, context):
    gpu.state.blend_set("ALPHA")
    gpu.state.depth_mask_set(True)
    if not self.axis_in_front:
        gpu.state.depth_test_set("LESS_EQUAL")

    shader = gpu.shader.from_builtin("POLYLINE_SMOOTH_COLOR")
    shader.uniform_float("viewportSize", (context.area.width, context.area.height))
    shader.uniform_float("lineWidth", self.axis_width)

    colors = (
        (1.0, 0.25, 0.25, 1.0), (1.0, 0.5, 0.25, 1.0),
        (0.25, 1.0, 0.25, 1.0), (0.25, 0.85, 0.6, 1.0),
        (0.25, 0.25, 1.0, 1.0), (0.0, 0.7, 1.0, 1.0),
    )
    indxs = ((0, 1), (2, 3), (4, 5))

    for mat in self.mats:
        start = mat.translation
        x_end = mat @ Vector((self.axis_size, 0.0, 0.0))
        y_end = mat @ Vector((0.0, self.axis_size, 0.0))
        z_end = mat @ Vector((0.0, 0.0, self.axis_size))
        points = (
            start, x_end,
            start, y_end,
            start, z_end,
        )

        batch = batch_for_shader(shader, "LINES", {"pos": points, "color": colors}, indices=indxs)
        batch.draw(shader)

    gpu.state.blend_set("NONE")
    gpu.state.depth_test_set("NONE")
    gpu.state.depth_mask_set(False)
