# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterator
from typing import NamedTuple

import blf
import bpy

_TYPE_BOOL = 1
_TYPE_INT = 2
_TYPE_PROC = 3
_TYPE_ENUM = 4


class _Prop(NamedTuple):
    type: int
    name: str
    key: str
    attr: str
    items: tuple[str]


class Layout:
    __slots__ = "children", "enabled_by", "col_max"
    children: "list[Layout | _Prop]"
    enabled_by: str
    col_max: list[str]

    def __init__(self) -> None:
        self.children = []
        self.enabled_by = ""
        self.col_max = ["", ""]

    def get_col_max(self) -> list[int]:
        for child in self.children:
            if child.__class__ is Layout:
                self.col_max[0] = max(self.col_max[0], child.col_max[0], key=len)
                self.col_max[1] = max(self.col_max[1], child.col_max[1], key=len)

        return self.col_max

    def layout(self) -> "Layout":
        lay = Layout()
        self.children.append(lay)
        return lay

    def _prop(self, type: int, name: str, key: str, attr: str, items: tuple[str] = None) -> None:
        self.children.append(_Prop(type, name, key, attr, items))
        self.col_max[0] = max(self.col_max[0], name, key=len)
        self.col_max[1] = max(self.col_max[1], key, key=len)

    def separator(self) -> None:
        self.children.append(_Prop(None, None, None, None, None))

    def bool(self, name: str, key: str, attr: str) -> None:
        self._prop(_TYPE_BOOL, name, key, attr)

    def int(self, name: str, key: str, attr: str) -> None:
        self._prop(_TYPE_INT, name, key, attr)

    def proc(self, name: str, key: str, attr: str) -> None:
        self._prop(_TYPE_PROC, name, key, attr)

    def enum(self, name: str, key: str, attr: str, items: tuple[str]) -> None:
        self._prop(_TYPE_ENUM, name, key, attr, items)


def _get_font_scale(prefs: bpy.types.Preferences) -> float:
    if bpy.app.version < (4, 3, 0):
        font_size = prefs.ui_styles[0].widget_label.points
    else:
        font_size = prefs.ui_styles[0].widget.points

    return font_size * prefs.view.ui_scale / 11  # 11 is the default font size


def get_xy() -> tuple[int, int]:
    overlay = bpy.context.space_data.overlay
    prefs = bpy.context.preferences
    view = prefs.view
    ui_scale = prefs.view.ui_scale
    fontscale = _get_font_scale(prefs)

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


def _get_props(layout: Layout, data) -> Iterator[_Prop]:
    for child in layout.children:
        if child.__class__ is _Prop:
            yield child
            continue

        if child.enabled_by and not getattr(data, child.enabled_by):
            continue

        yield from _get_props(child, data)


def draw_options(data, layout: Layout, x: int, y: int) -> None:
    prefs = bpy.context.preferences

    color_text = prefs.themes[0].view_3d.space.text_hi
    color_grey = (0.67, 0.67, 0.67, 1.0)
    color_green = (0.3, 1.0, 0.3, 1.0)
    color_red = (1.0, 0.3, 0.3, 1.0)
    color_yellow = (0.9, 0.9, 0.0, 1.0)
    color_blue = (0.5, 0.6, 1.0, 1.0)

    fontid = 1
    fontscale = _get_font_scale(prefs)
    fontsize = round(fontscale * 15)

    blf.size(fontid, fontsize)

    col_max = layout.get_col_max()
    w_col1, _ = blf.dimensions(fontid, col_max[0])
    w_col2, _ = blf.dimensions(fontid, col_max[1])
    _, h_font = blf.dimensions(fontid, "M")
    lineheight = round(h_font * 1.8)

    for prop in _get_props(layout, data):
        y -= lineheight
        _x = x

        if prop.type is None:
            continue

        blf.position(fontid, x, y, 0.0)
        blf.color(fontid, *color_text, 1.0)
        blf.draw(fontid, prop.name)

        if prop.key:
            _x += w_col1 + 20
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_grey)
            blf.draw(fontid, prop.key)

        if prop.type is _TYPE_BOOL:
            _x += w_col2 + 10
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            _x += 20
            blf.position(fontid, _x, y, 0.0)
            if getattr(data, prop.attr):
                blf.color(fontid, *color_green)
                blf.draw(fontid, "ON")
            else:
                blf.color(fontid, *color_red)
                blf.draw(fontid, "OFF")

        elif prop.type is _TYPE_INT:
            _x += w_col2 + 10
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            _x += 20
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_blue)
            blf.draw(fontid, str(round(getattr(data, prop.attr), 1)))

        elif prop.type is _TYPE_ENUM:
            _x += w_col2 + 10
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, ":")

            _x += 20
            blf.position(fontid, _x, y, 0.0)
            blf.color(fontid, *color_text, 1.0)
            blf.draw(fontid, prop.items[getattr(data, prop.attr)])

        elif prop.type is _TYPE_PROC:
            if getattr(data, prop.attr):
                _x += w_col2 + 10
                blf.position(fontid, _x, y, 0.0)
                blf.color(fontid, *color_text, 1.0)
                blf.draw(fontid, ":")

                _x += 20
                blf.position(fontid, _x, y, 0.0)
                blf.color(fontid, *color_yellow)
                blf.draw(fontid, "PROCESSING...")
