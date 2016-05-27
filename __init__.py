bl_info = {
	'name': 'JewelCraft',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': (1, 6),
	'blender': (2, 77, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Jewelry design toolkit.',
	'wiki_url': 'https://github.com/mrachinskiy/blender-addon-jewelcraft#readme',
	'tracker_url': 'https://github.com/mrachinskiy/blender-addon-jewelcraft/issues',
	'category': 'Object'}


if 'bpy' in locals():
	from importlib import reload
	reload(var)
	reload(localization)
	reload(operators)
	reload(ui)
	reload(modules.icons)
	reload(modules.units)
	reload(modules.assets)
	reload(modules.stats)
	reload(modules.props_utility)
	del reload
else:
	import bpy
	from bpy.props import (
		EnumProperty,
		BoolProperty,
		FloatProperty,
		StringProperty,
		PointerProperty,
	)
	from bpy.types import (
		PropertyGroup,
		AddonPreferences,
	)
	from . import (
		var,
		operators,
		ui,
	)
	from .modules import props_utility
	from .modules.icons import preview_collections






class Preferences(AddonPreferences):

	bl_idname = var.addon_id

	lang = EnumProperty(
		name='UI language',
		items=(
			('RU', 'Russian (Русский)', ''),
			('EN', 'English',           ''),
		),
		default='EN',
		description='Add-on UI language')


	def draw(self, context):
		layout = self.layout
		split = layout.split(percentage=.4)
		split.prop(self, 'lang')






class Properties(PropertyGroup):

	make_gem_cut = EnumProperty(name='Cut', items=props_utility.cuts)
	make_gem_stone = EnumProperty(name='Stone', items=props_utility.stones)
	make_gem_size = FloatProperty(name='Size', description='Gem size', default=1.0, min=0.0, step=10, precision=2, unit='LENGTH')


	weighting_metals = EnumProperty(name='Metals' , items=props_utility.metals)
	weighting_custom = FloatProperty(description='Custom density (g/cm³)', default=1.0, min=0.01, step=1, precision=2)


	export_options = BoolProperty()

	export_size = StringProperty(description='Object for size reference')
	export_shank = StringProperty(description='Object for shank width and height reference')
	export_dim = StringProperty(description='Object for dimensions reference')
	export_weight = StringProperty(description='Object for weight reference')

	export_metals        = BoolProperty()
	export_m_24g         = BoolProperty()
	export_m_22g         = BoolProperty()
	export_m_18wg        = BoolProperty(default=True)
	export_m_18yg        = BoolProperty()
	export_m_14wg        = BoolProperty(default=True)
	export_m_14yg        = BoolProperty()
	export_m_ster        = BoolProperty()
	export_m_pd          = BoolProperty()
	export_m_pl          = BoolProperty()
	export_m_custom      = BoolProperty()
	export_m_custom_name = StringProperty(description='Material name')
	export_m_custom_dens = FloatProperty(description='Custom density (g/cm³)', default=1.0, min=0.01, step=1, precision=2)

	export_lang = EnumProperty(
		name='Export stats language',
		items=(
			('RU',   'Russian (Русский)', ''),
			('EN',   'English',           ''),
			('AUTO', 'Auto',              'Inherit locale from add-on preferences'),
		),
		default='AUTO',
		description='Statistics language')






classes = (
	ui.ImportPanel,
	ui.WeightingPanel,
	ui.ExportPanel,

	operators.SEARCH_STONE,

	operators.MAKE_GEM,
	operators.REPLACE_STONE,
	operators.REPLACE_CUT,

	operators.MAKE_PRONGS,
	operators.MAKE_SINGLE_PRONG,
	operators.MAKE_CUTTER,
	operators.MAKE_CUTTER_SEAT,
	operators.MAKE_IMITATION,

	operators.MAKE_DUPLIFACE,
	operators.SELECT_DOUBLES,

	operators.WEIGHT_DISPLAY,

	operators.EXPORT_PICK_SIZE,
	operators.EXPORT_PICK_SHANK,
	operators.EXPORT_PICK_DIM,
	operators.EXPORT_PICK_WEIGHT,
	operators.EXPORT_STATS,

	Preferences,
	Properties,
)






def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.jewelcraft = PointerProperty(type=Properties)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.jewelcraft

	pcoll_remove = bpy.utils.previews.remove
	for pcoll in preview_collections.values():
		pcoll_remove(pcoll)
	preview_collections.clear()


if __name__ == '__main__':
	register()
