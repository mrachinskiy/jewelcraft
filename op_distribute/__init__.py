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
from bpy.props import FloatProperty, BoolProperty


class Distribute:

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sizes = context.window_manager.jewelcraft.sizes

        layout.separator()

        row = layout.row()
        row.template_list(
            "VIEW3D_UL_jewelcraft_sizes",
            "",
            sizes,
            "coll",
            sizes,
            "index",
            rows=4,
        )

        col = row.column(align=True)
        col.operator("wm.jewelcraft_ul_add", text="", icon="ADD").prop = "sizes"
        col.operator("wm.jewelcraft_ul_del", text="", icon="REMOVE").prop = "sizes"
        col.separator()
        col.operator("wm.jewelcraft_ul_clear", text="", icon="X").prop = "sizes"
        col.separator()
        op = col.operator("wm.jewelcraft_ul_move", text="", icon="TRIA_UP")
        op.prop = "sizes"
        op.move_up = True
        col.operator("wm.jewelcraft_ul_move", text="", icon="TRIA_DOWN").prop = "sizes"

        layout.separator()

        layout.label(text="Transforms")
        col = layout.column(align=True)
        col.prop(self, "rot_x")
        col.prop(self, "rot_z")
        col.prop(self, "loc_z")

        layout.separator()

        layout.label(text="Distribution (%)")
        col = layout.column(align=True)
        col.prop(self, "start")
        sub = col.column(align=True)
        sub.active = not self.use_absolute_offset
        sub.prop(self, "end")

        layout.separator()

        row = layout.row(heading="Absolute Offset")
        row.prop(self, "use_absolute_offset", text="")
        sub = row.row()
        sub.active = self.use_absolute_offset
        sub.prop(self, "spacing", text="")

    def execute(self, context):
        from . import distribute_func
        return distribute_func.execute(self, context)

    def invoke(self, context, event):
        from . import distribute_func
        return distribute_func.invoke(self, context, event)


class OBJECT_OT_curve_distribute(Distribute, Operator):
    bl_label = "Distribute on Curve"
    bl_description = (
        "Distribute selected object along active curve\n"
        "(Shortcut: hold Ctrl when using the tool to avoid properties reset)"
    )
    bl_idname = "object.jewelcraft_curve_distribute"
    bl_options = {"REGISTER", "UNDO"}

    is_distribute = True

    rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION")
    rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION")
    loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH")

    start: FloatProperty(name="Start", step=5)
    end: FloatProperty(name="End", default=100.0, step=5)

    use_absolute_offset: BoolProperty(name="Absolute Offset")
    spacing: FloatProperty(name="Spacing", default=0.2, step=1, unit="LENGTH")


class OBJECT_OT_curve_redistribute(Distribute, Operator):
    bl_label = "Redistribute"
    bl_description = "Redistribute selected objects along curve"
    bl_idname = "object.jewelcraft_curve_redistribute"
    bl_options = {"REGISTER", "UNDO"}

    is_distribute = False

    rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION", options={"SKIP_SAVE"})
    rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION", options={"SKIP_SAVE"})
    loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH", options={"SKIP_SAVE"})

    start: FloatProperty(name="Start", step=5, options={"SKIP_SAVE"})
    end: FloatProperty(name="End", default=100.0, step=5, options={"SKIP_SAVE"})

    use_absolute_offset: BoolProperty(name="Absolute Offset", options={"SKIP_SAVE"})
    spacing: FloatProperty(name="Spacing", default=0.2, step=1, unit="LENGTH", options={"SKIP_SAVE"})
