# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import bpy
import blf


TYPE_BOOL = 0
TYPE_NUM = 1
TYPE_PROC = 2
TYPE_ENUM = 3
TYPE_DEP_ON = 4
TYPE_DEP_OFF = 5


def padding_init(x=20, y=10) -> tuple[int, int]:
    for region in bpy.context.area.regions:
        if region.type == "HEADER":
            y += region.height
        elif region.type == "TOOLS":
            x += region.width

    view = bpy.context.preferences.view
    overlay = bpy.context.space_data.overlay

    if overlay.show_text and (view.show_view_name or view.show_object_info):
        y += 60
    if overlay.show_stats:
        y += 140

    y = bpy.context.region.height - y

    return x, y


def options_init(self, values: tuple[tuple[str, str, str, int], ...]) -> None:
    self.option_list = values
    self.option_col_1_max = max(self.option_list, key=lambda x: len(x[0]))[0]
    self.option_col_2_max = max(self.option_list, key=lambda x: len(x[1]))[1]


def options_display(self, context, x: int, y: int) -> None:
    prefs = context.preferences

    color_text = prefs.themes[0].view_3d.space.text_hi
    color_grey = (0.67, 0.67, 0.67, 1.0)
    color_green = (0.3, 1.0, 0.3, 1.0)
    color_red = (1.0, 0.3, 0.3, 1.0)
    color_yellow = (0.9, 0.9, 0.0, 1.0)
    color_blue = (0.5, 0.6, 1.0, 1.0)

    fontid = 1
    fontsize = round(prefs.ui_styles[0].widget_label.points * prefs.view.ui_scale)

    blf.size(fontid, fontsize, 104)

    font_w_1, font_h = blf.dimensions(fontid, self.option_col_1_max)
    font_w_2, _ = blf.dimensions(fontid, self.option_col_2_max)
    font_row_height = round(font_h * 1.5)

    layout_enabled = True

    for option, hotkey, prop, type_ in self.option_list:

        if type_ is TYPE_DEP_OFF:
            layout_enabled = True
            continue

        if not layout_enabled:
            continue

        if type_ is TYPE_DEP_ON:
            layout_enabled = getattr(self, prop)
            continue

        y -= font_row_height
        x_ofst = x

        blf.position(fontid, x, y, 0.0)
        blf.color(fontid, *color_text, 1.0)
        blf.draw(fontid, option)

        if hotkey:
            x_ofst += font_w_1 + 20
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_grey)
            blf.draw(fontid, hotkey)

        if type_ is TYPE_BOOL:
            x_ofst += font_w_2 + 10
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            x_ofst += 20
            blf.position(fontid, x_ofst, y, 0.0)
            if getattr(self, prop):
                blf.color(fontid, *color_green)
                blf.draw(fontid, "ON")
            else:
                blf.color(fontid, *color_red)
                blf.draw(fontid, "OFF")

        elif type_ is TYPE_NUM:
            x_ofst += font_w_2 + 10
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            x_ofst += 20
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_blue)
            blf.draw(fontid, str(round(getattr(self, prop), 1)))

        elif type_ is TYPE_ENUM:
            x_ofst += font_w_2 + 10
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            x_ofst += 20
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, getattr(self, f"{prop}_enum")[getattr(self, prop)])

        elif type_ is TYPE_PROC:
            if getattr(self, prop):
                x_ofst += font_w_2 + 10
                blf.position(fontid, x_ofst, y, 0.0)
                blf.color(fontid, *color_text, 1.0)
                blf.draw(fontid, ":")

                x_ofst += 20
                blf.position(fontid, x_ofst, y, 0.0)
                blf.color(fontid, *color_yellow)
                blf.draw(fontid, "PROCESSING...")
