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
    col.prop(self.handle_dim, "z1")

    if self.shape_rnd or self.shape_sq:
        col.prop(self.handle_dim, "y", text="Size")
    else:
        col.prop(self.handle_dim, "y")
        col.prop(self.handle_dim, "x")

    col.prop(self.handle_dim, "z2")

    if self.shape_fant and self.cut in {"PEAR", "HEART"}:
        col.prop(self, "handle_shift")

    # Girdle
    # ------------------------

    layout.separator()

    layout.label(text="Girdle")

    col = layout.column()
    col.prop(self.girdle_dim, "z1", text="Top" if self.use_handle else "Table")

    if self.shape_tri or self.cut == "HEART":
        col.prop(self.girdle_dim, "y", text="Length Offset")
        col.prop(self.girdle_dim, "x", text="Width Offset")
    else:
        col.prop(self.girdle_dim, "y", text="Size Offset")

    col.prop(self.girdle_dim, "z2")

    # Hole
    # ------------------------

    layout.separator()

    row = layout.row()
    row.use_property_split = False
    row.prop(self, "use_hole")

    show_culet_size = not self.use_hole and self.shape_rect

    col = layout.column()
    col.prop(self.hole_dim, "z1", text="Top" if self.use_hole else "Culet")
    if show_culet_size:
        col.prop(self.hole_dim, "y")

    sub = col.column()
    sub.enabled = self.use_hole

    if self.shape_rnd or self.shape_sq:
        sub.prop(self.hole_dim, "y", text="Size")
    else:
        if not show_culet_size:
            sub.prop(self.hole_dim, "y")
        sub.prop(self.hole_dim, "x")

    sub.prop(self.hole_dim, "z2")

    if self.cut in {"PEAR", "HEART"}:
        col = layout.column()
        col.enabled = self.cut == "PEAR"
        col.prop(self, "hole_shift")

    # Curve seat
    # ------------------------

    layout.separator()

    row = layout.row()
    row.use_property_split = False
    row.prop(self, "use_curve_seat")

    col = layout.column()
    col.enabled = self.use_curve_seat
    col.prop(self, "curve_seat_profile")
    col.prop(self, "curve_seat_segments")

    if not self.shape_rnd:

        if self.shape_tri:

            # Curve profile
            # ------------------------

            layout.separator()

            layout.label(text="Curve Profile")

            col = layout.column()
            col.prop(self, "curve_profile_factor")
            sub = col.column()
            sub.enabled = self.curve_profile_factor != 0.0
            sub.prop(self, "curve_profile_segments")

        elif self.cut in {"MARQUISE", "PEAR", "HEART"}:

            # Profile settings
            # ------------------------

            layout.separator()

            layout.label(text="Profile")

            col = layout.column()
            col.prop(self, "mul_1")
            col.prop(self, "mul_2")
            if self.cut == "HEART":
                col.prop(self, "mul_3")

        if not self.shape_fant:

            # Bevel corners
            # ------------------------

            if self.shape_rect:
                bevel_width = "bevel_corners_width"
            else:
                bevel_width = "bevel_corners_percent"

            layout.separator()

            layout.label(text="Bevel Corners")

            col = layout.column()
            col.prop(self, bevel_width)
            sub = col.column()
            sub.enabled = getattr(self, bevel_width) != 0.0
            sub.prop(self, "bevel_corners_segments")
            sub.prop(self, "bevel_corners_profile")

    if self.shape_rnd or self.shape_fant:

        layout.separator()
        layout.prop(self, "detalization")
