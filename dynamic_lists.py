import os

from bpy.app.translations import pgettext_iface as _
import bpy.utils.previews

from . import var, ui
from .locale import iface_lang
from .lib.asset import user_asset_library_folder


_cache = {}


def cuts(self, context):
	lang = iface_lang()

	if _cache.get('cuts__lang') == lang:
		return _cache['cuts__list']

	if 'cuts' in ui.preview_collections:
		pcoll = ui.preview_collections['cuts']
	else:
		pcoll = bpy.utils.previews.new()

		for entry in os.scandir(var.gem_asset_dir):
			if entry.name.endswith('.png'):
				name = os.path.splitext(entry.name)[0]
				pcoll.load(name, entry.path, 'IMAGE')

		ui.preview_collections['cuts'] = pcoll

	list_ = (
		('ROUND',     _('Round'),     '', pcoll['round'].icon_id,     0),
		('OVAL',      _('Oval'),      '', pcoll['oval'].icon_id,      1),
		('CUSHION',   _('Cushion'),   '', pcoll['cushion'].icon_id,   2),
		('PEAR',      _('Pear'),      '', pcoll['pear'].icon_id,      3),
		('MARQUISE',  _('Marquise'),  '', pcoll['marquise'].icon_id,  4),
		('PRINCESS',  _('Princess'),  '', pcoll['princess'].icon_id,  5),
		('BAGUETTE',  _('Baguette'),  '', pcoll['baguette'].icon_id,  6),
		('SQUARE',    _('Square'),    '', pcoll['square'].icon_id,    7),
		('EMERALD',   _('Emerald'),   '', pcoll['emerald'].icon_id,   8),
		('ASSCHER',   _('Asscher'),   '', pcoll['asscher'].icon_id,   9),
		('RADIANT',   _('Radiant'),   '', pcoll['radiant'].icon_id,   10),
		('FLANDERS',  _('Flanders'),  '', pcoll['flanders'].icon_id,  11),
		('OCTAGON',   _('Octagon'),   '', pcoll['octagon'].icon_id,   12),
		('HEART',     _('Heart'),     '', pcoll['heart'].icon_id,     13),
		('TRILLION',  _('Trillion'),  '', pcoll['trillion'].icon_id,  14),
		('TRILLIANT', _('Trilliant'), '', pcoll['trilliant'].icon_id, 15),
		('TRIANGLE',  _('Triangle'),  '', pcoll['triangle'].icon_id,  16),
		)

	_cache['cuts__list'] = list_
	_cache['cuts__lang'] = lang

	return list_


def stones(self, context):
	lang = iface_lang()

	if _cache.get('stones__lang') == lang:
		return _cache['stones__list']

	list_ = [
		('DIAMOND',        'Diamond',        '', 0),
		('ALEXANDRITE',    'Alexandrite',    '', 1),
		('AMETHYST',       'Amethyst',       '', 2),
		('AQUAMARINE',     'Aquamarine',     '', 3),
		('CITRINE',        'Citrine',        '', 4),
		('CUBIC_ZIRCONIA', 'Cubic Zirconia', '', 5),
		('EMERALD',        'Emerald',        '', 6),
		('GARNET',         'Garnet',         '', 7),
		('MORGANITE',      'Morganite',      '', 8),
		('QUARTZ',         'Quartz',         '', 9),
		('PERIDOT',        'Peridot',        '', 10),
		('RUBY',           'Ruby',           '', 11),
		('SAPPHIRE',       'Sapphire',       '', 12),
		('SPINEL',         'Spinel',         '', 13),
		('TANZANITE',      'Tanzanite',      '', 14),
		('TOPAZ',          'Topaz',          '', 15),
		('TOURMALINE',     'Tourmaline',     '', 16),
		('ZIRCON',         'Zircon',         '', 17),
		]

	list_.sort(key=lambda x: x[1])

	_cache['stones__list'] = list_
	_cache['stones__lang'] = lang

	return list_


def alloys(self, context):
	lang = iface_lang()
	alloys_set = context.user_preferences.addons[__package__].preferences.alloys_set

	if _cache.get('alloys__lang') == lang and _cache.get('alloys__set') == alloys_set:
		return _cache['alloys__list']

	if alloys_set == 'RU':
		list_ = [
			('YG_24K',    'Yellow Gold 999',   'Зл 999,9',           12),
			('YG_958',    'Yellow Gold 958',   'ЗлСрМ 958-20',       13),
			('YG_750',    'Yellow Gold 750',   'ЗлСрМ 750-150',      14),
			('YG_585',    'Yellow Gold 585',   'ЗлСрМ 585-300',      15),
			('YG_375',    'Yellow Gold 375',   'ЗлСрМ 375-250',      16),
			('WG_750_PD', 'White Gold 750 Pd', 'ЗлСрПд 750-100-150', 17),
			('WG_750_NI', 'White Gold 750 Ni', 'ЗлСрНЦ 750-150-7,5', 0),
			('WG_585_PD', 'White Gold 585 Pd', 'ЗлСрПд 585-255-160', 1),
			('WG_585_NI', 'White Gold 585 Ni', 'ЗлНЦМ 585-12,5-4',   2),
			('RG_585',    'Red Gold 585',      'ЗлСрМ 585-80',       3),
			('RG_375',    'Red Gold 375',      'ЗлСрМ 375-160',      4),
			('PT_950',    'Platinum 950',      'ПлРд 950-50',        5),
			('PT_900',    'Platinum 900',      'ПлИ 900-100',        6),
			('PD_950',    'Palladium 950',     'ПдРу 950-50',        7),
			('S_925',     'Silver 925',        'СрМ 925',            8),
			('BRASS',     'Brass',             'Л85',                9),
			('CUSTOM',    'Custom Density',    '',                   10),
			('VOLUME',    'Volume',            '',                   11),
			]
	else:
		list_ = [
			('YG_24K',    'Yellow Gold 24K',   'Au 99.9%',                                       16),
			('YG_22K',    'Yellow Gold 22K',   'Au 91.6%, Ag 4.9%, Cu 3.5%',                     17),
			('YG_18K',    'Yellow Gold 18K',   'Au 75.3%, Ag 16.5, Cu 6.7%, Zn 1.5%',            18),
			('YG_14K',    'Yellow Gold 14K',   'Au 58.4%, Ag 9.8%, Cu 28%, Zn 3.8%',             19),
			('YG_10K',    'Yellow Gold 10K',   'Au 41.7%, Ag 11.2%, Cu 40.5%, Zn 6.6%',          20),
			('WG_18K_PD', 'White Gold 18K Pd', 'Au 78.7%, Cu 8.3%, Pd 13%',                      0),
			('WG_18K_NI', 'White Gold 18K Ni', 'Au 75.15%, Cu 8.75%, Ni 12%, Zn 4.1%',           1),
			('WG_14K_PD', 'White Gold 14K Pd', 'Au 58.55%, Cu 7.2%, Ag 20%, Pd 13.5%, Zn 0.75%', 2),
			('WG_14K_NI', 'White Gold 14K Ni', 'Au 58.43%, Cu 21%, Ni 12.73%, Zn 7.84%',         3),
			('WG_10K',    'White Gold 10K',    'Au 41.7%, Cu 35.7%, Ni 10.3%, Zn 12.3%',         4),
			('RG_18K',    'Rose Gold 18K',     'Au 75.3%, Cu 23.3%, Ag 1.2%, Zn 0.2%',           5),
			('RG_14K',    'Rose Gold 14K',     'Au 58.4%, Cu 39.2%, Ag 2%, Zn 0.4%',             6),
			('RG_10K',    'Rose Gold 10K',     'Au 41.5%, Cu 55%, Ag 3%, Zn 0.5%',               7),
			('PT_950',    'Platinum 950',      'Pt 95%, Ru 5%',                                  8),
			('PT_900',    'Platinum 900',      'Pt 90%, Ir 10%',                                 9),
			('PD_950',    'Palladium 950',     'Pd 95%, Ru 5%',                                  10),
			('S_925',     'Silver Sterling',   'Ag 92.5%, Cu 7.5%',                              11),
			('S_ARGT',    'Silver Argentium',  'Argentium 935 Pro',                              12),
			('BRASS',     'Brass',             'Cu 85%, Zn 15%',                                 13),
			('CUSTOM',    'Custom Density',    '',                                               14),
			('VOLUME',    'Volume',            '',                                               15),
			]

	_cache['alloys__lang'] = lang
	_cache['alloys__set'] = alloys_set
	_cache['alloys__list'] = list_

	return list_


# Assets
# ---------------------------


def asset_folders(self, context):

	if 'asset_folders__list' in _cache:
		return _cache['asset_folders__list']

	folder = user_asset_library_folder()

	if not os.path.exists(folder):
		_cache['asset_folders__list'] = [('','','')]
		return [('','','')]

	list_ = []

	for entry in os.scandir(folder):
		if entry.is_dir() and not entry.name.startswith('.'):
			id_ = entry.name
			name_ = entry.name + ' '  # Add trailing space so UI translation won't apply
			list_.append((id_, name_, ''))

	if not list_:
		list_ = [('','','')]

	_cache['asset_folders__list'] = list_

	return list_


def assets(self, context):
	category = context.window_manager.jewelcraft.asset_folder

	if 'assets__list' in _cache and category == _cache.get('assets__category'):
		return _cache['assets__list']

	_cache['assets__category'] = category
	folder = os.path.join(user_asset_library_folder(), category)

	if not os.path.exists(folder):
		_cache['assets__list'] = [('','','')]
		return [('','','')]

	if 'assets' in ui.preview_collections:
		pcoll = ui.preview_collections['assets']
	else:
		pcoll = bpy.utils.previews.new()

	list_ = []
	i = 0

	for entry in os.scandir(folder):
		if entry.name.endswith('.png'):
			filename = os.path.splitext(entry.name)[0]
			id_ = filename
			name_ = filename + ' '  # Add trailing space so UI translation won't apply
			preview_id = category + filename

			if preview_id not in pcoll:
				pcoll.load(preview_id, entry.path, 'IMAGE')

			list_.append((id_, name_, '', pcoll[preview_id].icon_id, i))
			i += 1

	ui.preview_collections['assets'] = pcoll

	if not list_:
		list_ = [('','','')]

	_cache['assets__list'] = list_

	return list_


def asset_folder_list_refresh():
	try:
		del _cache['asset_folders__list']
	except:
		pass


def asset_list_refresh(preview_id=False, hard=False):
	try:

		if preview_id:
			del ui.preview_collections['assets'][preview_id]
		elif hard:
			bpy.utils.previews.remove(ui.preview_collections['assets'])
			del ui.preview_collections['assets']

		del _cache['assets__list']

	except:
		pass
