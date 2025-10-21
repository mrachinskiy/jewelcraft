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


def data_format(Report, _: Callable[[str], str], fmt_str: bool) -> None:
    _mm = _("mm")
    _mm3 = _("mm³")
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
                sizef = l
            elif trait is gemlib.TRAIT_X_SIZE:
                if fmt_str:
                    sizef = f"{w} × {l}"
                else:
                    sizef = (w, l)
            else:
                if fmt_str:
                    sizef = f"{l} × {w}"
                else:
                    sizef = (l, w)

            gems_fmt.append(_Gem(stonef, cutf, _(color), sizef, ct, qty, total_ct))

        Report.gems = gems_fmt

    if Report.metadata:

        Report.metadata = [(_(k), v) for k, v in Report.metadata]

    if Report.entries:

        entries_fmt = []

        for item_type, name, values in Report.entries:

            if item_type == "WEIGHT":
                vol, density = values
                value = round(vol * density, 2)
                if fmt_str:
                    value = f"{value} {_g}"

            elif item_type == "VOLUME":
                value = round(values, 2)
                if fmt_str:
                    value = f"{value} {_mm3}"

            elif item_type == "DIMENSIONS":
                value = values
                if fmt_str:
                    value = " × ".join([str(x) for x in values])
                    value = f"{value} {_mm}"

            elif item_type == "RING_SIZE":
                dia, size_format = values
                cir = dia * pi

                if size_format == "DIAMETER":
                    value = dia
                    if fmt_str:
                        value = f"{value} {_mm}"
                elif size_format == "CIRCUMFERENCE":
                    value = round(cir, 2)
                    if fmt_str:
                        value = f"{value} {_mm}"
                else:
                    value = ringsizelib.to_size_fmt(cir, size_format)
                    if fmt_str and value is None:
                        value = "[NO CORRESPONDING SIZE]"

            entries_fmt.append((item_type, name, value))

        Report.entries = entries_fmt
