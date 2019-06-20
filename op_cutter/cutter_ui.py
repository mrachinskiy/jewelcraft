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

        # Handle
        # ------------------------

        layout.separator()

        row = layout.row()
        row.use_property_split = False
        row.prop(self, "use_handle")

        col = layout.column()
        col.enabled = self.use_handle
        col.prop(self, "handle_z_top")

        if self.shape_rnd or self.shape_sq:
            col.prop(self, "handle_l_size", text="Size")
        else:
            col.prop(self, "handle_l_size")
            col.prop(self, "handle_w_size")

        col.prop(self, "handle_z_btm")

        # Girdle
        # ------------------------

        layout.separator()

        layout.label(text="Girdle")

        col = layout.column()
        col.prop(self, "girdle_z_top", text="Top" if self.use_handle else "Table")

        if self.shape_tri or self.cut == "HEART":
            col.prop(self, "girdle_l_ofst")
            col.prop(self, "girdle_w_ofst")
        else:
            col.prop(self, "girdle_l_ofst", text="Size Offset")

        col.prop(self, "girdle_z_btm")

        # Hole
        # ------------------------

        layout.separator()

        row = layout.row()
        row.use_property_split = False
        row.prop(self, "use_hole")

        col = layout.column()
        col.prop(self, "hole_z_top", text="Top" if self.use_hole else "Culet")

        sub = col.column()
        sub.enabled = self.use_hole

        if self.shape_rnd or self.shape_sq:
            sub.prop(self, "hole_l_size", text="Size")
        else:
            sub.prop(self, "hole_l_size")
            sub.prop(self, "hole_w_size")

        sub.prop(self, "hole_z_btm")

        if self.shape_fant and self.cut in {"PEAR", "HEART"}:
            sub.prop(self, "hole_pos_ofst")

        if not self.shape_rnd:

            # Curve Seat
            # ------------------------

            layout.separator()

            row = layout.row()
            row.use_property_split = False
            row.prop(self, "use_curve_seat")

            col = layout.column()
            col.enabled = self.use_curve_seat
            col.prop(self, "curve_seat_segments")
            col.prop(self, "curve_seat_profile")

            if self.shape_tri:

                # Curve Profile
                # ------------------------

                layout.separator()

                row = layout.row()
                row.use_property_split = False
                row.prop(self, "use_curve_profile")

                col = layout.column()
                col.enabled = self.use_curve_profile
                col.prop(self, "curve_profile_segments")
                col.prop(self, "curve_profile_factor")

            elif self.cut in {"MARQUISE", "PEAR", "HEART"}:

                # Marquise Profile
                # ------------------------

                layout.separator()

                layout.label(text="Profile")

                col = layout.column()
                col.prop(self, "mul_1")
                col.prop(self, "mul_2")

            if not self.shape_fant:

                # Bevel Corners
                # ------------------------

                layout.separator()

                row = layout.row()
                row.use_property_split = False
                row.prop(self, "use_bevel_corners")

                col = layout.column()
                col.enabled = self.use_bevel_corners

                if self.shape_rect:
                    col.prop(self, "bevel_corners_width")
                else:
                    col.prop(self, "bevel_corners_percent")

                col.prop(self, "bevel_corners_segments")
                col.prop(self, "bevel_corners_profile")

        if self.shape_rnd or self.cut in {"OVAL", "MARQUISE", "PEAR", "HEART"}:

            layout.separator()
            layout.prop(self, "detalization")
