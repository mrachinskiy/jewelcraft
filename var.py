from os import path


addon_id = __package__
addon_path = path.dirname(__file__)
asset_filepath = path.join(addon_path, 'assets', 'gems.blend')
icons_path = path.join(addon_path, 'icons')


metal_density = {
	'24G'  : 19.3, # g/cm³
	'22G'  : 17.8,
	'18WG' : 15.8,
	'14WG' : 14.6,
	'18YG' : 15.5,
	'14YG' : 13.8,
	'STER' : 10.36,
	'PD'   : 12.0,
	'PL'   : 21.4,
}

stone_density = {

	# Corundum group
	'RUBY'           : 4.1, # g/cm³
	'SAPPHIRE'       : 4.1,

	# Beryl group
	'EMERALD'        : 2.76,
	'AQUAMARINE'     : 2.76,
	'MORGANITE'      : 2.76,

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
	'ZIRCON'         : 4.73,
}

gem_volume_correction = {

	# Approximation groups

	# Cone
	'ROUND'     : 1.3056,
	'OCTAGON'   : 1.35,

	# Cone rectangular
	'OVAL'      : 1.34455,
	'PEAR'      : 1.24936,
	'MARQUISE'  : 1.20412,
	'HEART'     : 1.29,

	# Pyramid
	'SQUARE'    : 1.6,
	'PRINCESS'  : 1.43301,
	'ASSCHER'   : 1.379,
	'CUSHION'   : 1.2852,
	'RADIANT'   : 1.3494,
	'FLANDERS'  : 1.2407,

	# Prism
	'EMERALD'   : 1.025,
	'BAGUETTE'  : 1.197,

	# Tetrahedron
	'TRILLION'  : 1.669,
	'TRILLIANT' : 1.91,
	'TRIANGLE'  : 1.522,
}
