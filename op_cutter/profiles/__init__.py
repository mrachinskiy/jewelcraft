# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2022  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


from ...lib import gemlib
from . import (
    _fantasy,
    _rectangle,
    _round,
    _triangle,
)


sections = {
    gemlib.SHAPE_FANTASY: _fantasy.Section,
    gemlib.SHAPE_RECTANGLE: _rectangle.Section,
    gemlib.SHAPE_SQUARE: _rectangle.Section,
    gemlib.SHAPE_ROUND: _round.Section,
    gemlib.SHAPE_TRIANGLE: _triangle.Section,
}
