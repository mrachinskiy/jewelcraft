import os
import sys


if sys.platform == 'win32':
	local_path = os.getenv('LOCALAPPDATA')
elif sys.platform == 'darwin':
	local_path = os.path.expanduser('~/Library/Application Support')
else:
	local_path = os.path.expanduser('~/.local/share')


addon_id = __package__
addon_dir = os.path.dirname(__file__)

gem_asset_dir = os.path.join(addon_dir, 'assets', 'gems')
gem_asset_filepath = os.path.join(gem_asset_dir, 'gems.blend')

user_asset_dir = os.path.join(local_path, 'Blender', 'JewelCraft', 'Asset Library', 'Object')


alloy_density = {

	# g/cm³

	# Gold
	# ----------------------------

	'YG_24K': 19.3,  # Au 99.9% (Зл 999,9)
	'YG_22K': 17.86,  # Au 91.6%, Ag 4.9%, Cu 3.5%
	'YG_18K': 15.53,  # Au 75.3%, Ag 16.5, Cu 6.7%, Zn 1.5%
	'YG_14K': 13.05,  # Au 58.4%, Ag 9.8%, Cu 28%, Zn 3.8%
	'YG_10K': 11.47,  # Au 41.7%, Ag 11.2%, Cu 40.5%, Zn 6.6%
	'WG_18K_PD': 15.66,  # Au 78.7%, Cu 8.3%, Pd 13%
	'WG_18K_NI': 14.69,  # Au 75.15%, Cu 8.75%, Ni 12%, Zn 4.1%
	'WG_14K_PD': 14.6,  # Au 58.55%, Cu 7.2%, Ag 20%, Pd 13.5%, Zn 0.75%
	'WG_14K_NI': 12.61,  # Au 58.43%, Cu 21%, Ni 12.73%, Zn 7.84%
	'WG_10K': 10.99,  # Au 41.7%, Cu 35.7%, Ni 10.3%, Zn 12.3%
	'RG_18K': 15.02,  # Au 75.3%, Cu 23.3%, Ag 1.2%, Zn 0.2%
	'RG_14K': 13.03,  # Au 58.4%, Cu 39.2%, Ag 2%, Zn 0.4%
	'RG_10K': 11.52,  # Au 41.5%, Cu 55%, Ag 3%, Zn 0.5%

	'YG_958': 18.52,  # ЗлСрМ 958-20
	'YG_750': 15.53,  # ЗлСрМ 750-150
	'YG_585': 13.92,  # ЗлСрМ 585-300
	'YG_375': 11.74,  # ЗлСрМ 375-250
	'WG_750_PD': 16.44,  # ЗлСрПд 750-100-150
	'WG_750_NI': 15.38,  # ЗлСрНЦ 750-150-7,5
	'WG_585_PD': 14.76,  # ЗлСрПд 585-255-160
	'WG_585_NI': 12.85,  # ЗлНЦМ 585-12,5-4
	'RG_585': 13.24,  # ЗлСрМ 585-80
	'RG_375': 11.54,  # ЗлСрМ 375-160

	# Platinum
	# ----------------------------

	'PT_950': 20.7,  # Pt 95%, Ru 5% (ПлРд 950-50) [Pt/Ru and Pt/Rh have similar density]
	'PT_900': 21.54,  # Pt 90%, Ir 10% (ПлИ 900-100)

	# Palladium
	# ----------------------------

	'PD_950': 12.16,  # Pd 95%, Ru 5% (ПдРу 950-50)

	# Silver
	# ----------------------------

	'S_925': 10.36,  # Ag 92.5%, Cu 7.5% (СрМ 925)
	'S_ARGT': 10.3,  # Argentium 935 Pro

	# Brass
	# ----------------------------

	'BRASS': 8.66,  # Cu 85%, Zn 15% (Л85)
	}


stone_density = {

	# g/cm³

	# Corundum group
	'RUBY': 4.1,
	'SAPPHIRE': 4.1,

	# Beryl group
	'AQUAMARINE': 2.76,
	'EMERALD': 2.76,
	'MORGANITE': 2.76,

	# Quartz group
	'AMETHYST': 2.65,
	'CITRINE': 2.65,
	'QUARTZ': 2.65,

	'ALEXANDRITE': 3.73,
	'CUBIC_ZIRCONIA': 5.9,
	'DIAMOND': 3.53,
	'GARNET': 4.3,
	'PERIDOT': 3.34,
	'SPINEL': 3.8,
	'TANZANITE': 3.38,
	'TOPAZ': 3.57,
	'TOURMALINE': 3.22,
	'ZIRCON': 4.73,
	}


gem_volume_correction = {

	# Approximation groups

	# Cone
	'ROUND': 1.3056,
	'OCTAGON': 1.35,
	'OVAL': 1.34455,
	'PEAR': 1.24936,
	'MARQUISE': 1.20412,
	'HEART': 1.29,

	# Pyramid
	'SQUARE': 1.6,
	'PRINCESS': 1.43301,
	'ASSCHER': 1.379,
	'CUSHION': 1.2852,
	'RADIANT': 1.3494,
	'FLANDERS': 1.2407,

	# Prism
	'EMERALD': 1.025,
	'BAGUETTE': 1.197,

	# Tetrahedron
	'TRILLION': 1.669,
	'TRILLIANT': 1.91,
	'TRIANGLE': 1.522,
	}


default_color = {
	'DIAMOND': [1.0, 1.0, 1.0],
	'CUBIC_ZIRCONIA': [1.0, 1.0, 1.0],

	'RUBY': [0.57, 0.011, 0.005],
	'SPINEL': [0.57, 0.011, 0.005],

	'SAPPHIRE': [0.004, 0.019, 0.214],
	'TANZANITE': [0.004, 0.019, 0.214],

	'ALEXANDRITE': [0.153, 0.0705, 0.595],
	'AMETHYST': [0.415, 0.041, 0.523],
	'AQUAMARINE': [0.0, 0.748, 1.0],
	'CITRINE': [1.0, 0.355, 0.0],
	'EMERALD': [0.062, 0.748, 0.057],
	'GARNET': [0.319, 0.0, 0.0],
	'MORGANITE': [0.41, 0.21, 0.09],
	'PERIDOT': [0.201, 0.748, 0.026],
	}
