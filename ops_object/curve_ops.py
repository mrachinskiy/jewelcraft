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
from mathutils import Matrix, Vector

from .. import var
from ..lib import (
    asset,
    unit,
    mesh,
    ui_lib,
    dynamic_list,
)


def upd_size(self, context):
    if self.size_format == "CH":
        cir = self.size_float + 40.0

    elif self.size_format == "UK":
        size = float(self.size_abc)

        if self.use_half_size:
            size += 0.5

        cir = var.CIR_BASE_UK + var.CIR_STEP_UK * size

    elif self.size_format in {"US", "JP"}:
        size = self.size_float

        if self.size_format == "JP":
            size = var.MAP_SIZE_JP_TO_US[self.size_int - 1]

        cir = var.CIR_BASE_US + var.CIR_STEP_US * size

    self.circumference = unit.Scale(context).to_scene(round(cir, 4))


def upd_diameter(self, context):
    if self.use_unit_conversion:
        self["circumference"] = self.diameter * pi
    else:
        self["circumference"] = round(self.diameter * pi, 4)


def upd_circumference(self, context):
    if self.use_unit_conversion:
        self["diameter"] = self.circumference / pi
    else:
        self["diameter"] = round(self.circumference / pi, 2)


class CURVE_OT_size_curve_add(Operator):
    bl_label = "JewelCraft Make Size Curve"
    bl_description = "Create size curve"
    bl_idname = "curve.jewelcraft_size_curve_add"
    bl_options = {"REGISTER", "UNDO"}

    size_format: EnumProperty(
        name="Format",
        items=(
            ("US", "USA", ""),
            ("UK", "Britain", ""),
            ("CH", "Swiss", ""),
            ("JP", "Japan", ""),
        ),
        update=upd_size,
    )
    size_abc: EnumProperty(
        name="Size",
        items=dynamic_list.abc,
        update=upd_size,
    )
    size_int: IntProperty(
        name="Size",
        default=8,
        min=1,
        max=27,
        update=upd_size,
    )
    size_float: FloatProperty(
        name="Size",
        default=4.5,
        min=0.0,
        step=50,
        precision=1,
        update=upd_size,
    )
    diameter: FloatProperty(
        name="Diameter",
        default=15.28,
        min=0.001,
        step=10,
        unit="LENGTH",
        update=upd_diameter,
    )
    circumference: FloatProperty(
        name="Circumference",
        default=48.0,
        min=0.001,
        step=100,
        precision=1,
        unit="LENGTH",
        update=upd_circumference,
    )
    up: BoolProperty(
        name="Start Up",
        description="Make curve start at the top",
        default=True,
        options={"SKIP_SAVE"},
    )
    use_size: BoolProperty(
        name="Ring Size",
        update=upd_size,
    )
    use_half_size: BoolProperty(
        name="1/2",
        update=upd_size,
    )
    use_unit_conversion: BoolProperty(options={"HIDDEN", "SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        col = layout.column()
        col.use_property_split = False
        col.prop(self, "use_size")

        col = layout.column()
        col.active = self.use_size
        col.prop(self, "size_format")

        if self.size_format == "UK":
            row = col.row(align=True)
            row.prop(self, "size_abc")
            row.prop(self, "use_half_size")
        elif self.size_format == "JP":
            col.prop(self, "size_int")
        else:
            col.prop(self, "size_float")

        layout.separator()

        layout.label(text="Curve")

        col = layout.column()
        col.active = not self.use_size
        col.prop(self, "diameter")
        col.prop(self, "circumference")

        layout.prop(self, "up")

        layout.separator()

    def execute(self, context):
        obs = context.selected_objects

        bpy.ops.curve.primitive_bezier_circle_add(radius=self.diameter / 2, rotation=(pi / 2, 0.0, 0.0))

        curve = context.object
        curve.name = "Size"
        curve.data.name = "Size"
        curve.data.resolution_u = 512
        curve.data.use_radius = False

        if self.up:
            mat = Matrix.Rotation(pi, 4, "Z")
            curve.data.transform(mat)

        if obs:
            for ob in obs:
                md = ob.modifiers.new("Curve", "CURVE")
                md.object = curve

        return {"FINISHED"}

    def invoke(self, context, event):
        self.use_unit_conversion = unit.Scale(context).use_conversion

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class CURVE_OT_length_display(Operator):
    bl_label = "JewelCraft Display Length"
    bl_description = "Display curve length"
    bl_idname = "curve.jewelcraft_length_display"

    def execute(self, context):
        ob = context.object

        if not ob or ob.type != "CURVE":
            self.report({"ERROR"}, "Active object must be a curve")
            return {"CANCELLED"}

        # Reset curve
        # ---------------------------

        settings = {
            "bevel_object": None,
            "bevel_depth": 0.0,
            "extrude": 0.0,
        }

        for k, v in settings.items():
            x = getattr(ob.data, k)
            setattr(ob.data, k, v)
            settings[k] = x

        # Display length
        # ---------------------------

        length = unit.Scale(context).from_scene(mesh.curve_length(ob))
        lengthf = "{:.2f} {}".format(length, _("mm"))

        ui_lib.popup_report(self, context, text=lengthf, title=_("Curve Length"))

        # Restore curve
        # ---------------------------

        for k, v in settings.items():
            setattr(ob.data, k, v)

        return {"FINISHED"}


class OBJECT_OT_stretch_along_curve(Operator):
    bl_label = "JewelCraft Stretch Along Curve"
    bl_description = (
        "Stretch deformed objects along curve on X axis, "
        "also works in Edit Mode with selected vertices"
    )
    bl_idname = "object.jewelcraft_stretch_along_curve"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        if context.mode == "EDIT_MESH":

            for ob in context.objects_in_mode:
                me = ob.data
                bbox, curve = asset.mod_curve_off(ob)

                if curve:
                    length = mesh.curve_length(curve)
                    length_halved = length / 2 / ob.matrix_world.to_scale()[0]

                    bm = bmesh.from_edit_mesh(me)

                    for v in bm.verts:
                        if v.select:
                            if v.co[0] > 0.0:
                                v.co[0] = length_halved
                            else:
                                v.co[0] = -length_halved

                    bm.normal_update()
                    bmesh.update_edit_mesh(me)

        else:

            for ob in context.selected_objects:
                bbox, curve = asset.mod_curve_off(ob)

                if curve:
                    length = mesh.curve_length(curve)

                    bbox = [ob.matrix_world @ Vector(x) for x in bbox]
                    dim = max(x[0] for x in bbox) - min(x[0] for x in bbox)

                    scaling = ob.matrix_local @ ob.scale
                    scaling[0] = length / dim * scaling[0]

                    ob.scale = ob.matrix_local.inverted() @ scaling

        return {"FINISHED"}


class OBJECT_OT_move_over_under(Operator):
    bl_label = "JewelCraft Move Over/Under"
    bl_description = "Move deformed object over or under the curve"
    bl_idname = "object.jewelcraft_move_over_under"
    bl_options = {"REGISTER", "UNDO"}

    under: BoolProperty(name="Under", options={"SKIP_SAVE"})
    individual: BoolProperty(name="Individual", description="Move each object individually")

    def execute(self, context):
        if not self.individual or context.mode == "EDIT_MESH":

            ob = context.edit_object or context.object

            if not ob:
                return {"CANCELLED"}

            context.view_layer.update()
            bbox, curve = asset.mod_curve_off(ob)
            bbox = [ob.matrix_world @ Vector(x) for x in bbox]

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
                bbox, curve = asset.mod_curve_off(ob)
                bbox = [ob.matrix_local @ Vector(x) for x in bbox]

                if self.under:
                    z_object = max(x[2] for x in bbox)
                else:
                    z_object = min(x[2] for x in bbox)

                if curve:
                    z_pivot = curve.location[2]
                else:
                    z_pivot = 0.0

                ob.location[2] += z_pivot - z_object

        return {"FINISHED"}
