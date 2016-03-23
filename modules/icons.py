from bpy.utils import previews
from os import path
from .. import var


preview_collections = {}


icon_names = (
	'cut-round',
	'cut-oval',
	'cut-emerald',
	'cut-marquise',
	'cut-pear',
	'cut-baguette',
	'cut-square',
	'cut-asscher',
	'cut-cushion',
	'cut-princess',
	'cut-trillion',
	'cut-octagon',
	'cut-heart',
	'cut-radiant',
	'cut-flanders',
	'cut-trilliant',
	'cut-triangle',

	'tool-cut',
	'tool-single_prong',
	'tool-cutter',
	'tool-cutter_seat',
	'tool-imitation_3_prong',
)

pcoll = previews.new()
load = pcoll.load

for name in icon_names:
	load(name.upper(), path.join(var.icons_path, name + '.png'), 'IMAGE')


preview_collections['icons'] = pcoll
