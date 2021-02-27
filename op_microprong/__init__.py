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


from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, EnumProperty


def upd_cutter_type(self, context):
    if self.cutter_type == "SIDE":
        self.dim_x = self.size_active * 0.5


class OBJECT_OT_microprong_cutter_add(Operator):
    bl_label = "Add Microprong Cutter"
    bl_description = "Create microprong cutter between selected gems"
    bl_idname = "object.jewelcraft_microprong_cutter_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    cutter_type: EnumProperty(
        name="Type",
        items=(
            ("BETWEEN", "Between", ""),
            ("SIDE", "Side", ""),
        ),
        update=upd_cutter_type,
    )

    dim_x: FloatProperty(name="Width", default=0.3, min=0.0, step=1, unit="LENGTH")
    dim_y: FloatProperty(name="Length", default=2.0, min=0.0, step=1, unit="LENGTH")

    handle_z: FloatProperty(name="Handle", default=0.5, min=0.0, step=1, unit="LENGTH")
    wedge_z: FloatProperty(name="Wedge", default=0.3, min=0.0, step=1, unit="LENGTH")

    rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION")
    rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION")
    loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH")

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

        layout.prop(self, "cutter_type")

        layout.separator()

        layout.label(text="Dimensions")
        col = layout.column(align=True)
        col.prop(self, "dim_x")
        col.prop(self, "dim_y")
        col.separator()
        col.prop(self, "handle_z")

        if self.cutter_type == "BETWEEN":
            col.prop(self, "wedge_z")
        else:
            layout.label(text="Bevel")
            col = layout.column(align=True)
            col.prop(self, "bevel_top")
            col.prop(self, "bevel_btm")
            col.separator()
            col.prop(self, "bevel_segments")

        layout.label(text="Transforms")
        col = layout.column(align=True)
        col.prop(self, "rot_x")
        col.prop(self, "rot_z")
        col.prop(self, "loc_z")

    def execute(self, context):
        if self.cutter_type == "BETWEEN":
            from . import microprong_between
            return microprong_between.execute(self, context)

        from . import microprong_side
        return microprong_side.execute(self, context)

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

        if obs_count < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_cutter
        self.curve_length = mesh.est_curve_length(curve)

        active = context.object

        for con in active.constraints:
            if con.type == "FOLLOW_PATH":
                break
        else:
            active = ob

        self.size_active = active.dimensions.y
        upd_cutter_type(self, context)

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)
