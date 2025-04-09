# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


def draw(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    layout.separator()

    layout.prop(self, "number")

    layout.separator()

    layout.label(text="Dimensions")

    col = layout.column()
    col.prop(self, "z1")
    col.prop(self, "diameter")
    col.prop(self, "z2")

    layout.separator()

    col = layout.column()
    col.label(text="Position")
    col.prop(self, "position")
    col.prop(self, "intersection")
    col.prop(self, "alignment")
    row = col.row(heading="Symmetry")
    row.prop(self, "use_symmetry", text="")
    sub = row.row()
    sub.enabled = self.use_symmetry
    sub.prop(self, "symmetry_pivot", text="")

    layout.separator()

    layout.label(text="Shape")

    col = layout.column()
    col.prop(self, "bump_scale")
    col.prop(self, "taper")
    col.prop(self, "detalization")
