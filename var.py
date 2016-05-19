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

default_color = {
	'DIAMOND'        : [1.0, 1.0, 1.0],
	'CUBIC_ZIRCONIA' : [1.0, 1.0, 1.0],
	'RUBY'           : [0.57, 0.011, 0.005],
	'SPINEL'         : [0.57, 0.011, 0.005],
	'GARNET'         : [0.319, 0.0, 0.0],
	'MORGANITE'      : [0.41, 0.21, 0.09],
	'CITRINE'        : [1.0, 0.355, 0.0],
	'PERIDOT'        : [0.201, 0.748, 0.026],
	'EMERALD'        : [0.062, 0.748, 0.057],
	'AQUAMARINE'     : [0.0, 0.748, 1.0],
	'SAPPHIRE'       : [0.004, 0.019, 0.214],
	'TANZANITE'      : [0.004, 0.019, 0.214],
	'AMETHYST'       : [0.415, 0.041, 0.523],

	'PRONGS' : [0.8, 0.8, 0.8],
	'CUTTER' : [1.0, 1.0, 1.0],
}
