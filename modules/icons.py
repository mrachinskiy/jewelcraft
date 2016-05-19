from bpy.utils import previews
from os import scandir
from os.path import splitext
from .. import var


preview_collections = {}


icon_previews = previews.new()
load = icon_previews.load
for entry in scandir(var.icons_path):
	load(splitext(entry.name)[0].upper(), entry.path, 'IMAGE')

preview_collections['icons'] = icon_previews
