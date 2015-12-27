from bpy.utils import previews
from os import path
from .. import var

preview_collections = {}
pcoll = previews.new()

load = pcoll.load
icon_path = path.join

load('cut',      icon_path(var.icons_path, 'cut.png'),              'IMAGE')
load('cutter',   icon_path(var.icons_path, 'cutter.png'),           'IMAGE')
load('cutter_s', icon_path(var.icons_path, 'cutter_seat_only.png'), 'IMAGE')

load('cut-round',    icon_path(var.icons_path, 'cut-round.png'),    'IMAGE')
load('cut-oval',     icon_path(var.icons_path, 'cut-oval.png'),     'IMAGE')
load('cut-emerald',  icon_path(var.icons_path, 'cut-emerald.png'),  'IMAGE')
load('cut-marquise', icon_path(var.icons_path, 'cut-marquise.png'), 'IMAGE')
load('cut-pearl',    icon_path(var.icons_path, 'cut-pearl.png'),    'IMAGE')
load('cut-baguette', icon_path(var.icons_path, 'cut-baguette.png'), 'IMAGE')
load('cut-square',   icon_path(var.icons_path, 'cut-square.png'),   'IMAGE')

preview_collections['main'] = pcoll
