# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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


import blf


TYPE_BOOL = 0
TYPE_NUM = 1
TYPE_PROC = 2
TYPE_ENUM = 3
TYPE_DEP_ON = 4
TYPE_DEP_OFF = 5


def padding_init(context, x=20, y=10):
    for region in context.area.regions:
        if region.type == "HEADER":
            y += region.height
        elif region.type == "TOOLS":
            x += region.width

    view = context.preferences.view
    overlay = context.space_data.overlay

    if overlay.show_text and (view.show_view_name or view.show_object_info):
        y += 60
    if overlay.show_stats:
        y += 140

    y = context.region.height - y

    return x, y


def options_init(self, values):
    self.font_size_options = 17

    self.option_list = values
    self.option_col_1_max = max(self.option_list, key=lambda x: len(x[0]))[0]
    self.option_col_2_max = max(self.option_list, key=lambda x: len(x[1]))[1]


def options_display(self, context, x, y):
    color_white = (0.95, 0.95, 0.95, 1.0)
    color_grey = (0.67, 0.67, 0.67, 1.0)
    color_green = (0.3, 1.0, 0.3, 1.0)
    color_red = (1.0, 0.3, 0.3, 1.0)
    color_yellow = (0.9, 0.9, 0.0, 1.0)
    color_blue = (0.5, 0.6, 1.0, 1.0)

    fontid = 1
    blf.size(fontid, self.prefs.view_font_size_option, 72)

    font_w_1, font_h = blf.dimensions(fontid, self.option_col_1_max)
    font_w_2, _ = blf.dimensions(fontid, self.option_col_2_max)
    font_row_height = font_h * 1.5

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
        blf.color(fontid, *color_white)
        blf.draw(fontid, option)

        if hotkey:
            x_ofst += font_w_1 + 20
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_grey)
            blf.draw(fontid, hotkey)

        if type_ is TYPE_BOOL:
            x_ofst += font_w_2 + 10
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_white)
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
            blf.color(fontid, *color_white)
            blf.draw(fontid, ":")

            x_ofst += 20
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_blue)
            blf.draw(fontid, str(round(getattr(self, prop), 1)))

        elif type_ is TYPE_ENUM:
            x_ofst += font_w_2 + 10
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_white)
            blf.draw(fontid, ":")

            x_ofst += 20
            blf.position(fontid, x_ofst, y, 0.0)
            blf.color(fontid, *color_white)
            blf.draw(fontid, getattr(self, f"{prop}_enum")[getattr(self, prop)])

        elif type_ is TYPE_PROC:
            if getattr(self, prop):
                x_ofst += font_w_2 + 10
                blf.position(fontid, x_ofst, y, 0.0)
                blf.color(fontid, *color_white)
                blf.draw(fontid, ":")

                x_ofst += 20
                blf.position(fontid, x_ofst, y, 0.0)
                blf.color(fontid, *color_yellow)
                blf.draw(fontid, "PROCESSING...")
