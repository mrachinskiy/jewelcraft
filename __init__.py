bl_info = {
	'name': 'JewelCraft',
	'author': 'Mikhail Rachinskiy (jewelcourses.com)',
	'version': (1, 6),
	'blender': (2, 77, 0),
	'location': '3D View > Tool Shelf',
	'description': 'Jewelry design toolkit.',
	'wiki_url': 'https://github.com/mrachinskiy/jewelcraft#readme',
	'tracker_url': 'https://github.com/mrachinskiy/jewelcraft/issues',
	'category': 'Object',
	}


if 'bpy' in locals():
	import importlib
	importlib.reload(var)
	importlib.reload(locale)
	importlib.reload(ui)
	importlib.reload(operators)
	importlib.reload(previews)
	importlib.reload(prop_items)
	importlib.reload(stats)
else:
	import bpy
	import bpy.utils.previews
	from bpy.types import (
		PropertyGroup,
		AddonPreferences,
		)
	from bpy.props import (
		EnumProperty,
		BoolProperty,
		FloatProperty,
		StringProperty,
		PointerProperty,
		)
	from . import (
		var,
		ui,
		operators,
		prop_items,
		previews,
		)


class Preferences(AddonPreferences):
	bl_idname = var.addon_id

	lang = EnumProperty(
		name='UI language',
		items=(('RU', 'Russian (Русский)', ''),
		       ('EN', 'English',           '')),
		default='EN',
		description='Add-on UI language',
		)

	def draw(self, context):
		layout = self.layout
		split = layout.split(percentage=0.15)

		col = split.column()
		col.label('UI Language:')

		col = split.column()
		colrow = col.row()
		colrow.alignment = 'LEFT'
		colrow.prop(self, 'lang', text='')


class Properties(PropertyGroup):
	gem_cut = EnumProperty(name='Cut', items=prop_items.cuts)
	gem_stone = EnumProperty(name='Stone', items=prop_items.stones)
	gem_size = FloatProperty(name='Size', description='Gem size', default=1.0, min=0.0, step=10, precision=2, unit='LENGTH')

	weighting_metals = EnumProperty(name='Metals', items=prop_items.metals)
	weighting_custom = FloatProperty(description='Custom density (g/cm³)', default=1.0, min=0.01, step=1, precision=2)

	stats_options = BoolProperty()
	stats_size = StringProperty(description='Object for size reference')
	stats_shank = StringProperty(description='Object for shank width and height reference')
	stats_dim = StringProperty(description='Object for dimensions reference')
	stats_weight = StringProperty(description='Object for weight reference')
	stats_metals = BoolProperty()
	stats_24g  = BoolProperty()
	stats_22g  = BoolProperty()
	stats_18wg = BoolProperty(default=True)
	stats_18yg = BoolProperty()
	stats_14wg = BoolProperty(default=True)
	stats_14yg = BoolProperty()
	stats_ster = BoolProperty()
	stats_pd   = BoolProperty()
	stats_pl   = BoolProperty()
	stats_custom = BoolProperty()
	stats_custom_name = StringProperty(description='Material name')
	stats_custom_dens = weighting_custom
	stats_lang = EnumProperty(
		name='Export stats language',
		items=(('RU',   'Russian (Русский)', ''),
		       ('EN',   'English',           ''),
		       ('AUTO', 'Auto',              'Inherit locale from add-on preferences')),
		default='AUTO',
		description='Statistics language',
		)


classes = (
	Preferences,
	Properties,

	ui.Gems,
	ui.Weighting,
	ui.Stats,

	operators.SEARCH_STONE,
	operators.MAKE_GEM,
	operators.REPLACE_STONE,
	operators.REPLACE_CUT,
	operators.MAKE_PRONGS,
	operators.MAKE_CUTTER,
	operators.MAKE_SINGLE_PRONG,
	operators.MAKE_IMITATION,
	operators.MAKE_DUPLIFACE,
	operators.SELECT_DOUBLES,

	operators.WEIGHT_DISPLAY,

	operators.STATS_EXPORT,
	operators.STATS_PICK,
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
	for pcoll in previews.preview_collections.values():
		pcoll_remove(pcoll)
	previews.preview_collections.clear()


if __name__ == '__main__':
	register()
