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
from bpy.props import BoolProperty, FloatProperty, IntProperty

from .. import var
from ..lib import asset
from .cutter_mesh import create_cutter
from .cutter_ui import UI
from .cutter_presets import init_presets


def update_coords_handle(self, context):
    self.girdle_z_top, self.table_z = self.table_z, self.girdle_z_top


def update_coords_hole(self, context):
    self.hole_z_top, self.culet_z = self.culet_z, self.hole_z_top


class OBJECT_OT_cutter_add(UI, Operator):
    bl_label = "JewelCraft Make Cutter"
    bl_description = "Create cutter for selected gems"
    bl_idname = "object.jewelcraft_cutter_add"
    bl_options = {"REGISTER", "UNDO"}

    auto_presets: BoolProperty(
        name="Use Automated Presets",
        description="Use automatically generated presets, discards user edits or presets",
        default=True,
    )

    detalization: IntProperty(name="Detalization", default=32, min=12, soft_max=64, step=1)

    handle: BoolProperty(name="Handle", default=True, update=update_coords_handle)
    handle_l_size: FloatProperty(name="Length", step=0.1, unit="LENGTH")
    handle_w_size: FloatProperty(name="Width", step=0.1, unit="LENGTH")
    handle_z_top: FloatProperty(name="Top", default=0.5, step=0.1, unit="LENGTH")
    handle_z_btm: FloatProperty(name="Bottom", default=0.5, step=0.1, unit="LENGTH")

    girdle_l_ofst: FloatProperty(name="Length Offset", step=0.1, unit="LENGTH")
    girdle_w_ofst: FloatProperty(name="Width Offset", step=0.1, unit="LENGTH")
    girdle_z_top: FloatProperty(name="Top", default=0.05, step=0.1, unit="LENGTH")
    girdle_z_btm: FloatProperty(name="Bottom", step=0.1, unit="LENGTH")
    table_z: FloatProperty(name="Table", options={"HIDDEN"})

    hole: BoolProperty(name="Hole", default=True, update=update_coords_hole)
    hole_z_top: FloatProperty(name="Top", default=0.25, step=0.1, unit="LENGTH")
    hole_z_btm: FloatProperty(name="Bottom", default=1.0, step=0.1, unit="LENGTH")
    hole_l_size: FloatProperty(name="Length", step=0.1, unit="LENGTH")
    hole_w_size: FloatProperty(name="Width", step=0.1, unit="LENGTH")
    hole_pos_ofst: FloatProperty(name="Position Offset", step=0.1, unit="LENGTH")
    culet_z: FloatProperty(name="Culet", options={"HIDDEN"})

    curve_seat: BoolProperty(name="Curve Seat")
    curve_seat_segments: IntProperty(name="Segments", default=15, min=2, soft_max=30, step=1)
    curve_seat_profile: FloatProperty(name="Profile", default=0.5, min=0.15, max=1.0, subtype="FACTOR")

    curve_profile: BoolProperty(name="Curve Profile")
    curve_profile_segments: IntProperty(name="Segments", default=10, min=1, soft_max=30, step=1)
    curve_profile_factor: FloatProperty(name="Factor", default=0.1, min=0.0, step=1)

    mul_1: FloatProperty(
        name="Factor 1",
        default=1.0,
        min=0.0,
        soft_max=2.0,
        subtype="FACTOR",
    )
    mul_2: FloatProperty(
        name="Factor 2",
        default=1.0,
        min=0.0,
        soft_max=2.0,
        subtype="FACTOR",
    )

    bevel_corners: BoolProperty(name="Bevel Corners")
    bevel_corners_width: FloatProperty(
        name="Width",
        default=0.1,
        min=0.0,
        step=0.1,
        unit="LENGTH",
    )
    bevel_corners_percent: FloatProperty(
        name="Width",
        default=18.0,
        min=0.0,
        max=50.0,
        step=1,
        subtype="PERCENTAGE",
    )
    bevel_corners_segments: IntProperty(
        name="Segments",
        default=1,
        min=1,
        soft_max=30,
        step=1,
    )
    bevel_corners_profile: FloatProperty(
        name="Profile",
        default=0.5,
        min=0.15,
        max=1.0,
        subtype="FACTOR",
    )

    def execute(self, context):
        bm = create_cutter(self)
        asset.bm_to_scene(bm, name="Cutter", color=self.color)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.object or not context.selected_objects:
            self.report({"ERROR"}, "At least one gem object must be selected")
            return {"CANCELLED"}

        asset.get_gem(self, context)
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_cutter

        if self.auto_presets:
            init_presets(self)

        return self.execute(context)
