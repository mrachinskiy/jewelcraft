# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import FloatProperty, StringProperty
from bpy.types import Operator

from ... import var


_SIZE_RATIO_MIN = 0.1
_SIZE_RATIO_MAX = 0.5
_HEIGHT_RATIO_MIN = 0.1
_HEIGHT_RATIO_MAX = 1.0
_WIDTH_RATIO_MIN = 0.1
_WIDTH_RATIO_MAX = 1.0
_MAX_GAP_MIN = 0.0
_MAX_GAP_MAX = 1.0
_WELD_DISTANCE_MIN = 0.0
_WELD_DISTANCE_MAX = 1.0
_SIZE_RATIO_DEFAULT = 0.4
_HEIGHT_RATIO_DEFAULT = 0.2
_WIDTH_RATIO_DEFAULT = 0.6
_UNIFORMITY_MIN = 0.0
_UNIFORMITY_MAX = 1.0
_UNIFORMITY_DEFAULT = 0.0
_MAX_GAP_DEFAULT = 0.5
_WELD_DISTANCE_DEFAULT = 0.3


class OBJECT_OT_prongs_auto_add(Operator):
    bl_label = "Add Prongs Auto"
    bl_description = "Create standard prongs between selected gems"
    bl_idname = "object.jewelcraft_prongs_auto_add"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    size_ratio: FloatProperty(name="Prong Size Ratio", default=_SIZE_RATIO_DEFAULT, min=_SIZE_RATIO_MIN, max=_SIZE_RATIO_MAX, soft_max=_SIZE_RATIO_MAX, precision=2)
    height_ratio: FloatProperty(name="Prong Height Ratio", default=_HEIGHT_RATIO_DEFAULT, min=_HEIGHT_RATIO_MIN, max=_HEIGHT_RATIO_MAX, soft_max=_HEIGHT_RATIO_MAX, precision=2)
    width_between_prongs: FloatProperty(name="Width Between Prongs Ratio", default=_WIDTH_RATIO_DEFAULT, min=_WIDTH_RATIO_MIN, max=_WIDTH_RATIO_MAX, soft_max=_WIDTH_RATIO_MAX, precision=2)
    uniformity: FloatProperty(name="Uniformity", default=_UNIFORMITY_DEFAULT, min=_UNIFORMITY_MIN, max=_UNIFORMITY_MAX, soft_max=_UNIFORMITY_MAX, subtype="FACTOR", precision=2)
    max_gap: FloatProperty(name="Max Gap", default=_MAX_GAP_DEFAULT, min=_MAX_GAP_MIN, max=_MAX_GAP_MAX, soft_max=_MAX_GAP_MAX, step=1, unit="LENGTH")
    weld_distance: FloatProperty(name="Weld Distance", default=_WELD_DISTANCE_DEFAULT, min=_WELD_DISTANCE_MIN, max=_WELD_DISTANCE_MAX, soft_max=_WELD_DISTANCE_MAX, step=1, unit="LENGTH")
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})

    def draw(self, context):
        from . import prongs_auto_ui
        prongs_auto_ui.draw(self, context)

    def execute(self, context):
        from ...lib import asset
        from . import prongs_auto_mesh

        gems = self._get_selected_gems(context)

        if len(gems) < 2:
            self.report({"ERROR"}, "At least two gem objects must be selected")
            return {"CANCELLED"}

        collection = self._get_or_create_collection(context)

        try:
            prong_infos = prongs_auto_mesh.create_prongs_auto(
                gems,
                self.size_ratio,
                self.height_ratio,
                self.width_between_prongs,
                self.uniformity,
                self.max_gap,
                self.weld_distance,
            )
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        if not prong_infos:
            self.report({"WARNING"}, "No valid gem connections found for the current gap settings")
            return {"CANCELLED"}

        for info in prong_infos:
            bm = prongs_auto_mesh.create_prong_mesh(info)
            ob = asset.bm_to_object(bm, name="Prong", color=self.color)
            asset.ob_link(ob, collection)
            ob.matrix_world = info.matrix

        return {"FINISHED"}

    def invoke(self, context, event):
        gems = self._get_selected_gems(context)

        if len(gems) < 2:
            self.report({"ERROR"}, "At least two gem objects must be selected")
            return {"CANCELLED"}

        self.size_ratio = _SIZE_RATIO_DEFAULT
        self.height_ratio = _HEIGHT_RATIO_DEFAULT
        self.width_between_prongs = _WIDTH_RATIO_DEFAULT
        self.uniformity = _UNIFORMITY_DEFAULT
        self.max_gap = _MAX_GAP_DEFAULT
        self.weld_distance = _WELD_DISTANCE_DEFAULT
        self.collection_name = ""

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.color = prefs.color_prongs

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)

    @staticmethod
    def _get_selected_gems(context):
        return [ob for ob in context.selected_objects if "gem" in ob]

    def _get_or_create_collection(self, context):
        if self.collection_name:
            collection = context.blend_data.collections.get(self.collection_name)
            if collection is not None:
                return collection

        collection = context.blend_data.collections.new("Prongs")
        context.scene.collection.children.link(collection)
        self.collection_name = collection.name

        return collection