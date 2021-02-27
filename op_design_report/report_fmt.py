# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


from typing import Callable
from math import pi

from ..lib import gemlib, ringsizelib


def data_format(Report, _: Callable[[str], str]) -> None:
    _mm = _("mm")
    _g = _("g")

    if Report.gems:

        gems_fmt = []

        for (stone, cut, size), qty in sorted(
            Report.gems.items(),
            key=lambda x: (x[0][0], x[0][1], -x[0][2][1], -x[0][2][0]),
        ):

            w, l, h = size
            ct = gemlib.ct_calc(stone, cut, size)
            total_ct = round(ct * qty, 3)

            try:
                stonef = _(gemlib.STONES[stone].name)
                cutf = _(gemlib.CUTS[cut].name)
                xy_symmetry = gemlib.CUTS[cut].xy_symmetry
            except KeyError:
                stonef = stone
                cutf = cut
                xy_symmetry = False

            if xy_symmetry:
                sizef = str(l)
            else:
                sizef = f"{l} × {w}"

            gems_fmt.append((stonef, cutf, sizef, ct, qty, total_ct))

        Report.gems = gems_fmt

    if Report.materials:

        mats_fmt = []

        for (mat_name, density), vol in Report.materials.items():
            weight = round(vol * density, 2)
            weightf = f"{weight} {_g}"

            mats_fmt.append((mat_name, weightf))

        Report.materials = mats_fmt

    if Report.notes:

        notes_fmt = []

        for item_type, name, values in Report.notes:

            if item_type == "DIMENSIONS":
                valuef = " × ".join([str(x) for x in values])
                valuef += f" {_mm}"

            elif item_type == "RING_SIZE":
                dia, size_format = values
                cir = dia * pi

                if size_format == "DIA":
                    valuef = f"{dia} {_mm}"
                elif size_format == "CIR":
                    valuef = f"{round(cir, 2)} {_mm}"
                else:
                    valuef = ringsizelib.cir_to_size(cir, size_format)

            notes_fmt.append((name, valuef))

        Report.notes = notes_fmt
