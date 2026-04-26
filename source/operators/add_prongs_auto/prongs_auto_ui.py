# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


def draw(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    layout.separator()

    if self.has_non_round_cuts:
        row = layout.row()
        row.alert = True
        row.alignment = "RIGHT"
        row.label(text="This tool is optimized for round cuts", icon="INFO")
        layout.separator()

    col = layout.column()
    col.prop_search(self, "collection_name", context.blend_data, "collections")

    row = layout.row()
    row.alignment = "RIGHT"
    row.label(text="If the collection does not exist, it will be created", icon="INFO")

    layout.separator()

    layout.label(text="Dimensions")
    col = layout.column()
    col.prop(self, "size_ratio")
    col.prop(self, "height_ratio")
    col.prop(self, "uniformity")

    layout.separator()

    layout.label(text="Connections")
    col = layout.column()
    col.prop(self, "width_between_prongs")
    col.prop(self, "max_gap")
    col.prop(self, "weld_distance")

    layout.separator()

    layout.label(text="Shape")
    col = layout.column()
    col.prop(self, "size_round")
    col.prop(self, "bump_scale")
    col.prop(self, "taper")
    col.prop(self, "detalization")
