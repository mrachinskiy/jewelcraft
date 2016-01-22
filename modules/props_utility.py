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
		('EMERALD',   l['emerald'],   "", pcoll['CUT-EMERALD'].icon_id,   4),
		('ASSCHER',   l['asscher'],   "", pcoll['CUT-ASSCHER'].icon_id,   5),
		('MARQUISE',  l['marquise'],  "", pcoll['CUT-MARQUISE'].icon_id,  6),
		('PEAR',      l['pear'],      "", pcoll['CUT-PEAR'].icon_id,      7),
		('HEART',     l['heart'],     "", pcoll['CUT-HEART'].icon_id,     12),
		('PRINCESS',  l['princess'],  "", pcoll['CUT-PRINCESS'].icon_id,  3),
		('RADIANT',   l['radiant'],   "", pcoll['CUT-RADIANT'].icon_id,   13),
		('CUSHION',   l['cushion'],   "", pcoll['CUT-CUSHION'].icon_id,   2),
		('OCTAGON',   l['octagon'],   "", pcoll['CUT-OCTAGON'].icon_id,   11),
		('FLANDERS',  l['flanders'],  "", pcoll['CUT-FLANDERS'].icon_id,  14),
		('TRILLIANT', l['trilliant'], "", pcoll['CUT-TRILLIANT'].icon_id, 15),
		('TRILLION',  l['trillion'],  "", pcoll['CUT-TRILLION'].icon_id,  8),
		('BAGUETTE',  l['baguette'],  "", pcoll['CUT-BAGUETTE'].icon_id,  9),
		('SQUARE',    l['square'],    "", pcoll['CUT-SQUARE'].icon_id,    10),

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
		('QUARTZ',         l['quartz'],         "", 7),
		('PERIDOT',        l['peridot'],        "", 8),
		('RUBY',           l['ruby'],           "", 9),
		('SAPPHIRE',       l['sapphire'],       "", 10),
		('SPINEL',         l['spinel'],         "", 11),
		('TANZANITE',      l['tanzanite'],      "", 12),
		('TOPAZ',          l['topaz'],          "", 13),
		('TOURMALINE',     l['tourmaline'],     "", 14),
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
		('24KT',        l['24kt'],        "", 9),
		('22KT',        l['22kt'],        "", 10),
		('18KT_WHITE',  l['18kt_white'],  "", 0),
		('14KT_WHITE',  l['14kt_white'],  "", 1),
		('18KT_YELLOW', l['18kt_yellow'], "", 2),
		('14KT_YELLOW', l['14kt_yellow'], "", 3),
		('STERLING',    l['sterling'],    "", 4),
		('PALLADIUM',   l['palladium'],   "", 5),
		('PLATINUM',    l['platinum'],    "", 6),
		('CUSTOM',      l['wt_custom'],   "", 7),
		('VOL',         l['wt_vol'],      "", 8),
	)

	return enum_items['WEIGHTING_METALS']
