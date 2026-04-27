# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Artem Viveritsa
# SPDX-FileContributor: Modified by Mikhail Rachinskiy


def draw(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    layout.separator()

    if self.has_non_round_cuts:
        row = layout.row()
        row.alert = True
        row.alignment = "CENTER"
        row.label(text="May not work with non-round cuts", icon="ERROR")
        layout.separator()

    row = layout.row(heading="Move to Collection")
    row.prop(self, "use_coll_move", text="")
    sub = row.row()
    sub.enabled = self.use_coll_move
    sub.alert = self.use_coll_move and not self.collection_name
    sub.prop(self, "collection_name", text="")

    layout.separator()

    layout.label(text="Dimensions")
    col = layout.column()
    col.prop(self, "size_ratio")
    col.prop(self, "height_ratio")
    col.prop(self, "size_step")
    col.prop(self, "uniformity")

    layout.separator()

    layout.label(text="Position")
    col = layout.column()
    col.prop(self, "gap")
    col.prop(self, "max_gap")
    col.prop(self, "merge_distance")

    layout.separator()

    layout.label(text="Shape")
    col = layout.column()
    col.prop(self, "bump_scale")
    col.prop(self, "taper")
    col.prop(self, "detalization")
