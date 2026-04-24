# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


def draw(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    layout.separator()

    if self.selected_gem_count < 2:
        row = layout.row()
        row.alert = True
        row.alignment = "RIGHT"
        row.label(text="At least two gem objects must be selected", icon="ERROR")
        layout.separator()

    col = layout.column()
    col.prop_search(self, "collection_name", context.blend_data, "collections")

    if not self.collection_name:
        row = layout.row()
        row.alignment = "RIGHT"
        row.label(text="If empty, a new 'Prongs' collection will be created", icon="INFO")

    layout.separator()

    layout.label(text="Dimensions")
    col = layout.column()
    col.prop(self, "size_ratio")
    col.prop(self, "height_ratio")
    col.prop(self, "width_between_prongs")
    col.prop(self, "uniformity")

    layout.separator()

    layout.label(text="Connections")
    col = layout.column()
    col.prop(self, "max_gap")
    col.prop(self, "weld_distance")

    layout.separator()

    layout.label(text="Shape")
    col = layout.column()
    col.prop(self, "size_round")
    col.prop(self, "bump_scale")
    col.prop(self, "taper")
    col.prop(self, "detalization")
    