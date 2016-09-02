import bpy
from bpy.types import Panel
from . import (
	var,
	locale,
	previews,
	)


def icon_tria(prop):
	if prop:
		return 'TRIA_DOWN'
	else:
		return 'TRIA_RIGHT'


class UI:
	bl_category = 'JewelCraft'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'

	def __init__(self):
		prefs = bpy.context.user_preferences.addons[var.addon_id].preferences
		self.props = bpy.context.scene.jewelcraft
		self.l = locale.locale[prefs.lang]


class Gems(UI, Panel):
	bl_label = 'Gems'
	bl_idname = 'jewelcraft_import'

	def draw(self, context):
		layout = self.layout
		l = self.l
		icons = previews.preview_collections['icons']

		layout.template_icon_view(self.props, 'gem_cut', show_labels=True)

		col = layout.column(align=True)
		colrow = col.row(align=True)
		colrow.prop(self.props, 'gem_stone', text='')
		colrow.operator('jewelcraft.search_stone', text='', icon='VIEWZOOM')
		col.prop(self.props, 'gem_size', text=l['size'])
		col.operator('jewelcraft.make_gem', text=l['make_gem'])

		col = layout.column(align=True)
		colrow = col.row(align=True)
		colrow.label(l['gem'])
		colrow.operator('jewelcraft.replace_stone', text='', icon='COLOR')
		colrow.operator('jewelcraft.replace_cut', text='', icon_value=icons['TOOL-CUT'].icon_id)

		col = layout.column(align=True)
		colrow = col.row(align=True)
		colrow.label(l['prongs'])
		colrow.operator('jewelcraft.make_single_prong', text='', icon_value=icons['TOOL-SINGLE_PRONG'].icon_id)
		colrow.operator('jewelcraft.make_prongs', text='', icon='SURFACE_NCIRCLE')
		colrow = col.row(align=True)
		colrow.label(l['cutter'])
		colrow.operator('jewelcraft.make_cutter', text='', icon_value=icons['TOOL-CUTTER_SEAT'].icon_id).seat_only = True
		colrow.operator('jewelcraft.make_cutter', text='', icon_value=icons['TOOL-CUTTER'].icon_id)
		colrow = col.row(align=True)
		colrow.label(l['imitation'])
		colrow.operator('jewelcraft.make_imitation', text='', icon_value=icons['TOOL-IMITATION'].icon_id)

		col = layout.column(align=True)
		col.operator('jewelcraft.make_dupliface', text=l['make_dupliface'])
		col.operator('jewelcraft.select_doubles', text=l['select_doubles'])


class Weighting(UI, Panel):
	bl_label = 'Weighting'
	bl_idname = 'jewelcraft_weighting'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		l = self.l
		weight = var.weighting_report

		layout.prop(self.props, 'weighting_metals', text='')

		col = layout.column(align=True)
		if self.props.weighting_metals == 'CUSTOM':
			col.prop(self.props, 'weighting_custom', text=l['g/cm'])
		col.operator('jewelcraft.weight_display', text=l['wt_calc'])

		if weight:
			box = layout.box()
			box.label(weight)


class Stats(UI, Panel):
	bl_label = 'Statistics'
	bl_idname = 'jewelcraft_export'

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		props = self.props
		l = self.l

		box = layout.box()
		boxrow = box.row(align=True)
		boxrow.prop(props, 'stats_options', icon=icon_tria(props.stats_options), icon_only=True)
		boxrow.label(l['stats_options'])
		if props.stats_options:
			col = box.column()
			colrow = col.row(align=True)
			colrow.prop_search(props, 'stats_size', scene, 'objects', text=l['size'])
			colrow.operator('jewelcraft.stats_pick', text='', icon='EYEDROPPER').prop = 'stats_size'
			colrow = col.row(align=True)
			colrow.prop_search(props, 'stats_shank', scene, 'objects', text=l['shank'])
			colrow.operator('jewelcraft.stats_pick', text='', icon='EYEDROPPER').prop = 'stats_shank'
			colrow = col.row(align=True)
			colrow.prop_search(props, 'stats_dim', scene, 'objects', text=l['dim'])
			colrow.operator('jewelcraft.stats_pick', text='', icon='EYEDROPPER').prop = 'stats_dim'
			colrow = col.row(align=True)
			colrow.prop_search(props, 'stats_weight', scene, 'objects', text=l['weight'])
			colrow.operator('jewelcraft.stats_pick', text='', icon='EYEDROPPER').prop = 'stats_weight'

			boxrow = box.row(align=True)
			boxrow.label(l['lang'] + ':')
			boxrow.prop(props, 'stats_lang', text='')

			boxrow = box.row(align=True)
			boxrow.prop(props, 'stats_metals', icon=icon_tria(props.stats_metals), icon_only=True)
			boxrow.label(l['metals'])
			if props.stats_metals:
				col = box.column(align=True)
				col.prop(props, 'stats_24g',    text=l['24g'])
				col.prop(props, 'stats_22g',    text=l['22g'])
				col.prop(props, 'stats_18wg',   text=l['18wg'])
				col.prop(props, 'stats_18yg',   text=l['18yg'])
				col.prop(props, 'stats_14wg',   text=l['14wg'])
				col.prop(props, 'stats_14yg',   text=l['14yg'])
				col.prop(props, 'stats_ster',   text=l['ster'])
				col.prop(props, 'stats_pd',     text=l['pd'])
				col.prop(props, 'stats_pl',     text=l['pl'])
				col.prop(props, 'stats_custom', text=l['custom'])

				sub = col.column()
				sub.enabled = props.stats_custom
				subrow = sub.row(align=True)
				subrow.label(l['custom_name'])
				subrow.prop(props, 'stats_custom_name', text='')
				subrow = sub.row(align=True)
				subrow.label(l['g/cm'] + ':')
				subrow.prop(props, 'stats_custom_dens', text='')

		col = layout.column(align=True)
		col.operator('jewelcraft.stats_export', text=l['stats_export'])
