# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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
from bpy.props import FloatProperty


class OBJECT_OT_microprong_cutter_add(Operator):
    bl_label = "Add Microprong Cutter"
    bl_description = "Create microprong cutter between selected gems"
    bl_idname = "object.jewelcraft_microprong_cutter_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    dim_x: FloatProperty(name="Width", default=0.3, min=0.0, step=1, unit="LENGTH")
    dim_y: FloatProperty(name="Length", default=2.0, min=0.0, step=1, unit="LENGTH")

    handle_z: FloatProperty(name="Handle", default=0.5, min=0.0, step=1, unit="LENGTH")
    keel_z: FloatProperty(name="Keel", default=0.3, min=0.0, step=1, unit="LENGTH")

    rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION")
    rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION")
    loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.label(text="Dimensions")
        col = layout.column(align=True)
        col.prop(self, "dim_x")
        col.prop(self, "dim_y")
        col.separator()
        col.prop(self, "handle_z")
        col.prop(self, "keel_z")

        layout.label(text="Transforms")
        col = layout.column(align=True)
        col.prop(self, "rot_x")
        col.prop(self, "rot_z")
        col.prop(self, "loc_z")

    def execute(self, context):
        from . import microprong_func
        return microprong_func.execute(self, context)

    def invoke(self, context, event):
        from . import microprong_func
        return microprong_func.invoke(self, context, event)
