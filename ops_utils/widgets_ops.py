# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
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
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty

from .. import var


class OBJECT_OT_jewelcraft_widgets_overrides_set(Operator):
    bl_label = "Override"
    bl_description = "Override widget display properties for selected objects"
    bl_idname = "object.jewelcraft_widgets_overrides_set"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    color = FloatVectorProperty(name="Widget Color", default=(1.0, 1.0, 1.0, 1.0), size=4, min=0.0, soft_max=1.0, subtype="COLOR")
    linewidth = IntProperty(name="Line Width", default=2, min=1, soft_max=5, subtype="PIXEL")
    distance = FloatProperty(name="Distance", default=0.2, min=0.0, step=1, precision=2, unit="LENGTH")

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        split.row()
        col = split.column(align=True)
        col.prop(self, "color", text="")
        col.prop(self, "linewidth")
        col.prop(self, "distance")

    def execute(self, context):

        for ob in context.selected_objects:
            if "gem" in ob:
                ob["jewelcraft_widget"] = {
                    "color": self.color,
                    "linewidth": self.linewidth,
                    "distance": self.distance,
                }

        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        prefs = context.user_preferences.addons[var.ADDON_ID].preferences
        default_settings = {
            "color": prefs.widget_color,
            "linewidth": prefs.widget_linewidth,
            "distance": prefs.widget_distance,
        }

        ovrd = context.active_object.get("jewelcraft_widget")

        if ovrd:
            default_settings.update(ovrd)

        self.color = default_settings["color"]
        self.linewidth = default_settings["linewidth"]
        self.distance = default_settings["distance"]

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_jewelcraft_widgets_overrides_del(Operator):
    bl_label = "Clear"
    bl_description = "Remove widget override properties from selected objects"
    bl_idname = "object.jewelcraft_widgets_overrides_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):

        for ob in context.selected_objects:
            if "jewelcraft_widget" in ob:
                del ob["jewelcraft_widget"]

        context.area.tag_redraw()

        return {"FINISHED"}
