# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from math import pi

import bpy
from bpy.types import Operator
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)
from bpy.app.translations import pgettext_iface as _
import bmesh
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
        ),
        update=set_ring_size,
    )

    size_us: FloatProperty(
        name="Size",
        default=4.5,
        min=0.0,
        step=50,
        precision=1,
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


class CURVE_OT_length_display(Operator):
    bl_label = "Curve Length"
    bl_description = "Display curve length"
    bl_idname = "curve.jewelcraft_length_display"

    def execute(self, context):
        from ..lib import mesh, ui_lib

        ob = context.object

        if not ob or ob.type != "CURVE":
            self.report({"ERROR"}, "Active object must be a curve")
            return {"CANCELLED"}

        length = unit.Scale().from_scene(mesh.est_curve_length(ob))
        report = f"{length:.2f} {_('mm')}"

        ui_lib.popup_list(self, _("Curve Length"), (report,))

        return {"FINISHED"}


class OBJECT_OT_stretch_along_curve(Operator):
    bl_label = "Stretch Along Curve"
    bl_description = (
        "Stretch deformed objects along curve on X axis, "
        "also works in Edit Mode with selected vertices"
    )
    bl_idname = "object.jewelcraft_stretch_along_curve"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..lib import asset, mesh

        if context.mode == "EDIT_MESH":

            for ob in context.objects_in_mode:
                me = ob.data
                curve = asset.mod_curve_off(ob)

                if not curve:
                    continue

                length = mesh.est_curve_length(curve)
                length_halved = length / 2 / ob.matrix_world.to_scale()[0]

                bm = bmesh.from_edit_mesh(me)
                for v in bm.verts:
                    if v.select:
                        if v.co.x > 0.0:
                            v.co.x = length_halved
                        else:
                            v.co.x = -length_halved
                bm.normal_update()
                bmesh.update_edit_mesh(me)

        else:

            for ob in context.selected_objects:
                curve, bbox = asset.mod_curve_off(ob, ob.matrix_world)

                if not curve:
                    continue

                length = mesh.est_curve_length(curve)
                dim = max(x[0] for x in bbox) - min(x[0] for x in bbox)
                ob.scale.x = length / dim * ob.scale.x

        return {"FINISHED"}


class OBJECT_OT_move_over_under(Operator):
    bl_label = "Move Over/Under"
    bl_description = "Move deformed object over or under the curve"
    bl_idname = "object.jewelcraft_move_over_under"
    bl_options = {"REGISTER", "UNDO"}

    under: BoolProperty(name="Under", options={"SKIP_SAVE"})
    individual: BoolProperty(name="Individual", description="Move each object individually")

    def execute(self, context):
        from ..lib import asset

        if not self.individual or context.mode == "EDIT_MESH":

            ob = context.edit_object or context.object

            if not ob:
                return {"CANCELLED"}

            context.view_layer.update()
            curve, bbox = asset.mod_curve_off(ob, ob.matrix_world)

            if self.under:
                z_object = max(x[2] for x in bbox)
            else:
                z_object = min(x[2] for x in bbox)

            if curve:
                z_pivot = curve.matrix_world.translation[2]
            else:
                z_pivot = 0.0

            vec = (0.0, 0.0, z_pivot - z_object)

            bpy.ops.transform.translate(value=vec)

        else:

            for ob in context.selected_objects:
                curve, bbox = asset.mod_curve_off(ob, ob.matrix_local)

                if self.under:
                    z_object = max(x[2] for x in bbox)
                else:
                    z_object = min(x[2] for x in bbox)

                if curve:
                    z_pivot = curve.location.z
                else:
                    z_pivot = 0.0

                ob.location.z += z_pivot - z_object

        return {"FINISHED"}
