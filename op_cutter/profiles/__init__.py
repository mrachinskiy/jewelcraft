# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

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
