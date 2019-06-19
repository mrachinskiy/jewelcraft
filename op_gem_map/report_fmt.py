# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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


from mathutils import Color

from .. import var
from ..lib import asset, gettext


def data_format(self, context, data):
    self.gems_raw = []
    self.gems_fmt = []
    gems_fmt_temp = []
    col_stone = 0
    col_cut = 0
    col_size = 0
    color_var = Color((0.85, 0.35, 0.35))
    _ = gettext.GetText(context, self.lang).gettext
    _pcs = _("pcs")
    _mm = _("mm")

    for (stone, cut, size), qty in sorted(
        data["gems"].items(),
        key=lambda x: (x[0][1], -x[0][2][1], -x[0][2][0], x[0][0]),
    ):
        # Color
        # ---------------------------

        color = (*color_var, 1.0)

        color_var.h += 0.15

        if color_var.h == 0.0:
            color_var.s += 0.1
            color_var.v -= 0.15

        # Format
        # ---------------------------

        l = asset.to_int(size[1])
        w = asset.to_int(size[0])

        stone_fmt = _(asset.get_name(stone))
        cut_fmt = _(asset.get_name(cut))
        qty_fmt = f"{qty} {_pcs}"

        if cut in var.CUT_SIZE_SINGLE:
            size_raw_fmt = str(l)
            size_fmt = f"{l} {_mm}"
        else:
            size_raw_fmt = f"{l}×{w}"
            size_fmt = f"{l} × {w} {_mm}"

        self.gems_raw.append((stone, cut, size, size_raw_fmt, color))
        gems_fmt_temp.append((stone_fmt, cut_fmt, size_fmt, qty_fmt, color))

        # Columns width
        # ---------------------------

        col_stone = max(col_stone, len(stone_fmt))
        col_cut = max(col_cut, len(cut_fmt))
        col_size = max(col_size, len(size_fmt))

    for stone, cut, size, qty, color in gems_fmt_temp:
        row = f"{cut:{col_cut}}   {size:{col_size}}   {stone:{col_stone}}   {qty}"
        self.gems_fmt.append((row, color))
