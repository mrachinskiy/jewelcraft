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

	# Corundum group
	'RUBY'           : 4.1, # g/cm³
	'SAPPHIRE'       : 4.1,

	# Beryl group
	'EMERALD'        : 2.76,
	'AQUAMARINE'     : 2.76,

	# Quartz group
	'QUARTZ'         : 2.65,
	'AMETHYST'       : 2.65,
	'CITRINE'        : 2.65,

	'DIAMOND'        : 3.53,
	'CUBIC_ZIRCONIA' : 5.9,
	'GARNET'         : 4.3,
	'SPINEL'         : 3.8,
	'TANZANITE'      : 3.38,
	'TOPAZ'          : 3.57,
	'TOURMALINE'     : 3.22,
	'PERIDOT'        : 3.34,
}

gem_volume_correction = {
	'ROUND'     : 1.3056,
	'OCTAGON'   : 1.4191,

	'OVAL'      : 1.34455,
	'PEAR'      : 1.24936,
	'MARQUISE'  : 1.20412,
	'HEART'     : 1.2294,

	'SQUARE'    : 1.684,
	'PRINCESS'  : 1.43301,
	'ASSCHER'   : 1.2557,
	'CUSHION'   : 1.1674,
	'RADIANT'   : 1.3494,
	'FLANDERS'  : 1.2726,

	'EMERALD'   : 0.9849,
	'BAGUETTE'  : 1.16507,

	'TRILLION'  : 1.68325,
	'TRILLIANT' : 1.5615,
}
