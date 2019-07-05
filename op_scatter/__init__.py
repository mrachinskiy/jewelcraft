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


from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty

from .scatter_ui import UI
from .scatter_func import Scatter


class OBJECT_OT_curve_scatter(UI, Scatter, Operator):
    bl_label = "JewelCraft Curve Scatter"
    bl_description = "Scatter selected object along active curve"
    bl_idname = "object.jewelcraft_curve_scatter"
    bl_options = {"REGISTER", "UNDO"}

    is_scatter = True

    number: IntProperty(name="Objects", default=10, min=1, soft_max=100)

    rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION")
    rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION")
    loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH")

    start: FloatProperty(name="Start", step=5)
    end: FloatProperty(name="End", default=100.0, step=5)

    use_absolute_offset: BoolProperty(name="Absolute Offset")
    spacing: FloatProperty(name="Spacing", default=0.2, step=1, unit="LENGTH")


class OBJECT_OT_curve_redistribute(UI, Scatter, Operator):
    bl_label = "JewelCraft Curve Redistribute"
    bl_description = "Redistribute selected objects along curve"
    bl_idname = "object.jewelcraft_curve_redistribute"
    bl_options = {"REGISTER", "UNDO"}

    is_scatter = False

    rot_x: FloatProperty(name="Tilt", step=10, unit="ROTATION", options={"SKIP_SAVE"})
    rot_z: FloatProperty(name="Rotation", step=10, unit="ROTATION", options={"SKIP_SAVE"})
    loc_z: FloatProperty(name="Offset", step=1, unit="LENGTH", options={"SKIP_SAVE"})

    start: FloatProperty(name="Start", step=5)
    end: FloatProperty(name="End", default=100.0, step=5)

    use_absolute_offset: BoolProperty(name="Absolute Offset", options={"SKIP_SAVE"})
    spacing: FloatProperty(name="Spacing", step=1, default=0.2, unit="LENGTH")
