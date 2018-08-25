# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
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
from bpy.props import FloatProperty, BoolProperty
from bpy.app.translations import pgettext_iface as _
import bmesh
from mathutils import Matrix, Vector

from ..lib import asset, unit, mesh, ui_lib


class CURVE_OT_jewelcraft_size_curve_add(Operator):
    bl_label = "JewelCraft Make Size Curve"
    bl_description = "Create size curve"
    bl_idname = "curve.jewelcraft_size_curve_add"
    bl_options = {"REGISTER", "UNDO"}

    size = FloatProperty(name="Size", default=15.5, unit="LENGTH")
    up = BoolProperty(name="Start Up", default=True, description="Make curve start at the top", options={"SKIP_SAVE"})

    def execute(self, context):
        obs = context.selected_objects

        bpy.ops.curve.primitive_bezier_circle_add(radius=self.size / 2, rotation=(pi / 2, 0.0, 0.0))

        curve = context.active_object
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


class CURVE_OT_jewelcraft_length_display(Operator):
    bl_label = "JewelCraft Display Length"
    bl_description = "Display curve length"
    bl_idname = "curve.jewelcraft_length_display"

    def execute(self, context):
        ob = context.active_object

        if not ob or ob.type != "CURVE":
            self.report({"ERROR"}, "Active object must be a curve")
            return {"CANCELLED"}

        # Reset curve
        # ---------------------------

        settings = {"bevel_object": None, "bevel_depth": 0.0, "extrude": 0.0}

        for k, v in settings.items():
            x = getattr(ob.data, k)
            setattr(ob.data, k, v)
            settings[k] = x

        # Display length
        # ---------------------------

        length = unit.to_metric(mesh.curve_length(ob))
        lengthf = "{:.2f} {}".format(length, _("mm"))

        ui_lib.popup_report(self, lengthf, title=_("Curve Length"))

        # Restore curve
        # ---------------------------

        for k, v in settings.items():
            setattr(ob.data, k, v)

        return {"FINISHED"}


class OBJECT_OT_jewelcraft_stretch_along_curve(Operator):
    bl_label = "JewelCraft Stretch Along Curve"
    bl_description = "Stretch deformed objects along curve, also works in Edit Mode with selected vertices"
    bl_idname = "object.jewelcraft_stretch_along_curve"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        if context.mode == "EDIT_MESH":

            ob = context.edit_object
            me = ob.data
            bbox, curve = asset.mod_curve_off(ob)

            if curve:
                length = mesh.curve_length(curve)
                length_halved = length / 2 / ob.matrix_world.to_scale()[0]

                bm = bmesh.from_edit_mesh(me)

                for v in bm.verts:
                    if v.select:
                        coord = ob.matrix_local * v.co

                        if coord[0] > 0.0:
                            coord[0] = length_halved
                        else:
                            coord[0] = -length_halved

                        v.co = ob.matrix_local.inverted() * coord

                bm.normal_update()
                bmesh.update_edit_mesh(me)

        else:

            for ob in context.selected_objects:
                bbox, curve = asset.mod_curve_off(ob)

                if curve:
                    length = mesh.curve_length(curve)

                    bbox = [ob.matrix_world * Vector(x) for x in bbox]
                    dim = max(x[0] for x in bbox) - min(x[0] for x in bbox)

                    scaling = ob.matrix_local * ob.scale
                    scaling[0] = length / dim * scaling[0]

                    ob.scale = ob.matrix_local.inverted() * scaling

        return {"FINISHED"}


class OBJECT_OT_jewelcraft_move_over_under(Operator):
    bl_label = "JewelCraft Move Over/Under"
    bl_description = "Move deformed object over or under the curve"
    bl_idname = "object.jewelcraft_move_over_under"
    bl_options = {"REGISTER", "UNDO"}

    under = BoolProperty(name="Under", options={"SKIP_SAVE"})
    individual = BoolProperty(name="Individual", description="Move each object individually")

    def execute(self, context):
        if not self.individual or context.mode == "EDIT_MESH":

            ob = context.edit_object or context.active_object

            if not ob:
                return {"CANCELLED"}

            context.scene.update()
            bbox, curve = asset.mod_curve_off(ob)

            bbox = [ob.matrix_world * Vector(x) for x in ob.bound_box]

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

                bbox = [ob.matrix_local * Vector(x) for x in ob.bound_box]

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
