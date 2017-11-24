import bpy
from bpy.types import Panel, Menu

from . import dynamic_lists

# Extern
from . import addon_updater_ops


preview_collections = {}


# Utils
# ---------------------------


def icon_tria(prop):
	if prop:
		return 'TRIA_DOWN'

	return 'TRIA_RIGHT'


class Setup:
	bl_category = 'JewelCraft'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'

	def __init__(self):
		self.prefs = bpy.context.user_preferences.addons[__package__].preferences
		self.scene_props = bpy.context.scene.jewelcraft
		self.wm_props = bpy.context.window_manager.jewelcraft


# Presets
# ---------------------------


class VIEW3D_MT_JewelCraft_Weighting_Presets(Menu):
	"""Weighting presets"""
	bl_label = 'Presets'
	preset_subdir = 'jewelcraft_weighting'
	preset_operator = 'script.execute_preset'
	draw = Menu.draw_preset


# Menus
# ---------------------------


class VIEW3D_MT_JewelCraft_Select_Gem_By(Menu):
	"""Select gems by trait"""
	bl_label = 'Select Gems By...'

	def draw(self, context):
		layout = self.layout

		layout.operator('object.jewelcraft_select_gems_by_trait', text='Size', text_ctxt='Dative').filter_size = True
		layout.operator('object.jewelcraft_select_gems_by_trait', text='Stone', text_ctxt='Dative').filter_stone = True
		layout.operator('object.jewelcraft_select_gems_by_trait', text='Cut', text_ctxt='Dative').filter_cut = True
		layout.separator()
		layout.operator('object.jewelcraft_select_gems_by_trait', text='Similar').filter_similar = True
		layout.separator()
		layout.operator('object.jewelcraft_select_doubles', text='Doubles')
		layout.separator()
		layout.operator('object.jewelcraft_select_gems_by_trait', text='All')


class VIEW3D_MT_JewelCraft_Folder_Tools(Menu):
	"""Category tools"""
	bl_label = ''

	def draw(self, context):
		layout = self.layout

		layout.operator('wm.jewelcraft_asset_folder_create', icon='ZOOMIN')
		layout.operator('wm.jewelcraft_asset_folder_rename', icon='LINE_DATA')
		layout.separator()
		layout.operator('wm.jewelcraft_asset_library_open', text='Open Library Folder', icon='FILE_FOLDER')
		layout.separator()
		layout.operator('wm.jewelcraft_asset_ui_refresh', icon='FILE_REFRESH')


class VIEW3D_MT_JewelCraft_Asset_Tools(Menu):
	"""Asset tools"""
	bl_label = ''

	def draw(self, context):
		layout = self.layout

		layout.operator('wm.jewelcraft_asset_rename', text='Rename', icon='LINE_DATA')
		layout.operator('wm.jewelcraft_asset_replace', icon='GROUP')
		layout.operator('wm.jewelcraft_asset_preview_replace', text='Replace Preview', icon='IMAGE_DATA')


class VIEW3D_MT_JewelCraft_Alloy_Tools(Menu, Setup):
	"""Alloys set"""
	bl_label = ''

	def draw(self, context):
		layout = self.layout
		layout.label('Alloys Set:')
		layout.prop(self.prefs, 'alloys_set', text='')


class VIEW3D_MT_JewelCraft_Product_Report_Tools(Menu, Setup):
	"""Product report language"""
	bl_label = ''

	def draw(self, context):
		layout = self.layout
		layout.prop(self.prefs, 'product_report_display')
		layout.prop(self.prefs, 'product_report_save')
		layout.separator()
		layout.label('Report Language:')
		layout.prop(self.prefs, 'product_report_lang', text='')


# Panels
# ---------------------------


class VIEW3D_PT_JewelCraft_Gems(Panel, Setup):
	bl_label = 'Gems'

	@classmethod
	def poll(cls, context):
		return context.mode in {'OBJECT', 'EDIT_MESH'}

	def draw(self, context):

		# Updater
		# ------------------
		addon_updater_ops.check_for_update_background(context)
		addon_updater_ops.update_notice_box_ui(self, context)
		# ------------------

		layout = self.layout
		props = self.wm_props

		layout.template_icon_view(props, 'gem_cut', show_labels=True)

		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(props, 'gem_stone', text='')
		row.operator('view3d.jewelcraft_search_stone', text='', icon='VIEWZOOM')

		layout.operator('object.jewelcraft_gem_add', text='Make Gem')

		col = layout.column(align=True)
		col.label('Replace:')
		row = col.row(align=True)
		row.operator('object.jewelcraft_stone_replace', text='Stone')
		row.operator('object.jewelcraft_cut_replace', text='Cut', text_ctxt='JewelCraft')

		layout.menu('VIEW3D_MT_JewelCraft_Select_Gem_By')


class VIEW3D_PT_JewelCraft_Assets(Panel, Setup):
	bl_label = 'Assets'
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		return context.mode in {'OBJECT', 'EDIT_MESH'}

	def draw(self, context):
		layout = self.layout
		props = self.wm_props

		if not props.asset_folder:
			layout.operator('wm.jewelcraft_asset_folder_create', icon='ZOOMIN')
			layout.operator('wm.jewelcraft_asset_ui_refresh', icon='FILE_REFRESH')
			return

		row = layout.row(align=True)
		row.prop(props, 'asset_folder', text='')
		row.menu('VIEW3D_MT_JewelCraft_Folder_Tools', icon='SCRIPTWIN')

		row = layout.row()

		col = row.column()
		col.enabled = bool(props.asset_list)
		col.template_icon_view(props, 'asset_list', show_labels=True)
		if self.prefs.display_asset_name:
			col.label(props.asset_list)

		col = row.column(align=True)
		col.operator('wm.jewelcraft_asset_add_to_library', text='', icon='ZOOMIN')
		col.operator('wm.jewelcraft_asset_remove_from_library', text='', icon='ZOOMOUT')
		col.operator('view3d.jewelcraft_search_asset', text='', icon='VIEWZOOM')
		col.menu('VIEW3D_MT_JewelCraft_Asset_Tools', icon='SCRIPTWIN')

		layout.operator('wm.jewelcraft_asset_import', text='Import Asset')


class VIEW3D_PT_JewelCraft_Jeweling(Panel, Setup):
	bl_label = 'Jeweling'
	bl_context = 'objectmode'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.label('Add:')
		col.operator('object.jewelcraft_prongs_add', text='Prongs')
		col.operator('object.jewelcraft_cutter_add', text='Cutter')

		layout.operator('object.jewelcraft_make_dupliface', text='Make Dupli-face')

		row = layout.row(align=True)
		row.operator('object.jewelcraft_dist_helper_add', text='Distance Helper')
		row.operator('object.jewelcraft_dist_helper_add', text='', icon='X').remove = True

		col = layout.column(align=True)
		col.label('Deform:')
		row = col.row(align=True)
		row.operator('object.jewelcraft_scatter_along_curve', text='Scatter Along Curve')
		row.operator('object.jewelcraft_redistribute_along_curve', text='', icon='FILE_REFRESH')


class VIEW3D_PT_JewelCraft_Curve(Panel, Setup):
	bl_label = 'Curve'
	bl_context = 'objectmode'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.label('Add:')
		col.operator('curve.jewelcraft_size_curve_add', text='Size Curve', icon='CURVE_BEZCIRCLE')

		col = layout.column(align=True)
		col.label('Deform:')
		col.operator('object.jewelcraft_move_over_under', text='Over', icon='TRIA_UP')
		col.operator('object.jewelcraft_stretch_along_curve', text='Stretch', icon='ARROW_LEFTRIGHT')
		col.operator('object.jewelcraft_move_over_under', text='Under', icon='TRIA_DOWN').under = True

		col = layout.column(align=True)
		col.label('Report:')
		col.operator('curve.jewelcraft_length_display', text='Curve Length', icon='IPO_QUAD')


class VIEW3D_PT_JewelCraft_Curve_Editmesh(Panel, Setup):
	bl_label = 'Curve'
	bl_context = 'mesh_edit'

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.label('Deform:')
		col.operator('object.jewelcraft_stretch_along_curve', text='Stretch', icon='ARROW_LEFTRIGHT')


class VIEW3D_PT_JewelCraft_Object(Panel, Setup):
	bl_label = 'Object'
	bl_context = 'objectmode'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.operator('object.jewelcraft_object_mirror', text='Mirror Objects', icon='MOD_MIRROR')

		col = layout.column(align=True)
		col.label('Deform:')
		col.operator('object.jewelcraft_lattice_project', text='Lattice Project', icon='MOD_SHRINKWRAP')
		col.operator('object.jewelcraft_lattice_profile', text='Lattice Profile', icon='SPHERECURVE')


class VIEW3D_PT_JewelCraft_Weighting(Panel, Setup):
	bl_label = 'Weighting'
	bl_context = 'objectmode'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		props = self.wm_props

		row = layout.row(align=True)
		row.menu('VIEW3D_MT_JewelCraft_Weighting_Presets', text=VIEW3D_MT_JewelCraft_Weighting_Presets.bl_label)
		row.operator('view3d.jewelcraft_add_preset_weighting', text='', icon='ZOOMIN')
		row.operator('view3d.jewelcraft_add_preset_weighting', text='', icon='ZOOMOUT').remove_active = True

		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(props, 'weighting_mat', text='')
		row.menu('VIEW3D_MT_JewelCraft_Alloy_Tools', icon='SCRIPTWIN')
		row.operator('view3d.jewelcraft_search_alloy', text='', icon='VIEWZOOM')

		if props.weighting_mat == 'CUSTOM':
			col.prop(props, 'weighting_dens')

		layout.operator('mesh.jewelcraft_weight_display', text='Calculate')


class VIEW3D_PT_JewelCraft_Product_Report(Panel, Setup):
	bl_label = 'Product Report'
	bl_context = 'objectmode'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		scene_props = self.scene_props
		wm_props = self.wm_props
		scene = context.scene

		col_box = layout.column(align=True)

		box = col_box.box()
		box.prop(wm_props, 'product_report_sizes', icon=icon_tria(wm_props.product_report_sizes), emboss=False)
		if wm_props.product_report_sizes:
			col = box.column()
			col.prop_search(scene_props, 'product_report_ob_size', scene, 'objects')
			col.prop_search(scene_props, 'product_report_ob_shank', scene, 'objects')
			col.prop_search(scene_props, 'product_report_ob_dim', scene, 'objects', text='Dimensions', text_ctxt='JewelCraft')

		box = col_box.box()
		box.prop(wm_props, 'product_report_weighting', icon=icon_tria(wm_props.product_report_weighting), emboss=False)
		if wm_props.product_report_weighting:

			box.prop_search(scene_props, 'product_report_ob_weight', scene, 'objects', text='')

			col = box.column(align=True)
			col.enabled = scene_props.product_report_ob_weight is not None

			alloy_list = dynamic_lists.alloys(self, context)[:-2]

			for mat in alloy_list:
				col.prop(scene_props, 'product_report_mat_' + mat[0].lower(), text=mat[1])

			col.separator()

			col.prop(scene_props, 'product_report_mat_custom')

			sub = col.column()
			sub.enabled = scene_props.product_report_mat_custom
			sub.prop(scene_props, 'product_report_mat_custom_name')
			sub.prop(scene_props, 'product_report_mat_custom_dens')

		row = layout.row(align=True)
		row.operator('wm.jewelcraft_product_report', text='Product Report')
		row.menu('VIEW3D_MT_JewelCraft_Product_Report_Tools', icon='SCRIPTWIN')
