from . import (
	var,
	locale,
	previews,
	)


enum_items = {}


def cuts(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences

	if enum_items.get('1_lang') == prefs.lang:
		return enum_items['1_items']

	l = locale.locale[prefs.lang]
	icons = previews.preview_collections['icons']

	enum_items['1_lang'] = prefs.lang
	enum_items['1_items'] = (
		('ROUND',     l['round'],     '', icons['CUT-ROUND'].icon_id,     0),
		('OVAL',      l['oval'],      '', icons['CUT-OVAL'].icon_id,      1),
		('CUSHION',   l['cushion'],   '', icons['CUT-CUSHION'].icon_id,   2),
		('PEAR',      l['pear'],      '', icons['CUT-PEAR'].icon_id,      3),
		('MARQUISE',  l['marquise'],  '', icons['CUT-MARQUISE'].icon_id,  4),
		('PRINCESS',  l['princess'],  '', icons['CUT-PRINCESS'].icon_id,  5),
		('BAGUETTE',  l['baguette'],  '', icons['CUT-BAGUETTE'].icon_id,  6),
		('SQUARE',    l['square'],    '', icons['CUT-SQUARE'].icon_id,    7),
		('EMERALD',   l['emerald'],   '', icons['CUT-EMERALD'].icon_id,   8),
		('ASSCHER',   l['asscher'],   '', icons['CUT-ASSCHER'].icon_id,   9),
		('RADIANT',   l['radiant'],   '', icons['CUT-RADIANT'].icon_id,   10),
		('FLANDERS',  l['flanders'],  '', icons['CUT-FLANDERS'].icon_id,  11),
		('OCTAGON',   l['octagon'],   '', icons['CUT-OCTAGON'].icon_id,   12),
		('HEART',     l['heart'],     '', icons['CUT-HEART'].icon_id,     13),
		('TRILLION',  l['trillion'],  '', icons['CUT-TRILLION'].icon_id,  14),
		('TRILLIANT', l['trilliant'], '', icons['CUT-TRILLIANT'].icon_id, 15),
		('TRIANGLE',  l['triangle'],  '', icons['CUT-TRIANGLE'].icon_id,  16),
		)

	return enum_items['1_items']


def stones(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences

	if enum_items.get('2_lang') == prefs.lang:
		return enum_items['2_items']

	l = locale.locale[prefs.lang]

	items = [
		('DIAMOND',        l['diamond'],        '', 0),
		('AMETHYST',       l['amethyst'],       '', 1),
		('AQUAMARINE',     l['aquamarine'],     '', 2),
		('CITRINE',        l['citrine'],        '', 3),
		('CUBIC_ZIRCONIA', l['cubic_zirconia'], '', 4),
		('EMERALD',        l['emerald'],        '', 5),
		('GARNET',         l['garnet'],         '', 6),
		('MORGANITE',      l['morganite'],      '', 7),
		('QUARTZ',         l['quartz'],         '', 8),
		('PERIDOT',        l['peridot'],        '', 9),
		('RUBY',           l['ruby'],           '', 10),
		('SAPPHIRE',       l['sapphire'],       '', 11),
		('SPINEL',         l['spinel'],         '', 12),
		('TANZANITE',      l['tanzanite'],      '', 13),
		('TOPAZ',          l['topaz'],          '', 14),
		('TOURMALINE',     l['tourmaline'],     '', 15),
		('ZIRCON',         l['zircon'],         '', 16),
		]

	enum_items['2_lang'] = prefs.lang
	enum_items['2_items'] = sorted(items, key=lambda x: x[1])

	return enum_items['2_items']


def metals(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences

	if enum_items.get('3_lang') == prefs.lang:
		return enum_items['3_items']

	l = locale.locale[prefs.lang]

	enum_items['3_lang'] = prefs.lang
	enum_items['3_items'] = (
		('24G',    l['24g'],       '', 9),
		('22G',    l['22g'],       '', 10),
		('18WG',   l['18wg'],      '', 0),
		('18YG',   l['18yg'],      '', 1),
		('14WG',   l['14wg'],      '', 2),
		('14YG',   l['14yg'],      '', 3),
		('STER',   l['ster'],      '', 4),
		('PD',     l['pd'],        '', 5),
		('PL',     l['pl'],        '', 6),
		('CUSTOM', l['wt_custom'], '', 7),
		('VOLUME', l['wt_volume'], '', 8),
		)

	return enum_items['3_items']
