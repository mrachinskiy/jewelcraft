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
from bpy.props import EnumProperty

from .. import dynamic_lists


class VIEW3D_OT_jewelcraft_search_stone(Operator):
    bl_label = "Search Stone"
    bl_description = "Search stone by name"
    bl_idname = "view3d.jewelcraft_search_stone"
    bl_property = "stone"
    bl_options = {"INTERNAL"}

    stone = EnumProperty(items=dynamic_lists.stones)

    def execute(self, context):
        context.window_manager.jewelcraft.gem_stone = self.stone
        context.area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}


class VIEW3D_OT_jewelcraft_search_asset(Operator):
    bl_label = "Search Asset"
    bl_description = "Search asset by name"
    bl_idname = "view3d.jewelcraft_search_asset"
    bl_property = "asset"
    bl_options = {"INTERNAL"}

    asset = EnumProperty(items=dynamic_lists.assets)

    def execute(self, context):
        context.window_manager.jewelcraft.asset_list = self.asset
        context.area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}
