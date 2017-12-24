import os

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import bpy.utils.previews

from .. import var, dynamic_lists
from ..lib.asset import (
	asset_export,
	asset_import_batch,
	render_preview,
	face_pos,
	user_asset_library_folder,
	)


class Setup:

	def __init__(self):
		self.props = bpy.context.window_manager.jewelcraft

		self.folder_name = self.props.asset_folder
		self.folder = os.path.join(user_asset_library_folder(), self.folder_name)

		self.asset_name = self.props.asset_list
		self.filepath = os.path.join(self.folder, self.asset_name)


class WM_OT_JewelCraft_Asset_Add_To_Library(Operator, Setup):
	"""Add selected objects to asset library"""
	bl_label = 'Add To Library'
	bl_idname = 'wm.jewelcraft_asset_add_to_library'
	bl_options = {'INTERNAL'}

	asset_name = StringProperty(name='Asset Name', description='Asset name', options={'SKIP_SAVE'})

	@classmethod
	def poll(cls, context):
		return bool(context.window_manager.jewelcraft.asset_folder)

	def __init__(self):
		super().__init__()
		prefs = bpy.context.user_preferences.addons[var.addon_id].preferences

		self.asset_name = ''

		if prefs.asset_name_from_obj:
			self.asset_name = bpy.context.active_object.name

	def draw(self, context):
		layout = self.layout
		layout.separator()
		layout.prop(self, 'asset_name')
		layout.separator()

	def execute(self, context):
		filepath = os.path.join(self.folder, self.asset_name)

		asset_export(folder=self.folder, filename=self.asset_name + '.blend')
		render_preview(filepath=filepath + '.png')
		dynamic_lists.asset_list_refresh()
		self.props.asset_list = self.asset_name

		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)


class WM_OT_JewelCraft_Asset_Remove_From_Library(Operator, Setup):
	"""Remove asset from library"""
	bl_label = 'Remove Asset'
	bl_idname = 'wm.jewelcraft_asset_remove_from_library'
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return bool(context.window_manager.jewelcraft.asset_list)

	def execute(self, context):
		asset_list = dynamic_lists.assets(self, context)
		prev_item = ''
		last_item = self.asset_name == asset_list[-1][0]

		for ast in asset_list:
			if ast[0] == self.asset_name:
				break
			prev_item = ast[0]

		os.remove(self.filepath + '.blend')
		os.remove(self.filepath + '.png')

		dynamic_lists.asset_list_refresh(preview_id=self.folder_name + self.asset_name)

		if last_item:
			try:
				self.props.asset_list = prev_item
			except:
				pass

		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_confirm(self, event)


class WM_OT_JewelCraft_Asset_Rename(Operator, Setup):
	"""Rename asset"""
	bl_label = 'Rename Asset'
	bl_idname = 'wm.jewelcraft_asset_rename'
	bl_options = {'INTERNAL'}

	asset_name = StringProperty(name='Asset Name', description='Asset name', options={'SKIP_SAVE'})

	@classmethod
	def poll(cls, context):
		return bool(context.window_manager.jewelcraft.asset_list)

	def draw(self, context):
		layout = self.layout
		layout.separator()
		layout.prop(self, 'asset_name')
		layout.separator()

	def execute(self, context):
		name_current = self.props.asset_list

		file_current = os.path.join(self.folder, name_current + '.blend')
		file_preview_current = os.path.join(self.folder, name_current + '.png')

		file_new = os.path.join(self.folder, self.asset_name + '.blend')
		file_preview_new = os.path.join(self.folder, self.asset_name + '.png')

		if not os.path.exists(self.folder):
			return {'FINISHED'}

		os.rename(file_current, file_new)
		os.rename(file_preview_current, file_preview_new)

		dynamic_lists.asset_list_refresh()
		self.props.asset_list = self.asset_name

		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)


class WM_OT_JewelCraft_Asset_Replace(Operator, Setup):
	"""Replace current asset with selected objects"""
	bl_label = 'Replace Asset'
	bl_idname = 'wm.jewelcraft_asset_replace'
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return bool(context.window_manager.jewelcraft.asset_list)

	def execute(self, context):
		asset_export(folder=self.folder, filename=self.asset_name + '.blend')
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_confirm(self, event)


class WM_OT_JewelCraft_Asset_Preview_Replace(Operator, Setup):
	"""Replace asset preview image"""
	bl_label = 'Replace Asset Preview'
	bl_idname = 'wm.jewelcraft_asset_preview_replace'
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return bool(context.window_manager.jewelcraft.asset_list)

	def execute(self, context):
		render_preview(filepath=self.filepath + '.png')
		dynamic_lists.asset_list_refresh(preview_id=self.folder_name + self.asset_name)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_confirm(self, event)


class WM_OT_JewelCraft_Asset_Import(Operator, Setup):
	"""Import selected asset"""
	bl_label = 'JewelCraft Import Asset'
	bl_idname = 'wm.jewelcraft_asset_import'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bool(context.window_manager.jewelcraft.asset_list)

	def execute(self, context):
		scene = context.scene

		for ob in scene.objects:
			ob.select = False

		imported = asset_import_batch(filepath=self.filepath + '.blend')
		obs = imported.objects

		for ob in obs:
			scene.objects.link(ob)
			ob.select = True

		if len(obs) == 1:
			ob.location = scene.cursor_location

			if context.mode == 'EDIT_MESH':
				face_pos(ob)
				bpy.ops.object.mode_set(mode='OBJECT')

		scene.objects.active = ob

		return {'FINISHED'}
