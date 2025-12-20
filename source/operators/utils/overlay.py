# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import EnumProperty, FloatProperty, FloatVectorProperty, IntProperty
from bpy.types import Operator

from ... import var


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


class WM_OT_ul_gem_map_palette_generate(Operator):
    bl_label = "Generate Palette"
    bl_description = "Generate color palette"
    bl_idname = "wm.jewelcraft_ul_gem_map_palette_generate"
    bl_options = {"INTERNAL"}

    hue_range: EnumProperty(
        name="Hue Range",
        items=(
            ("FULL", "Full", ""),
            ("LIMITED", "Limited", ""),
            ("RANDOM", "Random", ""),
        ),
    )
    hue_direction: EnumProperty(
        name="Hue Direction",
        items=(
            ("CW", "Clockwise", ""),
            ("CCW", "Counter-Clockwise", ""),
        ),
    )
    color1: FloatVectorProperty(
        name="Color 1",
        default=(1.0, 0.15, 0.15),
        size=3,
        min=0.0,
        soft_max=1.0,
        subtype="COLOR",
    )
    color2: FloatVectorProperty(
        name="Color 2",
        default=(1.0, 0.86, 0.15),
        size=3,
        min=0.0,
        soft_max=1.0,
        subtype="COLOR",
    )
    palette_size: IntProperty(
        name="Palette Size",
        default=6,
        min=1,
        soft_max=64,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.prop(self, "hue_range")
        if self.hue_range != "RANDOM":
            row.separator()
            row.prop(self, "hue_direction", text="")
            if self.hue_range == "FULL":
                layout.prop(self, "color1", text="Initial Color")
            else:
                row = layout.row(align=True)
                row.prop(self, "color1", text="Color Range")
                row.prop(self, "color2", text="")
        layout.prop(self, "palette_size")

    def execute(self, context):
        from mathutils import Color

        ul = context.window_manager.jewelcraft.gem_map_palette
        ul.clear()

        if self.hue_range == "RANDOM":
            import random

            color = Color((1.0, 1.0, 1.0))
            for _ in range(self.palette_size):
                color.s = random.uniform(0.6, 1.0)
                color.h = random.random()
                item = ul.add()
                item.color = color

            if context.area:
                context.area.tag_redraw()

            return {"FINISHED"}

        color1 = Color(self.color1)
        color2 = Color(self.color2)
        is_cw = self.hue_direction == "CW"

        if self.hue_range == "FULL":
            h_ofst = 1 / self.palette_size
            s_ofst = 0.0
            v_ofst = 0.0
        else:
            h_ofst = 0.0

            if color1.s and color2.s:
                h_diff = color2.h - color1.h

                if h_diff < 0.0:
                    h_diff = 1.0 + h_diff

                if is_cw:
                    h_ofst = h_diff / (self.palette_size - 1)
                else:
                    h_ofst = (1.0 - h_diff) / (self.palette_size - 1)

            s_ofst = (color2.s - color1.s) / (self.palette_size - 1)
            v_ofst = (color2.v - color1.v) / (self.palette_size - 1)

        for _ in range(self.palette_size):
            item = ul.add()
            item.color = color1

            color1.s += s_ofst
            color1.v += v_ofst

            if is_cw:
                remainder = color1.h + h_ofst - 1.0
                if remainder > 0.0:
                    color1.h = remainder
                else:
                    color1.h += h_ofst
            else:
                remainder = color1.h - h_ofst + 1.0
                if remainder < 1.0:
                    color1.h = remainder
                else:
                    color1.h -= h_ofst

        if context.area:
            context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        if event.alt:
            return self.execute(context)

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_ul_gem_map_palette_set_active(Operator):
    bl_label = "Set Active"
    bl_description = "Set active item"
    bl_idname = "wm.jewelcraft_ul_gem_map_palette_set_active"
    bl_options = {"INTERNAL"}

    index: IntProperty()

    def execute(self, context):
        ul = context.window_manager.jewelcraft.gem_map_palette

        if self.index != ul.index:
            ul.index = self.index

        return {"FINISHED"}


class WM_OT_ul_palette_save(Operator):
    bl_label = "Save As Default"
    bl_description = "Save as default"
    bl_idname = "wm.jewelcraft_ul_palette_save"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.window_manager.jewelcraft.gem_map_palette.serialize()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_ul_palette_load(Operator):
    bl_label = "Load Default"
    bl_description = "Load default"
    bl_idname = "wm.jewelcraft_ul_palette_load"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.window_manager.jewelcraft.gem_map_palette.deserialize()
        context.area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
