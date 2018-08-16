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
        split.prop(self, "handle", text="Handle")
        col = split.column(align=True)
        col.prop(self, "handle_z_top", text="Top")

        if self.shape_rnd or self.shape_sq:
            col.prop(self, "handle_l_size", text="Size")
        else:
            col.prop(self, "handle_l_size", text="Length")
            col.prop(self, "handle_w_size", text="Width")

        col.prop(self, "handle_z_btm", text="Bottom")

        layout.separator()

        split = layout.split()
        split.label("Girdle")
        col = split.column(align=True)
        col.prop(self, "girdle_z_top", text="Top")

        if not self.shape_tri:
            col.prop(self, "girdle_l_ofst", text="Size Offset")
        else:
            col.prop(self, "girdle_l_ofst", text="Length Offset")
            col.prop(self, "girdle_w_ofst", text="Width Offset")

        col.prop(self, "girdle_z_btm", text="Bottom")

        layout.separator()

        split = layout.split()
        split.prop(self, "hole", text="Hole")
        col = split.column(align=True)
        col.prop(self, "hole_z_top", text="Top/Culet")

        if self.shape_rnd or self.shape_sq:
            col.prop(self, "hole_l_size", text="Size")
        else:
            col.prop(self, "hole_l_size", text="Length")
            col.prop(self, "hole_w_size", text="Width")

        col.prop(self, "hole_z_btm", text="Bottom")

        if self.shape_fant and self.cut in {"PEAR", "HEART"}:
            col.prop(self, "hole_pos_ofst", text="Position Offset")

        if not self.shape_rnd:

            layout.separator()

            split = layout.split()
            split.prop(self, "curve_seat", text="Curve Seat")
            col = split.column(align=True)
            col.prop(self, "curve_seat_segments", text="Segments")
            col.prop(self, "curve_seat_profile", text="Profile")

            if self.shape_tri:

                layout.separator()

                split = layout.split()
                split.prop(self, "curve_profile", text="Curve Profile")
                col = split.column(align=True)
                col.prop(self, "curve_profile_segments", text="Segments")
                col.prop(self, "curve_profile_factor", text="Factor")

            elif self.cut == "MARQUISE":

                layout.separator()

                split = layout.split()
                split.label("Profile")
                col = split.column(align=True)
                col.prop(self, "mul_1", text="Factor 1")
                col.prop(self, "mul_2", text="Factor 2")

            if not self.shape_fant:

                layout.separator()

                split = layout.split()
                split.prop(self, "bevel_corners", text="Bevel Corners")
                col = split.column(align=True)

                if self.shape_rect:
                    col.prop(self, "bevel_corners_width", text="Width")
                else:
                    col.prop(self, "bevel_corners_percent", text="Width")

                col.prop(self, "bevel_corners_segments", text="Segments")
                col.prop(self, "bevel_corners_profile", text="Profile")

        if self.shape_rnd or self.cut in {"OVAL", "MARQUISE"}:

            layout.separator()

            split = layout.split()
            split.label("Detalization")
            split.prop(self, "detalization", text="")
