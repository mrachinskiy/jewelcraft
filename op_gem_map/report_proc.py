# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from mathutils import Color

from ..lib import colorlib, gemlib, gettext


def _to_int(x: float) -> int | float:
    if x.is_integer():
        return int(x)
    return x


def data_process(ReportData, lang: str) -> tuple[str, tuple[int]]:
    table_data = []
    _table_tmp = []
    col_stone = 0
    col_cut = 0
    col_size = 0
    col_color_name = 0
    color_var = Color((0.85, 0.35, 0.35))
    _ = gettext.GetText(lang).gettext
    _pcs = _("pcs")
    _mm = _("mm")

    for (stone, cut, size, color_name), qty in sorted(
        ReportData.gems.items(),
        key=lambda x: (x[0][1], -x[0][2][1], -x[0][2][0], x[0][0]),
    ):
        # Color
        # ---------------------------

        color = (*color_var, 1.0)

        color_var.h += 0.15

        if color_var.h == 0.0:
            color_var.s += 0.1
            color_var.v -= 0.15

        if color_name:
            mat_color = (*[colorlib.linear_to_srgb(x) for x in bpy.data.materials[color_name].diffuse_color[:3]], 1.0)
        else:
            mat_color = (0.0, 0.0, 0.0, 0.0)

        # Format
        # ---------------------------

        l = _to_int(size[1])
        w = _to_int(size[0])

        try:
            stone_fmt = _(gemlib.STONES[stone].name)
            cut_fmt = _(gemlib.CUTS[cut].name)
            trait = gemlib.CUTS[cut].trait
        except KeyError:
            stone_fmt = stone
            cut_fmt = cut
            trait = None

        if trait is gemlib.TRAIT_XY_SYMMETRY:
            size_fmt = f"{l} {_mm}"
        elif trait is gemlib.TRAIT_X_SIZE:
            size_fmt = f"{w} × {l} {_mm}"
        else:
            size_fmt = f"{l} × {w} {_mm}"

        qty_fmt = f"{qty} {_pcs}"

        _table_tmp.append((stone_fmt, cut_fmt, size_fmt, _(color_name), qty_fmt, color, mat_color))

        # Columns width
        # ---------------------------

        col_stone = max(col_stone, len(stone_fmt))
        col_cut = max(col_cut, len(cut_fmt))
        col_size = max(col_size, len(size_fmt))
        col_color_name = max(col_color_name, len(color_name))

    for stone, cut, size, color_name, qty, color, mat_color in _table_tmp:
        row = f"{cut:{col_cut}}   {size:{col_size}}   {stone:{col_stone}}   {color_name:{col_color_name}}   {qty}"
        table_data.append((row, color, mat_color))

    return table_data
