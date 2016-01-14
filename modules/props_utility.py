from .. import (
	var,
	localization,
)
from .icons import preview_collections


def gem_type(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]

	items = [
		('DIAMOND',        l['diamond'],        "", 0),
		('AMETHYST',       l['amethyst'],       "", 1),
		('AQUAMARINE',     l['aquamarine'],     "", 2),
		('CITRINE',        l['citrine'],        "", 3),
		('CUBIC_ZIRCONIA', l['cubic_zirconia'], "", 4),
		('EMERALD',        l['emerald'],        "", 5),
		('GARNET',         l['garnet'],         "", 6),
		('QUARTZ',         l['quartz'],         "", 7),
		('RUBY',           l['ruby'],           "", 8),
		('SAPPHIRE',       l['sapphire'],       "", 9),
		('SPINEL',         l['spinel'],         "", 10),
		('TANZANITE',      l['tanzanite'],      "", 11),
		('TOPAZ',          l['topaz'],          "", 12),
		('TOURMALINE',     l['tourmaline'],     "", 13),
	]
	return sorted(items, key=lambda x: x[1])


def gem_cut(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]
	pcoll = preview_collections['main']

	items = (
		('ROUND',    l['round'],    "", pcoll['cut-round'].icon_id,    0),
		('OVAL',     l['oval'],     "", pcoll['cut-oval'].icon_id,     1),
		('EMERALD',  l['emerald'],  "", pcoll['cut-emerald'].icon_id,  2),
		('ASSCHER',  l['asscher'],  "", pcoll['cut-asscher'].icon_id,  8),
		('MARQUISE', l['marquise'], "", pcoll['cut-marquise'].icon_id, 3),
		('PEARL',    l['pearl'],    "", pcoll['cut-pearl'].icon_id,    4),
		('BAGUETTE', l['baguette'], "", pcoll['cut-baguette'].icon_id, 5),
		('SQUARE',   l['square'],   "", pcoll['cut-square'].icon_id,   6),
		('PRINCESS', l['princess'], "", pcoll['cut-princess'].icon_id, 9),
		('CUSHION',  l['cushion'],  "", pcoll['cut-cushion'].icon_id,  7),
		('TRILLION', l['trillion'], "", pcoll['cut-trillion'].icon_id, 10),
	)
	return items


def weighting_metals(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]

	items = (
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
	return items
