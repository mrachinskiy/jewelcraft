# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2022  Mikhail Rachinskiy
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


class OBJECT_OT_prongs_add(Operator):
    bl_label = "Add Prongs"
    bl_description = (
        "Create prongs for selected gems\n"
        "(Shortcut: hold Ctrl when using the tool to avoid properties reset)"
    )
    bl_idname = "object.jewelcraft_prongs_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    number: IntProperty(name="Prong Number", default=4, min=1, soft_max=10)
    diameter: FloatProperty(name="Diameter", default=0.4, min=0.0, step=0.1, unit="LENGTH")
    z1: FloatProperty(name="Top", default=0.4, step=0.1, unit="LENGTH")
    z2: FloatProperty(name="Bottom", default=0.5, step=0.1, unit="LENGTH")

    position: FloatProperty(name="Position", default=radians(45.0), step=25, precision=0, unit="ROTATION")
    intersection: FloatProperty(name="Intersection", default=30.0, soft_min=0.0, soft_max=100.0, precision=0, subtype="PERCENTAGE")
    alignment: FloatProperty(name="Alignment", step=25, precision=0, unit="ROTATION")

    use_symmetry: BoolProperty(name="Symmetry")
    symmetry_pivot: FloatProperty(name="Symmetry Pivot", step=25, precision=0, unit="ROTATION")

    bump_scale: FloatProperty(name="Bump Scale", default=0.5, soft_min=0.0, soft_max=1.0, subtype="FACTOR")
    taper: FloatProperty(name="Taper", default=0.0, min=0.0, soft_max=1.0, subtype="FACTOR")
    detalization: IntProperty(name="Detalization", default=32, min=3, soft_max=64, step=1)

    def draw(self, context):
        from . import prongs_ui
        prongs_ui.draw(self, context)

    def execute(self, context):
        from ..lib import asset
        from . import prongs_mesh

        bm = prongs_mesh.create_prongs(self)
        asset.bm_to_scene(bm, name="Prongs", color=self.color)

        return {"FINISHED"}

    def invoke(self, context, event):
        from ..lib import gemlib
        from . import prongs_presets

        ob = context.object

        if not ob or not context.selected_objects:
            self.report({"ERROR"}, "At least one gem object must be selected")
            return {"CANCELLED"}

        self.gem_dim = ob.dimensions.copy()
        self.cut = ob["gem"]["cut"] if "gem" in ob else None
        try:
            self.shape = gemlib.CUTS[self.cut].shape
        except KeyError:
            self.shape = gemlib.SHAPE_ROUND

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_prongs

        if not event.ctrl:
            prongs_presets.init_presets(self)

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)
