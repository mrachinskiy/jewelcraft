# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bmesh.types import BMesh, BMVert
from mathutils import Vector

from ....lib import gemlib
from . import fantasy, rectangle, round, triangle


class Section:

    def add(self, bm: BMesh, size: Vector, offset: tuple[float, float, float] = None) -> tuple[list[BMVert], list[BMVert]]:
        ...

    def add_z_fmt(self, bm: BMesh, size: Vector) -> tuple[list[BMVert], list[BMVert]]:
        ...

    def add_seat_rect(self, bm: BMesh, girdle_verts: list[BMVert], Girdle: Vector, Hole: Vector) -> None:
        ...


def get(op) -> Section:
    match op.shape:
        case gemlib.SHAPE_ROUND:
            return round.Section(op)
        case gemlib.SHAPE_RECTANGLE | gemlib.SHAPE_SQUARE:
            return rectangle.Section(op)
        case gemlib.SHAPE_FANTASY:
            return fantasy.Section(op)
        case gemlib.SHAPE_TRIANGLE:
            return triangle.Section(op)
