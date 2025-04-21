# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Callable
from math import pi
from typing import NamedTuple

from ...lib import gemlib, ringsizelib


class _Gem(NamedTuple):
    stone: str
    cut: str
    color: str
    size: float
    ct: float
    qty: int
    ct_sum: float


def data_format(Report, _: Callable[[str], str]) -> None:
    _mm = _("mm")
    _g = _("g")

    if Report.gems:

        gems_fmt = []

        for (stone, cut, size, color), qty in sorted(
            Report.gems.items(),
            key=lambda x: (x[0][0], x[0][1], -x[0][2][1], -x[0][2][0]),
        ):

            w, l, h = size
            ct = gemlib.ct_calc(stone, cut, size)
            total_ct = round(ct * qty, 3)

            try:
                stonef = _(gemlib.STONES[stone].name)
                cutf = _(gemlib.CUTS[cut].name)
                trait = gemlib.CUTS[cut].trait
            except KeyError:
                stonef = stone
                cutf = cut
                trait = None

            if trait is gemlib.TRAIT_XY_SYMMETRY:
                sizef = str(l)
            elif trait is gemlib.TRAIT_X_SIZE:
                sizef = f"{w} × {l}"
            else:
                sizef = f"{l} × {w}"

            gems_fmt.append(_Gem(stonef, cutf, _(color), sizef, ct, qty, total_ct))

        Report.gems = gems_fmt

    if Report.metadata:

        Report.metadata = [(_(k), v) for k, v in Report.metadata]

    if Report.materials:

        mats_fmt = []

        for mat_name, density, vol in Report.materials:
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
                    valuef = ringsizelib.to_size_fmt(cir, size_format)
                    if valuef is None:
                        valuef = "[NO CORRESPONDING SIZE]"

            notes_fmt.append((name, valuef))

        Report.notes = notes_fmt
