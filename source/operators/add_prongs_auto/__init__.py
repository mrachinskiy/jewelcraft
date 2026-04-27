# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Artem Viveritsa
# SPDX-FileContributor: Modified by Mikhail Rachinskiy

from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import Operator

from ... import var


class OBJECT_OT_prongs_auto_add(Operator):
    bl_label = "Auto Prongs"
    bl_description = "Automatically place prongs between selected gems"
    bl_idname = "object.jewelcraft_prongs_auto_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    has_non_round_cuts = False

    use_coll_move: BoolProperty(name="Move to Collection", default=True, options={"SKIP_SAVE"})
    collection_name: StringProperty(name="Collection", default="Prongs", options={"SKIP_SAVE"})

    size_ratio: FloatProperty(
        name="Size",
        description="Prong diameter relative to gem size",
        default=0.4,
        min=0.1,
        max=0.5,
        step=1,
        precision=2,
        subtype="FACTOR",
        options={"SKIP_SAVE"},
    )
    height_ratio: FloatProperty(
        name="Height",
        description="Prong height relative to gem size",
        default=0.2,
        min=0.1,
        max=1.0,
        step=1,
        precision=2,
        subtype="FACTOR",
        options={"SKIP_SAVE"},
    )
    size_step: FloatProperty(
        name="Size Step",
        description="Step value difference between diameters of generated prongs",
        default=0.025,
        min=0.001,
        soft_max=1.0,
        precision=3,
        step=2.5,
        unit="LENGTH",
        options={"SKIP_SAVE"},
    )
    uniformity: FloatProperty(
        name="Uniformity",
        description="Blends prong size and height toward the median value of all generated prongs",
        default=0.5,
        min=0.0,
        max=1.0,
        step=1,
        precision=2,
        subtype="FACTOR",
        options={"SKIP_SAVE"},
    )

    gap: FloatProperty(
        name="Gap",
        description="Distance between two prongs relative to gem size",
        default=0.6,
        min=0.1,
        max=1.0,
        step=1,
        precision=2,
        subtype="FACTOR",
        options={"SKIP_SAVE"},
    )
    max_gap: FloatProperty(
        name="Max Gap",
        default=0.5,
        min=0.0,
        max=1.0,
        step=1,
        unit="LENGTH",
        options={"SKIP_SAVE"},
    )
    merge_distance: FloatProperty(
        name="Merge Distance",
        description="Merge prongs located at specified distance",
        default=0.3,
        min=0.0,
        max=1.0,
        step=1,
        unit="LENGTH",
        options={"SKIP_SAVE"},
    )

    bump_scale: FloatProperty(
        name="Bump Scale",
        default=0.5,
        soft_min=0.0,
        soft_max=1.0,
        step=1,
        subtype="FACTOR",
        options={"SKIP_SAVE"},
    )
    taper: FloatProperty(
        name="Taper",
        default=0.0,
        min=0.0,
        soft_max=1.0,
        step=1,
        subtype="FACTOR",
        options={"SKIP_SAVE"},
    )
    detalization: IntProperty(
        name="Detalization",
        default=32,
        min=3,
        soft_max=64,
        step=1,
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        from . import prongs_auto_ui
        prongs_auto_ui.draw(self, context)

    def execute(self, context):
        from ...lib import asset
        from ..add_prongs import prongs_mesh
        from . import prongs_auto_mesh

        try:
            prong_infos = prongs_auto_mesh.create_prongs_auto(
                (ob for ob in context.selected_objects if "gem" in ob),
                self.size_ratio,
                self.height_ratio,
                self.gap,
                self.uniformity,
                self.max_gap,
                self.merge_distance,
                self.size_step,
            )
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"FINISHED"}

        if not prong_infos:
            self.report({"WARNING"}, "No valid gem connections found for the current gap settings")
            return {"FINISHED"}

        coll = context.blend_data.collections.get(self.collection_name)
        if coll is None:
            coll = context.blend_data.collections.new(self.collection_name)
            context.scene.collection.children.link(coll)

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        for info in prong_infos:
            bm = prongs_mesh.create_prong(
                info.size,
                info.height,
                info.height,
                self.bump_scale,
                self.taper,
                self.detalization,
            )
            ob = asset.bm_to_object(bm, name="Prong", color=prefs.color_prongs)
            asset.ob_link(ob, coll)
            ob.matrix_world = info.matrix

        return {"FINISHED"}

    def invoke(self, context, event):
        gems = [ob for ob in context.selected_objects if "gem" in ob]
        self.has_non_round_cuts = any(ob["gem"]["cut"] != "ROUND" for ob in gems)

        if len(gems) < 2:
            self.report({"ERROR"}, "At least two gem objects must be selected")
            return {"CANCELLED"}

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)
