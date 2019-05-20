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
from bpy.props import FloatProperty, FloatVectorProperty

from .. import var


class OBJECT_OT_widget_override_set(Operator):
    bl_label = "Override"
    bl_description = "Override widget display properties for selected objects"
    bl_idname = "object.jewelcraft_widget_override_set"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    color: FloatVectorProperty(
        name="Widget Color",
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
        col.prop(self, "spacing", text="Spacing", text_ctxt="JewelCraft")

    def execute(self, context):
        for ob in context.selected_objects:
            if "gem" in ob:
                ob["jewelcraft_widget"] = {
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
            "color": prefs.widget_color,
            "linewidth": prefs.widget_linewidth,
            "spacing": props.widget_spacing,
        }

        ovrd = context.object.get("jewelcraft_widget")
        if ovrd:
            default_settings.update(ovrd)

        self.color = default_settings["color"]
        self.linewidth = default_settings["linewidth"]
        self.spacing = default_settings["spacing"]

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_widget_override_del(Operator):
    bl_label = "Clear"
    bl_description = "Remove widget override properties from selected objects"
    bl_idname = "object.jewelcraft_widget_override_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        for ob in context.selected_objects:
            if "jewelcraft_widget" in ob:
                del ob["jewelcraft_widget"]

        context.area.tag_redraw()

        return {"FINISHED"}
