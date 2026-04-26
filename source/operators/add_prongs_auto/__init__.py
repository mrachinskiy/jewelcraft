# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import FloatProperty, IntProperty, StringProperty
from bpy.types import Operator

from ... import var


class OBJECT_OT_prongs_auto_add(Operator):
    bl_label = "Auto Prongs"
    bl_description = "Automatically place standard prongs between selected gems"
    bl_idname = "object.jewelcraft_prongs_auto_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}
    has_non_round_cuts = False

    collection_name: StringProperty(
        name="Collection",
        description="Target collection for generated prongs; if it does not exist, it will be created",
        default="Prongs",
        options={"SKIP_SAVE"},
    )
    
    size_ratio: FloatProperty(
        name="Size",
        description="Multiplier for prong diameter relative to the connection size of the paired gems; for example, 0.40 makes the prong diameter 40% of that size",
        default=0.4,
        min=0.1,
        max=0.5,
        soft_max=0.5,
        step=1,
        precision=2,
        options={"SKIP_SAVE"},
    )
    height_ratio: FloatProperty(
        name="Height",
        description="Multiplier for prong height above the connection midpoint relative to the paired gem size; higher values produce taller prongs",
        default=0.2,
        min=0.1,
        max=1.0,
        soft_max=1.0,
        step=1,
        precision=2,
        options={"SKIP_SAVE"},
    )
    uniformity: FloatProperty(
        name="Uniformity",
        description="Blends each prong size and height toward the median values of all generated prongs",
        default=0.5,
        min=0.0,
        max=1.0,
        soft_max=1.0,
        step=1,
        precision=2,
        options={"SKIP_SAVE"},
    )
    
    width_between_prongs: FloatProperty(
        name="Width Between",
        description="Multiplier for the center-to-center spacing between the two prongs created for each gem connection; higher values place them farther apart",
        default=0.6,
        min=0.1,
        max=1.0,
        soft_max=1.0,
        step=1,
        precision=2,
        options={"SKIP_SAVE"},
    )
    max_gap: FloatProperty(
        name="Max Gap",
        description="Maximum allowed surface gap between two gems for creating a prong pair",
        default=0.5,
        min=0.0,
        max=1.0,
        soft_max=1.0,
        step=1,
        unit="LENGTH",
        options={"SKIP_SAVE"},
    )
    weld_distance: FloatProperty(
        name="Weld Distance",
        description="Merge prongs whose centers are closer than this distance into one averaged prong",
        default=0.3,
        min=0.0,
        max=1.0,
        soft_max=1.0,
        step=1,
        unit="LENGTH",
        options={"SKIP_SAVE"},
    )
    
    size_round: FloatProperty(
        name="Size Round",
        description="Diameter rounding step in millimeters for generated prongs",
        default=0.025,
        min=0.001,
        soft_max=1.0,
        precision=3,
        step=2.5,
        unit="LENGTH",
        options={"SKIP_SAVE"},
    )
    bump_scale: FloatProperty(
        name="Bump Scale",
        description="Height of the rounded top cap; set to 0 for a flat top",
        default=0.5,
        soft_min=0.0,
        soft_max=1.0,
        subtype="FACTOR",
        step=1,
        options={"SKIP_SAVE"},
    )
    taper: FloatProperty(
        name="Taper",
        description="Widens the prong base relative to the top",
        default=0.0,
        min=0.0,
        soft_max=1.0,
        subtype="FACTOR",
        step=1,
        options={"SKIP_SAVE"},
    )
    detalization: IntProperty(
        name="Detalization",
        description="Number of radial segments used to build the prong mesh and top cap",
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
        from . import prongs_auto_mesh
        from ..add_prongs import prongs_mesh

        gems = [ob for ob in context.selected_objects if "gem" in ob]

        collection = context.blend_data.collections.get(self.collection_name)

        if collection is None:
            collection = context.blend_data.collections.new(self.collection_name)
            context.scene.collection.children.link(collection)
            self.collection_name = collection.name

        try:
            prong_infos = prongs_auto_mesh.create_prongs_auto(
                gems,
                self.size_ratio,
                self.height_ratio,
                self.width_between_prongs,
                self.uniformity,
                self.max_gap,
                self.weld_distance,
                self.size_round,
            )
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"FINISHED"}

        if not prong_infos:
            self.report({"WARNING"}, "No valid gem connections found for the current gap settings")
            return {"FINISHED"}

        for info in prong_infos:
            bm = prongs_mesh.create_prong(
                info.size,
                info.height,
                info.height,
                self.bump_scale,
                self.taper,
                self.detalization,
            )
            ob = asset.bm_to_object(bm, name="Prong", color=self.color)
            asset.ob_link(ob, collection)
            ob.matrix_world = info.matrix

        return {"FINISHED"}

    def invoke(self, context, event):
        gems = [ob for ob in context.selected_objects if "gem" in ob]
        self.has_non_round_cuts = any(ob["gem"]["cut"] != "ROUND" for ob in gems)

        if len(gems) < 2:
            self.report({"ERROR"}, "At least two gem objects must be selected")
            return {"CANCELLED"}

        if self.has_non_round_cuts:
            self.report({"WARNING"}, "This tool is optimized for round cuts and may work poorly with other gem cuts")

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_prongs

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)
