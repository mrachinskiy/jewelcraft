from bpy.types import PropertyGroup, AddonPreferences, Object
from bpy.props import (
	EnumProperty,
	BoolProperty,
	FloatProperty,
	StringProperty,
	PointerProperty,
	IntProperty,
	FloatVectorProperty,
	)

from . import var, dynamic_lists

# Extern
from . import addon_updater_ops


# Add-on preferences
# ------------------------------------------


def update_asset_refresh(self, context):
	dynamic_lists.asset_folder_list_refresh()
	dynamic_lists.asset_list_refresh(hard=True)


class PREFS_JewelCraft_Props(AddonPreferences):
	bl_idname = __package__

	active_section = EnumProperty(
		items=(('ASSET_MANAGER',  'Asset Manager',  ''),
		       ('WEIGHTING',      'Weighting',      ''),
		       ('PRODUCT_REPORT', 'Product Report', ''),
		       ('THEMES',         'Themes',         ''),
		       ('UPDATER',        'Updater',        '')),
		options={'SKIP_SAVE'},
		)

	asset_name_from_obj = BoolProperty(name='New asset name from active object', description='Use active object name when creating new asset')
	use_custom_asset_dir = BoolProperty(name='Use custom library folder', description='Set custom asset library folder, if disabled the default library folder will be used', update=update_asset_refresh)
	custom_asset_dir = StringProperty(name='Library Folder Path', description='Custom library folder path', subtype='DIR_PATH', update=update_asset_refresh)
	display_asset_name = BoolProperty(name='Display asset name', description='Display asset name in Tool Shelf')

	alloys_set = EnumProperty(
		name='Alloys Set',
		description='List of alloys for weighting',
		items=(('COMMON', 'Common', 'Common alloys, physical properties taken directly from suppliers'),
		       ('RU', 'RU (ГОСТ 30649-99, ГОСТ 15527-2004)', 'Russian regulations for precious alloys')),
		default='COMMON',
		)

	product_report_lang = EnumProperty(
		name='Report Language',
		description='Product report language',
		items=(('ru_RU', 'Russian (Русский)', ''),
		       ('en_US', 'English (English)', ''),
		       ('AUTO',  'Auto (Auto)',       'Use user preferences language setting')),
		default='AUTO',
		)
	product_report_display = BoolProperty(name='Display in a new window', description='Display product report in new window', default=True)
	product_report_save = BoolProperty(name='Save to file', description='Save product report to file in project folder', default=True)

	color_prongs = FloatVectorProperty(name='Prongs', default=(0.8, 0.8, 0.8), min=0.0, soft_max=1.0, subtype='COLOR')
	color_cutter = FloatVectorProperty(name='Cutter', default=(0.8, 0.8, 0.8), min=0.0, soft_max=1.0, subtype='COLOR')

	# Updater settings
	# ---------------------------

	auto_check_update = BoolProperty(
		name='Auto-check for Update',
		description='If enabled, auto-check for updates using an interval',
		default=True,
		)
	updater_intrval_months = IntProperty(
		name='Months',
		description='Number of months between checking for updates',
		default=0,
		min=0,
		)
	updater_intrval_days = IntProperty(
		name='Days',
		description='Number of days between checking for updates',
		default=7,
		min=0,
		)
	updater_intrval_hours = IntProperty(
		name='Hours',
		description='Number of hours between checking for updates',
		default=0,
		min=0,
		max=23,
		)
	updater_intrval_minutes = IntProperty(
		name='Minutes',
		description='Number of minutes between checking for updates',
		default=0,
		min=0,
		max=59,
		)

	def draw(self, context):
		layout = self.layout

		col = layout.column()
		col.row().prop(self, 'active_section', expand=True)
		col.separator()

		if self.active_section == 'ASSET_MANAGER':
			col = layout.column()
			col.prop(self, 'asset_name_from_obj')
			col.prop(self, 'display_asset_name')
			col.prop(self, 'use_custom_asset_dir')
			sub = col.row()
			sub.enabled = self.use_custom_asset_dir
			sub.prop(self, 'custom_asset_dir')

		elif self.active_section == 'WEIGHTING':
			layout.prop(self, 'alloys_set')

		elif self.active_section == 'PRODUCT_REPORT':
			col = layout.column()
			col.prop(self, 'product_report_display')
			col.prop(self, 'product_report_save')
			col.prop(self, 'product_report_lang')

		elif self.active_section == 'THEMES':
			col = layout.column_flow(3)
			col.prop(self, 'color_prongs')
			col.prop(self, 'color_cutter')

		elif self.active_section == 'UPDATER':
			addon_updater_ops.update_settings_ui(self, context)


# Window manager properties
# ------------------------------------------


def update_asset_list(self, context):
	dynamic_lists.asset_list_refresh()
	self.asset_list = dynamic_lists.assets(self, context)[0][0]


class WM_JewelCraft_Props(PropertyGroup):
	gem_cut = EnumProperty(items=dynamic_lists.cuts)
	gem_stone = EnumProperty(name='Stone', description='Stone', items=dynamic_lists.stones)

	asset_folder = EnumProperty(name='Category', description='Asset category', items=dynamic_lists.asset_folders, update=update_asset_list)
	asset_list = EnumProperty(items=dynamic_lists.assets)

	weighting_mat = EnumProperty(name='Material', description='Material', items=dynamic_lists.alloys)
	weighting_dens = FloatProperty(name='Density', description='Density g/cm³', default=1.0, min=0.01, step=1, precision=2)

	product_report_sizes = BoolProperty(name='Sizes')
	product_report_weighting = BoolProperty(name='Weighting')


# Scene properties
# ------------------------------------------


def generateprops(self):
	active_props = {'WG_18K_PD', 'WG_14K_PD', 'WG_750_NI', 'WG_585_NI', 'S_925'}

	for mat in var.alloy_density:
		val = mat in active_props
		setattr(self, 'product_report_mat_' + mat.lower(), BoolProperty(default=val))

	return self


@generateprops
class SCENE_JewelCraft_Props(PropertyGroup):
	product_report_ob_size = PointerProperty(type=Object, name='Size', description='Object for ring inner diameter reference')
	product_report_ob_shank = PointerProperty(type=Object, name='Shank', description='Object for shank width and height reference')
	product_report_ob_dim = PointerProperty(type=Object, name='Dimensions', description='Object for dimensions reference')
	product_report_ob_weight = PointerProperty(type=Object, name='Weighting', description='Object for weight reference')

	product_report_mat_custom = BoolProperty(name='Custom Material', description='Define custom material')
	product_report_mat_custom_name = StringProperty(name='Name', description='Name for the custom material')
	product_report_mat_custom_dens = FloatProperty(name='Density', description='Density g/cm³', default=1.0, min=0.01, step=1, precision=2)
