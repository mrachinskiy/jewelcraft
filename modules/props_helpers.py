from .. import (
	var,
	localization,
)
from .icons import preview_collections


def gems_type(self, context):
	'''For enum translation'''
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]

	items = (
		('DIAMOND',  l['diamond'],  "", 0),
		('ZIRCON',   l['zircon'],   "", 1),
		('TOPAZ',    l['topaz'],    "", 2),
		('EMERALD',  l['emerald'],  "", 3),
		('RUBY',     l['ruby'],     "", 4),
		('SAPPHIRE', l['sapphire'], "", 5),
	)
	return items


def gems_cut(self, context):
	'''For enum translation'''
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]
	pcoll = preview_collections['main']

	items = (
		('ROUND',    l['round'],    "", pcoll['cut-round'].icon_id,    0),
		('OVAL',     l['oval'],     "", pcoll['cut-oval'].icon_id,     1),
		('EMERALD',  l['emerald'],  "", pcoll['cut-emerald'].icon_id,  2),
		('MARQUISE', l['marquise'], "", pcoll['cut-marquise'].icon_id, 3),
		('PEARL',    l['pearl'],    "", pcoll['cut-pearl'].icon_id,    4),
		('BAGUETTE', l['baguette'], "", pcoll['cut-baguette'].icon_id, 5),
		('SQUARE',   l['square'],   "", pcoll['cut-square'].icon_id,   6),
	)
	return items


def volume_metal_list(self, context):
	prefs = context.user_preferences.addons[var.addon_id].preferences
	l = localization.locale[prefs.lang]

	items = (
		('24KT',        l['24kt'],        "", 9),
		('22KT',        l['22kt'],        "", 10),
		('18KT_WHITE',  l['18kt_white'],  "", 0),
		('14KT_WHITE',  l['14kt_white'],  "", 1),
		('18KT_YELLOW', l['18kt_yellow'], "", 2),
		('14KT_YELLOW', l['14kt_yellow'], "", 3),
		('SILVER',      l['silver'],      "", 4),
		('PALLADIUM',   l['palladium'],   "", 5),
		('PLATINUM',    l['platinum'],    "", 6),
		('CUSTOM',      l['wt_custom'],   "", 7),
		('VOL',         l['wt_vol'],      "", 8),
	)
	return items
