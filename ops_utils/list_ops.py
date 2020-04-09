# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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
from bpy.props import BoolProperty, StringProperty

from .. import var


# Scene
# ---------------------------


class SCENE_OT_ul_del(Operator):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "scene.jewelcraft_ul_del"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.scene.jewelcraft, self.prop).remove()
        return {"FINISHED"}


class SCENE_OT_ul_clear(Operator):
    bl_label = "Clear List"
    bl_description = "Remove all list items"
    bl_idname = "scene.jewelcraft_ul_clear"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.scene.jewelcraft, self.prop).clear()
        return {"FINISHED"}


class SCENE_OT_ul_move(Operator):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "scene.jewelcraft_ul_move"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.scene.jewelcraft, self.prop).move(self.move_up)
        return {"FINISHED"}


# Preferences
# ---------------------------


class PREFERENCES_OT_ul_add(Operator):
    bl_label = "Add Item"
    bl_description = "Add new item to the list"
    bl_idname = "preferences.jewelcraft_ul_add"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.preferences.addons[var.ADDON_ID].preferences, self.prop).add()
        context.preferences.is_dirty = True
        return {"FINISHED"}


class PREFERENCES_OT_ul_del(Operator):
    bl_label = "Remove Item"
    bl_description = "Remove selected item"
    bl_idname = "preferences.jewelcraft_ul_del"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.preferences.addons[var.ADDON_ID].preferences, self.prop).remove()
        context.preferences.is_dirty = True
        return {"FINISHED"}


class PREFERENCES_OT_ul_move(Operator):
    bl_label = "Move Item"
    bl_description = "Move selected item up/down in the list"
    bl_idname = "preferences.jewelcraft_ul_move"
    bl_options = {"INTERNAL"}

    prop: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    move_up: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        getattr(context.preferences.addons[var.ADDON_ID].preferences, self.prop).move(self.move_up)
        context.preferences.is_dirty = True
        return {"FINISHED"}
