# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..lib import view3d_lib

Color = tuple[float, float, float]
_handler = None


def handler_add(self, context):
    global _handler

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(_draw, (self, context), "WINDOW", "POST_PIXEL")


def handler_del():
    global _handler

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        _handler = None


def _draw(self, context):
    separator = 40
    x, y = view3d_lib.get_xy()

    # Onscreen text
    # -----------------------------

    y = gem_table(self, x, y)
    y -= separator

    if self.show_warn:
        y = warning(self, x, y)
        y -= separator

    view3d_lib.draw_options(self, self.view_options, x, y)

    # Reset state
    # ----------------------------

    gpu.state.blend_set("NONE")


def gem_table(self, x: int, y: int, color: Color | None = None) -> int:
    fontid = 1
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")

    if color is None:
        color = bpy.context.preferences.themes[0].view_3d.space.text_hi

    blf.size(fontid, self.prefs.gem_map_fontsize_table)
    blf.color(fontid, *color, 1.0)

    _, font_h = blf.dimensions(fontid, "Row Height")
    font_baseline = round(font_h * 0.4)
    font_row_height = font_h * 2
    icon_size = font_h * 1.5
    y += font_baseline
    indices = ((0, 1, 2), (0, 2, 3))

    for row, icon_color in self.table_data:
        y -= font_row_height

        points = (
            (x,             y),
            (x + icon_size, y),
            (x + icon_size, y + icon_size),
            (x,             y + icon_size),
        )

        shader.bind()
        shader.uniform_float("color", icon_color)
        batch_font = batch_for_shader(shader, "TRIS", {"pos": points}, indices=indices)
        batch_font.draw(shader)

        blf.position(fontid, x + font_row_height, y + font_baseline, 0.0)
        blf.draw(fontid, row)

    return y


def warning(self, x, y):
    fontid = 1
    blf.size(fontid, self.prefs.gem_map_fontsize_table)
    blf.color(fontid, 1.0, 0.3, 0.3, 1.0)

    _, font_h = blf.dimensions(fontid, "Row Height")
    font_row_height = font_h * 2
    y += font_h

    for row in self.warn:
        y -= font_row_height

        blf.position(fontid, x, y, 0.0)
        blf.draw(fontid, row)

    return y
