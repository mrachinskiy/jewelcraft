bl_info = {
	"name": "JewelCraft",
	"author": "Mikhail Rachinskiy (jewelcourses.com)",
	"version": (1,3),
	"blender": (2,7,5),
	"location": "3D View → Tool Shelf",
	"description": "JewelCraft—add-on for jewelry design that provides tools for asset managment, jeweling and statistics gathering to easily get all valuable information about your jewelry product such as: gemstone settings, product dimensions and weight in different metals.",
	"wiki_url": "https://github.com/mrachinskiy/blender-addon-jewelcraft",
	"tracker_url": "https://github.com/mrachinskiy/blender-addon-jewelcraft/issues",
	"category": "Object"}

if "bpy" in locals():
	import importlib
	importlib.reload(var)
	importlib.reload(localization)
	importlib.reload(operators)
	importlib.reload(ui)
	importlib.reload(modules.icons)
	importlib.reload(modules.helpers)
	importlib.reload(modules.assets)
	importlib.reload(modules.stats)
	importlib.reload(modules.props_helpers)
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
	from .modules import props_helpers
	from .modules.icons import preview_collections




class JewelCraftPreferences(AddonPreferences):

	bl_idname = var.addon_id

	lang = EnumProperty(
		name="UI language",
		items=(
			('RU', "Russian (Русский)", ""),
			('EN', "English (English)", ""),
		),
		default="EN",
		description="Add-on UI language")


	def draw(self, context):
		layout = self.layout
		split = layout.split(percentage=.4)
		split.prop(self, 'lang')




class JewelCraftProperties(PropertyGroup):

	import_gem_type = EnumProperty(name="Type", items=props_helpers.gem_type)
	import_gem_cut = EnumProperty(name="Cut", items=props_helpers.gem_cut)
	import_gem_size = FloatProperty(name="Size", description="Set gemstone size", default=1.0, min=0.1, step=10, precision=2)


	weighting_metals = EnumProperty(name="Metals" , items=props_helpers.weighting_metals)
	weighting_custom = FloatProperty(description="Custom density (g/cm³)", default=1.0, min=0.01, step=1, precision=2)


	export_options = BoolProperty()

	export_size = StringProperty(description="Set object for size reference")
	export_shank = StringProperty(description="Set object for shank reference")
	export_dim = StringProperty(description="Set object for dimensions reference")
	export_weight = StringProperty(description="Set object for weight reference")

	export_metals     = BoolProperty()
	metal_24kt        = BoolProperty()
	metal_22kt        = BoolProperty()
	metal_18kt_white  = BoolProperty(default=True)
	metal_14kt_white  = BoolProperty(default=True)
	metal_18kt_yellow = BoolProperty()
	metal_14kt_yellow = BoolProperty()
	metal_silver      = BoolProperty()
	metal_palladium   = BoolProperty()
	metal_platinum    = BoolProperty()
	metal_custom         = BoolProperty()
	metal_custom_name    = StringProperty(description="Material name")
	metal_custom_density = FloatProperty(description="Custom density (g/cm³)", default=1.0, min=0.01, step=1, precision=2)

	lang = EnumProperty(
		name="Export stats language",
		items=(
			('RU',   "Russian (Русский)", ""),
			('EN',   "English (English)", ""),
			('AUTO', "Auto", "Inherit locale from add-on preferences"),
		),
		default="AUTO",
		description="Statistics language")


	# g/cm³
	metal_density = {
		'24KT'        : 19.3,
		'22KT'        : 17.8,
		'18KT_WHITE'  : 15.8,
		'14KT_WHITE'  : 14.6,
		'18KT_YELLOW' : 15.5,
		'14KT_YELLOW' : 13.8,
		'SILVER'      : 10.5,
		'PALLADIUM'   : 12.0,
		'PLATINUM'    : 21.4,
	}

	# g/cm³
	stone_density = {
		'DIAMOND'        : 3.53,
		'CUBIC_ZIRCONIA' : 5.9,
		'TOPAZ'          : 3.57,
		'EMERALD'        : 2.76,
		'RUBY'           : 4.1,
		'SAPPHIRE'       : 4.1,
	}

	gem_volume_correction = {
		'ROUND'    : 1.3056,
		'OVAL'     : 1.34455,
		'PEARL'    : 1.24936,
		'MARQUISE' : 1.20412,
		'SQUARE'   : 1.4,
		'BAGUETTE' : 1.555,
		'EMERALD'  : 1.45,
	}

	# mm:ct (MSU)
	diamonds_table = {
		 0.8:0.0025,
		 1.0:0.004, 1.1:0.005, 1.2:0.006, 1.3:0.008, 1.4:0.010, 1.5:0.012, 1.6:0.015, 1.7:0.018, 1.8:0.021, 1.9:0.025,
		 2.0:0.029, 2.1:0.034, 2.2:0.039, 2.3:0.045, 2.4:0.051, 2.5:0.057, 2.6:0.064, 2.7:0.072, 2.8:0.080, 2.9:0.089,
		 3.0:0.099, 3.1:0.109, 3.2:0.120, 3.3:0.132, 3.4:0.144, 3.5:0.157, 3.6:0.171, 3.7:0.185, 3.8:0.201, 3.9:0.217,
		 4.0:0.240, 4.1:0.257, 4.2:0.274, 4.3:0.294, 4.4:0.318, 4.5:0.340, 4.6:0.353, 4.7:0.380, 4.8:0.410, 4.9:0.430,
		 5.0:0.460, 5.1:0.490, 5.2:0.520, 5.3:0.540, 5.4:0.570, 5.5:0.620, 5.6:0.660, 5.7:0.690, 5.8:0.720, 5.9:0.740,
		 6.0:0.800, 6.1:0.840, 6.2:0.880, 6.3:0.900, 6.4:0.960, 6.5:1.010, 6.6:1.050, 6.7:1.080, 6.8:1.150, 6.9:1.190,
		 7.0:1.240,
	}




classes = (
	ui.JewelCraftImportPanel,
	ui.JewelCraftWeightingPanel,
	ui.JewelCraftExportPanel,

	operators.IMPORT_GEM,
	operators.IMPORT_TYPE,
	operators.IMPORT_CUT,
	operators.IMPORT_PRONGS,
	operators.IMPORT_SINGLE_PRONG,
	operators.IMPORT_CUTTER,
	operators.IMPORT_CUTTER_SEAT_ONLY,
	operators.IMPORT_IMITATION_3_PRONG,
	operators.MAKE_DUPLIFACE,
	operators.WEIGHT_DISPLAY,

	operators.EXPORT_PICK_SIZE,
	operators.EXPORT_PICK_SHANK,
	operators.EXPORT_PICK_DIM,
	operators.EXPORT_PICK_WEIGHT,
	operators.EXPORT_STATS,

	JewelCraftPreferences,
	JewelCraftProperties,
)




def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.jewelcraft = PointerProperty(type=JewelCraftProperties)


def unregister():
	pcoll_remove = bpy.utils.previews.remove
	for pcoll in preview_collections.values():
		pcoll_remove(pcoll)
	preview_collections.clear()

	for cls in classes:
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.jewelcraft


if __name__ == "__main__":
	register()
