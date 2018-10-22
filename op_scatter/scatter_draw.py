# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
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


class Draw:

    def draw(self, context):
        layout = self.layout

        if self.is_scatter:
            split = layout.split()
            split.label("Object Number")
            split.prop(self, "number", text="")

            layout.separator()

        split = layout.split()
        split.label("Transforms")
        col = split.column(align=True)
        col.prop(self, "rot_y")
        col.prop(self, "rot_z")
        col.prop(self, "loc_z")

        layout.separator()

        split = layout.split()
        split.label("Scatter (%)")
        col = split.column(align=True)
        col.prop(self, "start")
        col.prop(self, "end")

        layout.separator()

        split = layout.split()
        split.prop(self, "use_absolute_offset")
        col = split.column(align=True)
        col.prop(self, "spacing")
