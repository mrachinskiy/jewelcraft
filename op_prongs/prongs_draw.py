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

        layout.prop(self, "auto_presets")

        layout.separator()

        split = layout.split()
        split.label("Prong Number")
        split.prop(self, "number", text="")

        layout.separator()

        split = layout.split()
        split.label("Dimensions")
        col = split.column(align=True)
        col.prop(self, "z_top", text="Top")
        col.prop(self, "diameter", text="Diameter")
        col.prop(self, "z_btm", text="Bottom")

        layout.separator()

        split = layout.split()
        split.label("Position")
        col = split.column(align=True)
        col.prop(self, "position", text="Position")
        col.prop(self, "intersection", text="Intersection")
        col.prop(self, "alignment", text="Alignment")

        layout.separator()

        split = layout.split()
        split.prop(self, "symmetry", text="Symmetry")
        split.prop(self, "symmetry_pivot", text="Pivot")

        layout.separator()

        split = layout.split()
        split.label("Deformations")
        col = split.column(align=True)
        col.prop(self, "bump_scale", text="Bump Scale")
        col.prop(self, "taper", text="Taper")

        layout.separator()

        split = layout.split()
        split.label("Detalization")
        split.prop(self, "detalization", text="")
