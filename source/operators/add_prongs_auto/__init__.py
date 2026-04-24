# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import FloatProperty, IntProperty, StringProperty
from bpy.types import Operator

from ... import var


class OBJECT_OT_prongs_auto_add(Operator):
    bl_label = "Add Prongs Auto"
    bl_description = "Create standard prongs between selected gems"
    bl_idname = "object.jewelcraft_prongs_auto_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    size_ratio: FloatProperty(name="Prong Size Ratio", default=0.4, min=0.1, max=0.5, soft_max=0.5, precision=2, options={"SKIP_SAVE"})
    height_ratio: FloatProperty(name="Prong Height Ratio", default=0.2, min=0.1, max=1.0, soft_max=1.0, precision=2, options={"SKIP_SAVE"})
    width_between_prongs: FloatProperty(name="Width Between Prongs Ratio", default=0.6, min=0.1, max=1.0, soft_max=1.0, precision=2, options={"SKIP_SAVE"})
    uniformity: FloatProperty(name="Uniformity", default=0.5, min=0.0, max=1.0, soft_max=1.0, subtype="FACTOR", precision=2, options={"SKIP_SAVE"})
    max_gap: FloatProperty(name="Max Gap", default=0.5, min=0.0, max=1.0, soft_max=1.0, step=1, unit="LENGTH", options={"SKIP_SAVE"})
    weld_distance: FloatProperty(name="Weld Distance", default=0.3, min=0.0, max=1.0, soft_max=1.0, step=1, unit="LENGTH", options={"SKIP_SAVE"})
    size_round: FloatProperty(name="Size Round", default=0.025, min=0.001, soft_max=1.0, precision=3, step=0.1, unit="LENGTH", options={"SKIP_SAVE"})
    bump_scale: FloatProperty(name="Bump Scale", default=0.5, soft_min=0.0, soft_max=1.0, subtype="FACTOR", options={"SKIP_SAVE"})
    taper: FloatProperty(name="Taper", default=0.0, min=0.0, soft_max=1.0, subtype="FACTOR", options={"SKIP_SAVE"})
    detalization: IntProperty(name="Detalization", default=32, min=3, soft_max=64, step=1, options={"SKIP_SAVE"})
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})
    
    selected_gem_count = 0

    def draw(self, context):
        from . import prongs_auto_ui
        prongs_auto_ui.draw(self, context)

    def execute(self, context):
        from ...lib import asset
        from . import prongs_auto_mesh
        from ..add_prongs import prongs_mesh

        gems = [ob for ob in context.selected_objects if "gem" in ob]

        if self.selected_gem_count < 2:
            self.report({"ERROR"}, "At least two gem objects must be selected")
            return {"FINISHED"}

        if self.collection_name:
            collection = context.blend_data.collections.get(self.collection_name)
        else:
            collection = None

        if collection is None:
            collection = context.blend_data.collections.new("Prongs")
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
        self.selected_gem_count = len(gems)

        if self.selected_gem_count < 2:
            self.report({"ERROR"}, "At least two gem objects must be selected")
            return {"CANCELLED"}

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_prongs

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)
