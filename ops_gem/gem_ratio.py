# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Object

from ..lib import asset


_cuts = {
    "OVAL": (
        (
            (set(range(5, 12 + 1)), 2),
            ({14, 16}, 4),
            ({18, 20}, 5),
        ),
        1.6,
    ),
    "PEAR": (
        (
            ({5, 6, 7}, 2),
            ({9, 10}, 3),
            ({12, 13, 16}, 4),
            ({14, 15, 18, 20}, 5),
        ),
        1.6,
    ),
}


def validate(ob: Object, cut: str, size: float) -> None:
    if cut not in _cuts:
        return

    ranges, scale_correction = _cuts[cut]
    size_int = int(size + 0.5)

    for range_, delta in ranges:
        if size_int in range_:
            ob.scale.x = (size_int - delta) * (size / size_int) * scale_correction
            asset.apply_scale(ob)
            return
