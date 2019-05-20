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


from math import radians

from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty

from .. import var
from ..lib import asset
from .prongs_ui import UI
from .prongs_presets import init_presets
from .prongs_mesh import create_prongs


class OBJECT_OT_prongs_add(UI, Operator):
    bl_label = "JewelCraft Make Prongs"
    bl_description = "Create prongs for selected gems"
    bl_idname = "object.jewelcraft_prongs_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    auto_presets: BoolProperty(
        name="Use Automated Presets",
        description="Use automatically generated presets, discards user edits or presets",
        default=True,
    )

    number: IntProperty(name="Prong Number", default=4, min=1, soft_max=10)

    diameter: FloatProperty(name="Diameter", default=0.4, min=0.0, step=1, unit="LENGTH")
    z_top: FloatProperty(name="Top", default=0.4, step=1, unit="LENGTH")
    z_btm: FloatProperty(name="Bottom", default=0.5, step=1, unit="LENGTH")

    position: FloatProperty(name="Position", default=radians(45.0), step=100, precision=0, unit="ROTATION")
    intersection: FloatProperty(
        name="Intersection",
        default=30.0,
        soft_min=0.0,
        soft_max=100.0,
        precision=0,
        subtype="PERCENTAGE",
    )
    alignment: FloatProperty(name="Alignment", step=100, precision=0, unit="ROTATION")

    symmetry: BoolProperty(name="Symmetry")
    symmetry_pivot: FloatProperty(name="Symmetry Pivot", step=100, precision=0, unit="ROTATION")

    bump_scale: FloatProperty(name="Bump Scale", default=0.5, soft_min=0.0, soft_max=1.0, subtype="FACTOR")
    taper: FloatProperty(name="Taper", default=0.0, min=0.0, soft_max=1.0, subtype="FACTOR")

    detalization: IntProperty(name="Detalization", default=32, min=12, soft_max=64, step=1)

    def execute(self, context):
        bm = create_prongs(self)
        asset.bm_to_scene(bm, name="Prongs", color=self.color)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.object or not context.selected_objects:
            self.report({"ERROR"}, "At least one gem object must be selected")
            return {"CANCELLED"}

        asset.get_gem(self, context)
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_prongs

        if self.auto_presets:
            init_presets(self)

        return self.execute(context)
