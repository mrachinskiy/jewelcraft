from os import path


addon_id = __package__
addon_path = path.dirname(__file__)
asset_filepath = path.join(addon_path, 'assets', 'gems.blend')
icons_path = path.join(addon_path, 'icons')


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
