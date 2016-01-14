from os import path


addon_id = __package__
addon_path = path.dirname(__file__)
asset_filepath = path.join(addon_path, 'assets', 'gems.blend')
icons_path = path.join(addon_path, 'icons')


metal_density = {
	'24KT'        : 19.3, # g/cm³
	'22KT'        : 17.8,
	'18KT_WHITE'  : 15.8,
	'14KT_WHITE'  : 14.6,
	'18KT_YELLOW' : 15.5,
	'14KT_YELLOW' : 13.8,
	'STERLING'    : 10.36,
	'PALLADIUM'   : 12.0,
	'PLATINUM'    : 21.4,
}

stone_density = {
	'DIAMOND'        : 3.53, # g/cm³

	# Corundum group
	'RUBY'           : 4.1,
	'SAPPHIRE'       : 4.1,

	# Beryl group
	'EMERALD'        : 2.76,
	'AQUAMARINE'     : 2.76,

	# Quartz group
	'QUARTZ'         : 2.65,
	'AMETHYST'       : 2.65,
	'CITRINE'        : 2.65,

	'CUBIC_ZIRCONIA' : 5.9,
	'GARNET'         : 4.3,
	'SPINEL'         : 3.8,
	'TANZANITE'      : 3.38,
	'TOPAZ'          : 3.57,
	'TOURMALINE'     : 3.22,
}

gem_volume_correction = {
	'ROUND'    : 1.3056,
	'OVAL'     : 1.34455,

	'PEARL'    : 1.24936,
	'MARQUISE' : 1.20412,

	'SQUARE'   : 1.4,
	'PRINCESS' : 1.43301,

	'EMERALD'  : 1.45,
	'BAGUETTE' : 1.555,

	'ASSCHER'  : 1.2557,
	'CUSHION'  : 1.1674,

	'TRILLION' : 1.68325,
}
