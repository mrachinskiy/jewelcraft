from bpy.utils import previews
from os import path
from .. import var

preview_collections = {}
pcoll = previews.new()

load = pcoll.load
icon_path = path.join

load('CUT-ROUND',     icon_path(var.icons_path, 'cut-round.png'),     'IMAGE')
load('CUT-OVAL',      icon_path(var.icons_path, 'cut-oval.png'),      'IMAGE')
load('CUT-EMERALD',   icon_path(var.icons_path, 'cut-emerald.png'),   'IMAGE')
load('CUT-MARQUISE',  icon_path(var.icons_path, 'cut-marquise.png'),  'IMAGE')
load('CUT-PEAR',      icon_path(var.icons_path, 'cut-pear.png'),      'IMAGE')
load('CUT-BAGUETTE',  icon_path(var.icons_path, 'cut-baguette.png'),  'IMAGE')
load('CUT-SQUARE',    icon_path(var.icons_path, 'cut-square.png'),    'IMAGE')
load('CUT-ASSCHER',   icon_path(var.icons_path, 'cut-asscher.png'),   'IMAGE')
load('CUT-CUSHION',   icon_path(var.icons_path, 'cut-cushion.png'),   'IMAGE')
load('CUT-PRINCESS',  icon_path(var.icons_path, 'cut-princess.png'),  'IMAGE')
load('CUT-TRILLION',  icon_path(var.icons_path, 'cut-trillion.png'),  'IMAGE')
load('CUT-OCTAGON',   icon_path(var.icons_path, 'cut-octagon.png'),   'IMAGE')
load('CUT-HEART',     icon_path(var.icons_path, 'cut-heart.png'),     'IMAGE')
load('CUT-RADIANT',   icon_path(var.icons_path, 'cut-radiant.png'),   'IMAGE')
load('CUT-FLANDERS',  icon_path(var.icons_path, 'cut-flanders.png'),  'IMAGE')
load('CUT-TRILLIANT', icon_path(var.icons_path, 'cut-trilliant.png'), 'IMAGE')
load('CUT-TRIANGLE',  icon_path(var.icons_path, 'cut-triangle.png'),  'IMAGE')

load('TOOL-CUT',               icon_path(var.icons_path, 'tool-cut.png'),               'IMAGE')
load('TOOL-SINGLE_PRONG',      icon_path(var.icons_path, 'tool-single_prong.png'),      'IMAGE')
load('TOOL-CUTTER',            icon_path(var.icons_path, 'tool-cutter.png'),            'IMAGE')
load('TOOL-CUTTER_SEAT',       icon_path(var.icons_path, 'tool-cutter_seat.png'),       'IMAGE')
load('TOOL-IMITATION_3_PRONG', icon_path(var.icons_path, 'tool-imitation_3_prong.png'), 'IMAGE')

preview_collections['main'] = pcoll
