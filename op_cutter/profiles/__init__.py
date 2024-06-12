# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from ...lib import gemlib
from . import fantasy, rectangle, round, triangle


def get(op):
    match op.shape:
        case gemlib.SHAPE_ROUND:
            return round.Section(op)
        case gemlib.SHAPE_RECTANGLE | gemlib.SHAPE_SQUARE:
            return rectangle.Section(op)
        case gemlib.SHAPE_FANTASY:
            return fantasy.Section(op)
        case gemlib.SHAPE_TRIANGLE:
            return triangle.Section(op)
