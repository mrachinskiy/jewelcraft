# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy

from collections.abc import Callable

from ...lib import gemlib
from . import report


def data_format(Report: report.Data, _: Callable[[str], str], fmt_str: bool) -> None:
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
                sizef = (w, l)
            else:
                sizef = (l, w)

            if fmt_str and isinstance(sizef, tuple):
                sizef = f"{sizef[0]} × {sizef[1]}"

            gems_fmt.append(report.GemFmt(stonef, cutf, _(color), sizef, ct, qty, total_ct))

        Report.gems = gems_fmt

    if Report.metadata:

        Report.metadata = [report.Meta(_(k), v) for k, v in Report.metadata]

    if fmt_str and Report.entries:

        entries_fmt = []

        for typ, name, value in Report.entries:
            if typ == "WEIGHT":
                value = f"{value} {_g}"
            elif typ == "VOLUME":
                value = f"{value} {_mm3}"
            elif typ == "DIMENSIONS":
                value = " × ".join([str(x) for x in value])
                value = f"{value} {_mm}"
            elif typ == "RING_SIZE":
                size_format, value = value
                if size_format in {"DIAMETER", "CIRCUMFERENCE"}:
                    value = f"{value} {_mm}"
                elif value is None:
                    value = "[NO CORRESPONDING SIZE]"

            entries_fmt.append((typ, name, value))

        Report.entries = entries_fmt
