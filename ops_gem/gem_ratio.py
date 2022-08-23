# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from bpy.types import Object

from ..lib import asset


_cuts = {
    "OVAL": (
        (
            (5, 12, 2),
            (14, 16, 4),
            (18, 20, 5),
        ),
        1.6,
    ),
    "PEAR": (
        (
            (5, 7, 2),
            (9, 10, 3),
            (12, 13, 4),
            (14, 15, 5),
            (15, 17, 4),
            (18, 20, 5),
        ),
        1.6,
    ),
}


def validate(ob: Object, cut: str, size: float) -> None:
    if cut not in _cuts:
        return

    ranges, scale_correction = _cuts[cut]

    for start, end, delta in ranges:
        if start <= size <= end:
            size_x = size - delta
            break
    else:
        return

    ob.scale.x = size_x * scale_correction
    asset.apply_scale(ob)
