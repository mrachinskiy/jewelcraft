import os

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from .. import dynamic_lists
from ..lib.asset import open_folder, user_asset_library_folder


class Setup:

	def __init__(self):
		self.props = bpy.context.window_manager.jewelcraft
		self.folder_name = self.props.asset_folder
		self.folder = os.path.join(user_asset_library_folder(), self.folder_name)


class WM_OT_JewelCraft_Asset_Library_Open(Operator):
	"""Open asset library folder"""
	bl_label = 'Open Library Folder'
	bl_idname = 'wm.jewelcraft_asset_library_open'
	bl_options = {'INTERNAL'}

	def execute(self, context):
		open_folder(user_asset_library_folder())
		return {'FINISHED'}


class WM_OT_JewelCraft_Asset_Folder_Create(Operator, Setup):
	"""Create category"""
	bl_label = 'Create Category'
	bl_idname = 'wm.jewelcraft_asset_folder_create'
	bl_options = {'INTERNAL'}

	folder_name = StringProperty(name='Category Name', description='Category name', options={'SKIP_SAVE'})

	def draw(self, context):
		layout = self.layout
		layout.separator()
		layout.prop(self, 'folder_name')
		layout.separator()

	def execute(self, context):

		folder = os.path.join(user_asset_library_folder(), self.folder_name)

		if not os.path.exists(folder):
			os.makedirs(folder)
			dynamic_lists.asset_folder_list_refresh()
			self.props.asset_folder = self.folder_name

		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)


class WM_OT_JewelCraft_Asset_Folder_Rename(Operator, Setup):
	"""Rename category"""
	bl_label = 'Rename'
	bl_idname = 'wm.jewelcraft_asset_folder_rename'
	bl_options = {'INTERNAL'}

	folder_name = StringProperty(name='Category Name', description='Category name', options={'SKIP_SAVE'})

	def draw(self, context):
		layout = self.layout
		layout.separator()
		layout.prop(self, 'folder_name')
		layout.separator()

	def execute(self, context):

		folder_new = os.path.join(user_asset_library_folder(), self.folder_name)

		if os.path.exists(self.folder):
			os.rename(self.folder, folder_new)
			dynamic_lists.asset_folder_list_refresh()
			self.props.asset_folder = self.folder_name

		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)


class WM_OT_JewelCraft_Asset_UI_Refresh(Operator):
	"""Refresh asset UI"""
	bl_label = 'Refresh'
	bl_idname = 'wm.jewelcraft_asset_ui_refresh'
	bl_options = {'INTERNAL'}

	def execute(self, context):
		dynamic_lists.asset_folder_list_refresh()
		dynamic_lists.asset_list_refresh(hard=True)
		return {'FINISHED'}
