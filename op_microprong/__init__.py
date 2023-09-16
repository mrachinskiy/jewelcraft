# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty


class OBJECT_OT_microprong_cutter_add(Operator):
    bl_label = "Add Microprong Cutter"
    bl_description = "Create microprong cutter between selected gems"
    bl_idname = "object.jewelcraft_microprong_cutter_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    use_between: BoolProperty(name="Between", default=True)
    use_side: BoolProperty(name="Side", default=True)

    between_x: FloatProperty(name="Width", default=0.3, min=0.0, step=1, unit="LENGTH")
    between_y: FloatProperty(name="Length", default=2.0, min=0.0, step=1, unit="LENGTH")
    between_z1: FloatProperty(name="Handle", default=0.5, min=0.0, step=1, unit="LENGTH")
    between_z2: FloatProperty(name="Wedge", default=0.3, min=0.0, step=1, unit="LENGTH")

    between_rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION")
    between_rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION")
    between_loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH")

    side_x: FloatProperty(name="Width", default=0.5, min=0.0, step=1, unit="LENGTH")
    side_y: FloatProperty(name="Length", default=2.0, min=0.0, step=1, unit="LENGTH")
    side_z1: FloatProperty(name="Handle", default=0.5, min=0.0, step=1, unit="LENGTH")
    side_z2: FloatProperty(name="Wedge", default=0.0, step=1, unit="LENGTH")

    side_rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION")
    side_rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION")
    side_loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH")

    bevel_top: FloatProperty(
        name="Top",
        min=0.0,
        max=50.0,
        precision=0,
        subtype="PERCENTAGE",
    )
    bevel_btm: FloatProperty(
        name="Bottom",
        default=50.0,
        min=0.0,
        max=50.0,
        precision=0,
        subtype="PERCENTAGE",
    )
    bevel_wedge: FloatProperty(
        name="Wedge",
        min=0.0,
        max=100.0,
        precision=0,
        subtype="PERCENTAGE",
    )
    bevel_segments: IntProperty(
        name="Segments",
        default=10,
        min=1,
        soft_max=30,
        step=1,
    )
    size_active: FloatProperty(options={"HIDDEN", "SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        row = layout.row()
        row.enabled = self.is_ob_multiple
        row.use_property_split = False
        row.prop(self, "use_between")

        if not self.is_ob_multiple:
            row = layout.row()
            row.alert = True
            row.alignment = "RIGHT"
            row.label(text="At least two objects must be selected", icon="ERROR")

        col = layout.column(align=True)
        col.enabled = self.use_between and self.is_ob_multiple
        col.prop(self, "between_x")
        col.prop(self, "between_y")
        col.separator()
        col.prop(self, "between_z1")
        col.prop(self, "between_z2")

        col = layout.column(align=True)
        col.enabled = self.use_between and self.is_ob_multiple
        col.label(text="Transforms")
        col.prop(self, "between_rot_x")
        col.prop(self, "between_rot_z")
        col.prop(self, "between_loc_z")

        layout.separator()

        row = layout.row()
        row.use_property_split = False
        row.prop(self, "use_side")

        col = layout.column(align=True)
        col.enabled = self.use_side
        col.prop(self, "side_x")
        col.prop(self, "side_y")
        col.separator()
        col.prop(self, "side_z1")
        col.prop(self, "side_z2")

        col = layout.column(align=True)
        col.enabled = self.use_side
        col.label(text="Bevel")
        col.prop(self, "bevel_top")
        col.prop(self, "bevel_btm")
        col.prop(self, "bevel_wedge")
        col.separator()
        col.prop(self, "bevel_segments")

        col = layout.column(align=True)
        col.enabled = self.use_side
        col.label(text="Transforms")
        col.prop(self, "side_rot_x")
        col.prop(self, "side_rot_z")
        col.prop(self, "side_loc_z")

    def execute(self, context):
        if self.use_between and self.is_ob_multiple:
            from . import microprong_between
            microprong_between.add(self, context)

        if self.use_side:
            from . import microprong_side
            microprong_side.add(self, context)

        return {"FINISHED"}

    def invoke(self, context, event):
        from .. import var
        from ..lib import mesh

        curve = None
        obs_count = 0

        for ob in context.selected_objects:

            if obs_count == 2:
                break

            for con in ob.constraints:
                if con.type == "FOLLOW_PATH":
                    curve = con.target
                    obs_count += 1
                    break

        if not curve:
            self.report({"ERROR"}, "Selected objects do not have Follow Path constraint")
            return {"CANCELLED"}

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_cutter
        self.curve_length = mesh.est_curve_length(curve)
        self.is_ob_multiple = obs_count > 1

        active = ob

        if context.object is not None:
            for con in context.object.constraints:
                if con.type == "FOLLOW_PATH":
                    active = context.object
                    break

        self.size_active = active.dimensions.y
        self.side_x = self.size_active * 0.5

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)
