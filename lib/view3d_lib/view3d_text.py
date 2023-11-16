# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

import blf
import bpy

TYPE_BOOL = 1
TYPE_INT = 2
TYPE_PROC = 3
TYPE_ENUM = 4
TYPE_DEP_ON = 5
TYPE_DEP_OFF = 6


def get_xy() -> tuple[int, int]:
    overlay = bpy.context.space_data.overlay
    prefs = bpy.context.preferences
    view = prefs.view
    ui_scale = prefs.view.ui_scale
    fontscale = prefs.ui_styles[0].widget_label.points * ui_scale / 11  # 11 is the default font size

    x = round(20 * ui_scale)
    y = round(10 * ui_scale)

    for region in bpy.context.area.regions:
        if region.type in {"HEADER", "TOOL_HEADER"}:
            y += region.height
        elif region.type == "TOOLS":
            x += region.width

    _y = 0

    if overlay.show_text and (view.show_view_name or view.show_object_info):
        _y += 60
    if overlay.show_stats:
        _y += 140

    y += round(_y * fontscale)
    y = bpy.context.region.height - y

    return x, y


def draw_options(props, options: tuple[tuple[str, str, str, int]], x: int, y: int) -> None:
    prefs = bpy.context.preferences

    color_text = prefs.themes[0].view_3d.space.text_hi
    color_grey = (0.67, 0.67, 0.67, 1.0)
    color_green = (0.3, 1.0, 0.3, 1.0)
    color_red = (1.0, 0.3, 0.3, 1.0)
    color_yellow = (0.9, 0.9, 0.0, 1.0)
    color_blue = (0.5, 0.6, 1.0, 1.0)

    fontid = 1
    fontscale = prefs.ui_styles[0].widget_label.points * prefs.view.ui_scale / 11  # 11 is the default font size
    fontsize = round(fontscale * 15)

    blf.size(fontid, fontsize)

    col_max = (
        max((x[0] for x in options), key=len),
        max((x[1] for x in options), key=len),
    )
    w_col1, h_font = blf.dimensions(fontid, col_max[0])
    w_col2, _ = blf.dimensions(fontid, col_max[1])
    lineheight = round(h_font * 1.5)

    layout_enabled = True

    for option, hotkey, prop, type_ in options:

        if type_ is TYPE_DEP_OFF:
            layout_enabled = True
            continue

        if not layout_enabled:
            continue

        if type_ is TYPE_DEP_ON:
            layout_enabled = getattr(props, prop)
            continue

        y -= lineheight
        _x = x

        blf.position(fontid, x, y, 0.0)
        blf.color(fontid, *color_text, 1.0)
        blf.draw(fontid, option)

        if hotkey:
            _x += w_col1 + 20
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_grey)
            blf.draw(fontid, hotkey)

        if type_ is TYPE_BOOL:
            _x += w_col2 + 10
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            _x += 20
            blf.position(fontid, _x, y, 0.0)
            if getattr(props, prop):
                blf.color(fontid, *color_green)
                blf.draw(fontid, "ON")
            else:
                blf.color(fontid, *color_red)
                blf.draw(fontid, "OFF")

        elif type_ is TYPE_INT:
            _x += w_col2 + 10
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            _x += 20
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_blue)
            blf.draw(fontid, str(round(getattr(props, prop), 1)))

        elif type_ is TYPE_ENUM:
            _x += w_col2 + 10
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            _x += 20
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, getattr(props, f"{prop}_enum")[getattr(props, prop)])

        elif type_ is TYPE_PROC:
            if getattr(props, prop):
                _x += w_col2 + 10
                blf.position(fontid, _x, y, 0.0)
                blf.color(fontid, *color_text, 1.0)
                blf.draw(fontid, ":")

                _x += 20
                blf.position(fontid, _x, y, 0.0)
                blf.color(fontid, *color_yellow)
                blf.draw(fontid, "PROCESSING...")
