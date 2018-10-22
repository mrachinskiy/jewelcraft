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


from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty

from .scatter_draw import Draw
from .scatter_func import Scatter


class OBJECT_OT_jewelcraft_curve_scatter(Draw, Scatter, Operator):
    bl_label = "JewelCraft Curve Scatter"
    bl_description = "Scatter selected object along active curve"
    bl_idname = "object.jewelcraft_curve_scatter"
    bl_options = {"REGISTER", "UNDO"}

    is_scatter = True

    number = IntProperty(name="Object Number", default=10, min=1, soft_max=100)

    rot_y = FloatProperty(name="Orientation", step=10, unit="ROTATION")
    rot_z = FloatProperty(name="Rotation", step=10, unit="ROTATION")
    loc_z = FloatProperty(name="Position", unit="LENGTH")

    start = FloatProperty(name="Start")
    end = FloatProperty(name="End", default=100.0)

    use_absolute_offset = BoolProperty(name="Absolute Offset")
    spacing = FloatProperty(name="Spacing", default=0.2, unit="LENGTH")


class OBJECT_OT_jewelcraft_curve_redistribute(Draw, Scatter, Operator):
    bl_label = "JewelCraft Curve Redistribute"
    bl_description = "Redistribute selected objects along curve"
    bl_idname = "object.jewelcraft_curve_redistribute"
    bl_options = {"REGISTER", "UNDO"}

    is_scatter = False

    rot_y = FloatProperty(name="Orientation", step=10, unit="ROTATION", options={"SKIP_SAVE"})
    rot_z = FloatProperty(name="Rotation", step=10, unit="ROTATION", options={"SKIP_SAVE"})
    loc_z = FloatProperty(name="Position", unit="LENGTH", options={"SKIP_SAVE"})

    start = FloatProperty(name="Start")
    end = FloatProperty(name="End", default=100.0)

    use_absolute_offset = BoolProperty(name="Absolute Offset", options={"SKIP_SAVE"})
    spacing = FloatProperty(name="Spacing", default=0.2, unit="LENGTH")
