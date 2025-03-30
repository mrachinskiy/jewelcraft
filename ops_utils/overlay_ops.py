# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import FloatProperty, FloatVectorProperty
from bpy.types import Operator

from .. import var


class OBJECT_OT_overlay_override_add(Operator):
    bl_label = "Override"
    bl_description = "Override overlay settings for selected objects"
    bl_idname = "object.jewelcraft_overlay_override_add"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    color: FloatVectorProperty(
        name="Color",
        default=(1.0, 1.0, 1.0, 1.0),
        size=4,
        min=0.0,
        soft_max=1.0,
        subtype="COLOR",
    )
    linewidth: FloatProperty(
        name="Line Width",
        default=1.2,
        min=1.0,
        soft_max=5.0,
        subtype="PIXEL",
    )
    spacing: FloatProperty(
        name="Spacing",
        default=0.2,
        min=0.0,
        step=1,
        precision=2,
        unit="LENGTH",
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(self, "color")
        col.prop(self, "linewidth")
        col.prop(self, "spacing", text="Spacing", text_ctxt="Jewelry")

    def execute(self, context):
        for ob in context.selected_objects:
            if "gem" in ob:
                ob["gem_overlay"] = {
                    "color": self.color,
                    "linewidth": self.linewidth,
                    "spacing": self.spacing,
                }

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        prefs = context.preferences.addons[var.ADDON_ID].preferences
        props = context.scene.jewelcraft

        default_settings = {
            "color": prefs.overlay_color,
            "linewidth": prefs.overlay_linewidth,
            "spacing": props.overlay_spacing,
        }

        ovrd = context.object.get("gem_overlay")
        if ovrd:
            default_settings.update(ovrd)

        self.color = default_settings["color"]
        self.linewidth = default_settings["linewidth"]
        self.spacing = default_settings["spacing"]

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_overlay_override_del(Operator):
    bl_label = "Clear"
    bl_description = "Remove overrides from selected objects"
    bl_idname = "object.jewelcraft_overlay_override_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        for ob in context.selected_objects:
            if "gem_overlay" in ob:
                del ob["gem_overlay"]

        context.area.tag_redraw()

        return {"FINISHED"}
