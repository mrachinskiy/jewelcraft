from .. import (
	var,
	localization,
)
from .icons import preview_collections
enum_items = {}



def gem_cut(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]

	if (enum_items.get('LANG_GEM_CUT') and enum_items['LANG_GEM_CUT'] == l and enum_items.get('GEM_CUT')):
		return enum_items['GEM_CUT']

	pcoll = preview_collections['main']
	enum_items['LANG_GEM_CUT'] = l

	enum_items['GEM_CUT'] = (
		('ROUND',     l['round'],     "", pcoll['CUT-ROUND'].icon_id,     0),
		('OVAL',      l['oval'],      "", pcoll['CUT-OVAL'].icon_id,      1),
		('CUSHION',   l['cushion'],   "", pcoll['CUT-CUSHION'].icon_id,   2),
		('PEAR',      l['pear'],      "", pcoll['CUT-PEAR'].icon_id,      3),
		('MARQUISE',  l['marquise'],  "", pcoll['CUT-MARQUISE'].icon_id,  4),
		('PRINCESS',  l['princess'],  "", pcoll['CUT-PRINCESS'].icon_id,  5),
		('BAGUETTE',  l['baguette'],  "", pcoll['CUT-BAGUETTE'].icon_id,  6),
		('SQUARE',    l['square'],    "", pcoll['CUT-SQUARE'].icon_id,    7),
		('EMERALD',   l['emerald'],   "", pcoll['CUT-EMERALD'].icon_id,   8),
		('ASSCHER',   l['asscher'],   "", pcoll['CUT-ASSCHER'].icon_id,   9),
		('RADIANT',   l['radiant'],   "", pcoll['CUT-RADIANT'].icon_id,   10),
		('FLANDERS',  l['flanders'],  "", pcoll['CUT-FLANDERS'].icon_id,  11),
		('OCTAGON',   l['octagon'],   "", pcoll['CUT-OCTAGON'].icon_id,   12),
		('HEART',     l['heart'],     "", pcoll['CUT-HEART'].icon_id,     13),
		('TRILLION',  l['trillion'],  "", pcoll['CUT-TRILLION'].icon_id,  14),
		('TRILLIANT', l['trilliant'], "", pcoll['CUT-TRILLIANT'].icon_id, 15),
		('TRIANGLE',  l['triangle'],  "", pcoll['CUT-TRIANGLE'].icon_id,  16),
	)

	return enum_items['GEM_CUT']



def gem_type(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]

	if (enum_items.get('LANG_GEM_TYPE') and enum_items['LANG_GEM_TYPE'] == l and enum_items.get('GEM_TYPE')):
		return enum_items['GEM_TYPE']

	enum_items['LANG_GEM_TYPE'] = l

	items = [
		('DIAMOND',        l['diamond'],        "", 0),
		('AMETHYST',       l['amethyst'],       "", 1),
		('AQUAMARINE',     l['aquamarine'],     "", 2),
		('CITRINE',        l['citrine'],        "", 3),
		('CUBIC_ZIRCONIA', l['cubic_zirconia'], "", 4),
		('EMERALD',        l['emerald'],        "", 5),
		('GARNET',         l['garnet'],         "", 6),
		('MORGANITE',      l['morganite'],      "", 7),
		('QUARTZ',         l['quartz'],         "", 8),
		('PERIDOT',        l['peridot'],        "", 9),
		('RUBY',           l['ruby'],           "", 10),
		('SAPPHIRE',       l['sapphire'],       "", 11),
		('SPINEL',         l['spinel'],         "", 12),
		('TANZANITE',      l['tanzanite'],      "", 13),
		('TOPAZ',          l['topaz'],          "", 14),
		('TOURMALINE',     l['tourmaline'],     "", 15),
		('ZIRCON',         l['zircon'],         "", 16),
	]

	enum_items['GEM_TYPE'] = sorted(items, key=lambda x: x[1])

	return enum_items['GEM_TYPE']



def weighting_metals(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]

	if (enum_items.get('LANG_WEIGHTING_METALS') and enum_items['LANG_WEIGHTING_METALS'] == l and enum_items.get('WEIGHTING_METALS')):
		return enum_items['WEIGHTING_METALS']

	enum_items['LANG_WEIGHTING_METALS'] = l

	enum_items['WEIGHTING_METALS'] = (
		('24G',    l['24g'],       "", 9),
		('22G',    l['22g'],       "", 10),
		('18WG',   l['18wg'],      "", 0),
		('18YG',   l['18yg'],      "", 1),
		('14WG',   l['14wg'],      "", 2),
		('14YG',   l['14yg'],      "", 3),
		('STER',   l['ster'],      "", 4),
		('PD',     l['pd'],        "", 5),
		('PL',     l['pl'],        "", 6),
		('CUSTOM', l['wt_custom'], "", 7),
		('VOL',    l['wt_vol'],    "", 8),
	)

	return enum_items['WEIGHTING_METALS']
