# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


from math import tau, sin, cos

from bmesh.types import BMesh, BMVert


class Section:
    __slots__ = (
        "detalization",
    )

    def __init__(self, operator) -> None:
        self.detalization = operator.detalization

    def add(self, bm: BMesh, size) -> tuple[list[BMVert], list[BMVert]]:
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
