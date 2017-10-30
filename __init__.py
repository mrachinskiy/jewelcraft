bl_info = {
	'name': 'JewelCraft',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': (2, 0, 0),
	'blender': (2, 79, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Jewelry design toolkit.',
	'wiki_url': 'https://github.com/mrachinskiy/jewelcraft#readme',
	'tracker_url': 'https://github.com/mrachinskiy/jewelcraft/issues',
	'category': 'Object',
	}


if 'bpy' in locals():
	import importlib
	import os

	for entry in os.scandir(var.addon_dir):

		if entry.is_file() and entry.name.endswith('.py') and not entry.name.startswith('__'):
			_module = entry.name[:-3]
			importlib.reload(eval(_module))

		elif entry.is_dir() and not entry.name.startswith(('.', '__')) and not entry.name.endswith('updater'):

			for subentry in os.scandir(entry.path):

				if subentry.name.endswith('.py'):
					_module = '{}.{}'.format(entry.name, subentry.name[:-3])
					importlib.reload(eval(_module))
else:
	import bpy
	import bpy.utils.previews
	from bpy.props import PointerProperty

	from . import var, ui, locale, preferences, dynamic_lists
	from .op_cutter import cutter_op
	from .op_prongs import prongs_op
	from .op_scatter import scatter_op
	from .op_product_report import product_report_op
	from .ops_asset import asset_ops, folder_ops
	from .ops_curve import curve_ops
	from .ops_gem import gem_ops, gem_select_ops
	from .ops_jeweling import jeweling_ops
	from .ops_object import object_ops
	from .ops_utils import presets_ops, search_ops

	# Extern
	from . import addon_updater_ops


classes = (
	preferences.PREFS_JewelCraft_Props,
	preferences.WM_JewelCraft_Props,
	preferences.SCENE_JewelCraft_Props,

	ui.VIEW3D_MT_JewelCraft_Weighting_Presets,
	ui.VIEW3D_MT_JewelCraft_Select_Gem_By,
	ui.VIEW3D_MT_JewelCraft_Folder_Tools,
	ui.VIEW3D_MT_JewelCraft_Asset_Tools,
	ui.VIEW3D_MT_JewelCraft_Alloy_Tools,
	ui.VIEW3D_MT_JewelCraft_Product_Report_Tools,

	ui.VIEW3D_PT_JewelCraft_Gems,
	ui.VIEW3D_PT_JewelCraft_Assets,
	ui.VIEW3D_PT_JewelCraft_Jeweling,
	ui.VIEW3D_PT_JewelCraft_Curve,
	ui.VIEW3D_PT_JewelCraft_Curve_Editmesh,
	ui.VIEW3D_PT_JewelCraft_Object,
	ui.VIEW3D_PT_JewelCraft_Weighting,
	ui.VIEW3D_PT_JewelCraft_Product_Report,

	prongs_op.OBJECT_OT_JewelCraft_Prongs_Add,
	cutter_op.OBJECT_OT_JewelCraft_Cutter_Add,
	scatter_op.OBJECT_OT_JewelCraft_Scatter_Along_Curve,
	scatter_op.OBJECT_OT_JewelCraft_Redistribute_Along_Curve,
	product_report_op.WM_OT_JewelCraft_Product_Report,

	gem_ops.OBJECT_OT_JewelCraft_Gem_Add,
	gem_ops.OBJECT_OT_JewelCraft_Stone_Replace,
	gem_ops.OBJECT_OT_JewelCraft_Cut_Replace,
	gem_ops.OBJECT_OT_JewelCraft_Gem_ID_Add,

	gem_select_ops.OBJECT_OT_JewelCraft_Select_Gems_By_Trait,
	gem_select_ops.OBJECT_OT_JewelCraft_Select_Doubles,

	folder_ops.WM_OT_JewelCraft_Asset_Library_Open,
	folder_ops.WM_OT_JewelCraft_Asset_Folder_Create,
	folder_ops.WM_OT_JewelCraft_Asset_Folder_Rename,
	folder_ops.WM_OT_JewelCraft_Asset_UI_Refresh,

	asset_ops.WM_OT_JewelCraft_Asset_Add_To_Library,
	asset_ops.WM_OT_JewelCraft_Asset_Remove_From_Library,
	asset_ops.WM_OT_JewelCraft_Asset_Rename,
	asset_ops.WM_OT_JewelCraft_Asset_Replace,
	asset_ops.WM_OT_JewelCraft_Asset_Preview_Replace,
	asset_ops.WM_OT_JewelCraft_Asset_Import,

	jeweling_ops.OBJECT_OT_JewelCraft_Make_Dupliface,
	jeweling_ops.OBJECT_OT_JewelCraft_Dist_Helper_Add,

	curve_ops.CURVE_OT_JewelCraft_Size_Curve_Add,
	curve_ops.CURVE_OT_JewelCraft_Length_Display,
	curve_ops.OBJECT_OT_JewelCraft_Stretch_Along_Curve,
	curve_ops.OBJECT_OT_JewelCraft_Move_Over_Under,

	object_ops.OBJECT_OT_JewelCraft_Object_Mirror,
	object_ops.OBJECT_OT_JewelCraft_Lattice_Project,
	object_ops.OBJECT_OT_JewelCraft_Lattice_Profile,
	object_ops.MESH_OT_JewelCraft_Weight_Display,

	presets_ops.VIEW3D_OT_JewelCraft_Add_Preset_Weighting,

	search_ops.VIEW3D_OT_JewelCraft_Search_Stone,
	search_ops.VIEW3D_OT_JewelCraft_Search_Alloy,
	search_ops.VIEW3D_OT_JewelCraft_Search_Asset,
	)


def register():
	addon_updater_ops.register(bl_info)

	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.WindowManager.jewelcraft = PointerProperty(type=preferences.WM_JewelCraft_Props)
	bpy.types.Scene.jewelcraft = PointerProperty(type=preferences.SCENE_JewelCraft_Props)

	bpy.app.translations.register(__name__, locale.lc_reg)


def unregister():
	addon_updater_ops.unregister()

	for cls in classes:
		bpy.utils.unregister_class(cls)

	del bpy.types.WindowManager.jewelcraft
	del bpy.types.Scene.jewelcraft

	bpy.app.translations.unregister(__name__)

	# Previews
	# ---------------------------

	for pcoll in ui.preview_collections.values():
		bpy.utils.previews.remove(pcoll)

	ui.preview_collections.clear()
	dynamic_lists._cache.clear()


if __name__ == '__main__':
	register()
