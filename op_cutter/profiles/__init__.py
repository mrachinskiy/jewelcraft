# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from ...lib import gemlib
from ._types import SectionSize
from . import (
    _fantasy,
    _rectangle,
    _round,
    _triangle,
)


sections: dict[int, type[_round.Section]] = {
    gemlib.SHAPE_FANTASY: _fantasy.Section,
    gemlib.SHAPE_RECTANGLE: _rectangle.Section,
    gemlib.SHAPE_SQUARE: _rectangle.Section,
    gemlib.SHAPE_ROUND: _round.Section,
    gemlib.SHAPE_TRIANGLE: _triangle.Section,
}
