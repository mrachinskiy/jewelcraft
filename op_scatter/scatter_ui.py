# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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


class UI:

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if self.is_scatter:
            layout.prop(self, "number")
            layout.separator()

        layout.label(text="Transforms")
        col = layout.column(align=True)
        col.prop(self, "rot_x")
        col.prop(self, "rot_z")
        col.prop(self, "loc_z")

        layout.separator()

        layout.label(text="Scatter (%)")
        col = layout.column(align=True)
        col.prop(self, "start")
        col.prop(self, "end")

        layout.separator()

        split = layout.split(align=True, factor=0.49)
        split.prop(self, "use_absolute_offset")
        sub = split.row()
        sub.enabled = self.use_absolute_offset
        sub.prop(self, "spacing", text="")
