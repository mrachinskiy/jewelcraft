# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from ...lib import gemlib
from . import _fantasy, _rectangle, _round, _triangle


def get(op):
    match op.shape:
        case gemlib.SHAPE_FANTASY:
            return _fantasy.Section(op)
        case gemlib.SHAPE_RECTANGLE:
            return _rectangle.Section(op)
        case gemlib.SHAPE_SQUARE:
            return _rectangle.Section(op)
        case gemlib.SHAPE_ROUND:
            return _round.Section(op)
        case gemlib.SHAPE_TRIANGLE:
            return _triangle.Section(op)
