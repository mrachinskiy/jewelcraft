from bpy.types import Operator
from bl_operators.presets import AddPresetBase


class VIEW3D_OT_JewelCraft_Add_Preset_Weighting(AddPresetBase, Operator):
	"""Add or remove weighting preset"""
	bl_label = 'Add Weighting Preset'
	bl_idname = 'view3d.jewelcraft_add_preset_weighting'
	preset_menu = 'VIEW3D_MT_JewelCraft_Weighting_Presets'

	preset_defines = [
		'props = bpy.context.window_manager.jewelcraft'
		]

	preset_values = [
		'props.weighting_mat',
		'props.weighting_dens',
		]

	preset_subdir = 'jewelcraft_weighting'
