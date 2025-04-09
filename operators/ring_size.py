# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from math import pi

import bpy
from bpy.app.translations import pgettext_iface as _
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import Operator
from mathutils import Matrix

from ..lib import dynamic_list, unit


def set_diameter(self, context):
    self["diameter"] = round(self.circumference / pi, self.diameter_precision)


def set_ring_size(self, context):
    from ..lib import ringsizelib

    cir = unit.Scale().from_scene(self.circumference)
    size = ringsizelib.to_size(cir, self.size_format)

    self.warn_no_size = size is None
    if self.warn_no_size:
        return

    if self.size_format == "UK":
        self["size_uk"], self["use_half_size"] = size
    else:
        self["size_" + self.size_format.lower()] = size


def upd_size(self, context):
    from ..lib import ringsizelib

    if self.size_format == "UK":
        size = float(self.size_uk)
        if self.use_half_size:
            size += 0.5
    else:
        size = self["size_" + self.size_format.lower()]

    cir = ringsizelib.to_cir(size, self.size_format)

    self["circumference"] = unit.Scale().to_scene(cir)
    set_diameter(self, context)


def upd_diameter(self, context):
    self["circumference"] = self.diameter * pi
    set_ring_size(self, context)


def upd_circumference(self, context):
    set_diameter(self, context)
    set_ring_size(self, context)


class CURVE_OT_size_curve_add(Operator):
    bl_label = "Add Size Curve"
    bl_description = "Create size curve"
    bl_idname = "curve.jewelcraft_size_curve_add"
    bl_options = {"REGISTER", "UNDO"}

    size_format: EnumProperty(
        name="Format",
        description="Ring size format",
        items=(
            ("US", "USA", ""),
            ("UK", "Britain", ""),
            ("CH", "Swiss", ""),
            ("JP", "Japan", ""),
            ("HK", "Hong Kong", ""),
        ),
        update=set_ring_size,
    )

    size_us: FloatProperty(
        name="Size",
        default=4.5,
        min=0.0,
        step=50,
        precision=2,
        update=upd_size,
    )
    size_ch: FloatProperty(
        name="Size",
        default=8.0,
        min=0.0,
        step=100,
        precision=2,
        update=upd_size,
    )
    size_jp: IntProperty(
        name="Size",
        default=8,
        min=1,
        max=27,
        update=upd_size,
    )
    size_hk: IntProperty(
        name="Size",
        default=10,
        min=5,
        max=30,
        update=upd_size,
    )
    size_uk: EnumProperty(
        name="Size",
        items=dynamic_list.abc,
        update=upd_size,
    )
    use_half_size: BoolProperty(
        name="1/2",
        update=upd_size,
    )

    diameter: FloatProperty(
        name="Diameter",
        default=15.29,
        min=0.001,
        step=10,
        unit="LENGTH",
        update=upd_diameter,
    )
    circumference: FloatProperty(
        name="Circumference",
        default=48.035,
        min=0.001,
        step=100,
        precision=1,
        unit="LENGTH",
        update=upd_circumference,
    )

    curve_start_pos: EnumProperty(
        name="Start",
        description="Curve start position",
        items=(
            ("TOP", "Top", ""),
            ("BOTTOM", "Bottom", ""),
        ),
        options={"SKIP_SAVE"},
    )

    diameter_precision: IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    warn_no_size: BoolProperty(options={"HIDDEN"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        col = layout.column()
        col.prop(self, "size_format")

        if self.warn_no_size:
            row = col.row()
            row.alert = True
            row.alignment = "RIGHT"
            row.label(text="No corresponding size", icon="ERROR")
        else:
            if self.size_format == "UK":
                row = col.row()
                row.prop(self, "size_uk")
                row.separator()
                row.prop(self, "use_half_size")
            else:
                col.prop(self, "size_" + self.size_format.lower())

        layout.separator()

        col = layout.column()
        col.prop(self, "diameter")
        col.prop(self, "circumference")

        layout.separator()

        layout.row().prop(self, "curve_start_pos", expand=True)

        layout.separator()

    def execute(self, context):
        obs = context.selected_objects

        bpy.ops.curve.primitive_bezier_circle_add(radius=self.diameter / 2, rotation=(pi / 2, 0.0, 0.0))

        curve = context.object
        curve.name = "Size"
        curve.data.name = "Size"
        curve.data.resolution_u = 512
        curve.data.use_radius = False

        if self.curve_start_pos == "TOP":
            mat = Matrix.Rotation(pi, 4, "Z")
            curve.data.transform(mat)

        if obs:
            for ob in obs:
                try:
                    md = ob.modifiers.new("Curve", "CURVE")
                    md.object = curve
                except AttributeError:
                    continue

        return {"FINISHED"}

    def invoke(self, context, event):
        self.diameter_precision = 5 if unit.check() is unit.WARN_SCALE else 2

        wm = context.window_manager
        return wm.invoke_props_dialog(self)
