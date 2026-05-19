# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from math import radians

from bpy.props import BoolProperty, FloatProperty, IntProperty
from bpy.types import Operator

from ... import var


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
        import collections

        from ...lib import asset, unit
        from . import prongs_mesh

        from_scene = unit.Scale().from_scene
        group_by_size = collections.defaultdict(list)

        for ob in context.selected_objects:
            if "gem" in ob:
                size = tuple(round(x, 2) for x in from_scene(ob.dimensions))
                group_by_size[size].append(ob)

        for size, obs in group_by_size.items():
            try:
                bm = prongs_mesh.get(self, obs[0].dimensions)
                asset.bm_to_parent(bm, obs, name="Prongs", color=self.color)
            finally:
                bm.free()

        return {"FINISHED"}

    def invoke(self, context, event):
        from ...lib import gemlib
        from . import prongs_presets

        ob = context.object

        if not ob or not context.selected_objects:
            self.report({"ERROR"}, "At least one gem object must be selected")
            return {"CANCELLED"}

        self.cut = ob["gem"]["cut"] if "gem" in ob else None
        try:
            self.shape = gemlib.CUTS[self.cut].shape
        except KeyError:
            self.shape = gemlib.SHAPE_ROUND

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_prongs

        if not event.ctrl:
            prongs_presets.init_presets(self, ob.dimensions.copy())

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)
