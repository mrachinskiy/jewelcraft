from bpy.types import Operator
from bpy.props import EnumProperty

from .. import dynamic_lists


class VIEW3D_OT_JewelCraft_Search_Stone(Operator):
	"""Search stone by name"""
	bl_label = 'Search Stone'
	bl_idname = 'view3d.jewelcraft_search_stone'
	bl_property = 'stone'
	bl_options = {'INTERNAL'}

	stone = EnumProperty(items=dynamic_lists.stones)

	def execute(self, context):
		context.window_manager.jewelcraft.gem_stone = self.stone
		context.area.tag_redraw()
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'FINISHED'}


class VIEW3D_OT_JewelCraft_Search_Alloy(Operator):
	"""Search alloy by name"""
	bl_label = 'Search Alloy'
	bl_idname = 'view3d.jewelcraft_search_alloy'
	bl_property = 'alloy'
	bl_options = {'INTERNAL'}

	alloy = EnumProperty(items=dynamic_lists.alloys)

	def execute(self, context):
		context.window_manager.jewelcraft.weighting_mat = self.alloy
		context.area.tag_redraw()
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'FINISHED'}


class VIEW3D_OT_JewelCraft_Search_Asset(Operator):
	"""Search asset by name"""
	bl_label = 'Search Asset'
	bl_idname = 'view3d.jewelcraft_search_asset'
	bl_property = 'asset'
	bl_options = {'INTERNAL'}

	asset = EnumProperty(items=dynamic_lists.assets)

	def execute(self, context):
		context.window_manager.jewelcraft.asset_list = self.asset
		context.area.tag_redraw()
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'FINISHED'}
