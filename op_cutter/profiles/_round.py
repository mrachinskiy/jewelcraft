# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from math import tau, sin, cos

from bmesh.types import BMesh, BMVert

from ._types import SectionSize


class Section:
    __slots__ = (
        "detalization",
    )

    def __init__(self, operator) -> None:
        self.detalization = operator.detalization

    def add(self, bm: BMesh, size: SectionSize) -> tuple[list[BMVert], list[BMVert]]:
        angle = tau / self.detalization
        vs1 = []
        vs2 = []
        app1 = vs1.append
        app2 = vs2.append

        for i in range(self.detalization):
            x = sin(i * angle) * size.y
            y = cos(i * angle) * size.y

            app1(bm.verts.new((-x, y, size.z1)))
            app2(bm.verts.new((-x, y, size.z2)))

        return vs1, vs2
