from bpy.types import Panel
from . import (
	var,
	localization,
)
from .modules import report
from .modules.icons import preview_collections


class ImportPanel(Panel):
	bl_category = 'JewelCraft'
	bl_label = 'Gems'
	bl_idname = 'jewelcraft_import'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'

	def draw(self, context):
		layout = self.layout
		prefs = context.user_preferences.addons[var.addon_id].preferences
		props = context.scene.jewelcraft
		l = localization.locale[prefs.lang]
		icons = preview_collections['icons']

		col = layout.column(align=True)

		col.template_icon_view(props, 'make_gem_cut', show_labels=True)

		col.separator()
		row = col.row(align=True)
		row.prop(props, 'make_gem_stone', text='')
		row.operator('jewelcraft.search_stone', text='', icon='VIEWZOOM')
		col.prop(props, 'make_gem_size', text=l['size'])
		col.operator('jewelcraft.make_gem', text=l['make_gem'])

		col.separator()
		row = col.row(align=True)
		row.label(l['gem'])
		row.operator('jewelcraft.replace_stone', text='', icon='COLOR')
		row.operator('jewelcraft.replace_cut', text='', icon_value=icons['TOOL-CUT'].icon_id)

		col.separator()
		row = col.row(align=True)
		row.label(l['prongs'])
		row.operator('jewelcraft.make_single_prong', text='', icon_value=icons['TOOL-SINGLE_PRONG'].icon_id)
		row.operator('jewelcraft.make_prongs', text='', icon='SURFACE_NCIRCLE')
		row = col.row(align=True)
		row.label(l['cutter'])
		row.operator('jewelcraft.make_cutter_seat', text='', icon_value=icons['TOOL-CUTTER_SEAT'].icon_id)
		row.operator('jewelcraft.make_cutter', text='', icon_value=icons['TOOL-CUTTER'].icon_id)
		row = col.row(align=True)
		row.label(l['imitation'])
		row.operator('jewelcraft.make_imitation', text='', icon_value=icons['TOOL-IMITATION'].icon_id)

		col.separator()
		col.operator('jewelcraft.make_dupliface', text=l['make_dupliface'])
		col.operator('jewelcraft.select_doubles', text=l['select_doubles'])






class WeightingPanel(Panel):
	bl_category = 'JewelCraft'
	bl_label = 'Weighting'
	bl_idname = 'jewelcraft_weighting'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		prefs = context.user_preferences.addons[var.addon_id].preferences
		props = context.scene.jewelcraft
		l = localization.locale[prefs.lang]
		m = props.weighting_metals
		weight = report.data

		col = layout.column(align=True)

		col.prop(props, 'weighting_metals', text='')

		if m == 'CUSTOM':
			col.separator()
			col.prop(props, 'weighting_custom', text=l['g/cm'])

		col.separator()
		col.operator('jewelcraft.weight_display', text=l['wt_calc'])

		if weight:
			col.separator()
			box = col.box()
			box.label(weight)






class ExportPanel(Panel):
	bl_category = 'JewelCraft'
	bl_label = 'Export'
	bl_idname = 'jewelcraft_export'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		prefs = context.user_preferences.addons[var.addon_id].preferences
		props = scene.jewelcraft
		l = localization.locale[prefs.lang]


		box = layout.box()


		row = box.row(align=True)
		row.prop(props, 'export_options', icon=icon_tria(props.export_options), icon_only=True)
		row.label(l['export_options'])
		if props.export_options:
			col = box.column()
			row = col.row(align=True)
			row.prop_search(props, 'export_size', scene, 'objects', text=l['size'])
			row.operator('jewelcraft.export_pick_size', text='', icon='EYEDROPPER')
			row = col.row(align=True)
			row.prop_search(props, 'export_shank', scene, 'objects', text=l['shank'])
			row.operator('jewelcraft.export_pick_shank', text='', icon='EYEDROPPER')
			row = col.row(align=True)
			row.prop_search(props, 'export_dim', scene, 'objects', text=l['dim'])
			row.operator('jewelcraft.export_pick_dim', text='', icon='EYEDROPPER')
			row = col.row(align=True)
			row.prop_search(props, 'export_weight', scene, 'objects', text=l['weight'])
			row.operator('jewelcraft.export_pick_weight', text='', icon='EYEDROPPER')


			row = box.row(align=True)
			row.prop(props, 'export_metals', icon=icon_tria(props.export_metals), icon_only=True)
			row.label(l['metals'])
			if props.export_metals:
				col = box.column(align=True)
				col.prop(props, 'export_m_24g',    text=l['24g'])
				col.prop(props, 'export_m_22g',    text=l['22g'])
				col.prop(props, 'export_m_18wg',   text=l['18wg'])
				col.prop(props, 'export_m_18yg',   text=l['18yg'])
				col.prop(props, 'export_m_14wg',   text=l['14wg'])
				col.prop(props, 'export_m_14yg',   text=l['14yg'])
				col.prop(props, 'export_m_ster',   text=l['ster'])
				col.prop(props, 'export_m_pd',     text=l['pd'])
				col.prop(props, 'export_m_pl',     text=l['pl'])
				col.prop(props, 'export_m_custom', text=l['custom'])

				col = col.column(align=True)
				col.enabled = props.export_m_custom
				row = col.row()
				row.label(l['custom_name'])
				row.label(l['g/cm'] + ':')
				row = col.row()
				row.prop(props, 'export_m_custom_name', text='')
				row.prop(props, 'export_m_custom_dens', text='')


			row = box.row(align=True)
			row.label(l['lang'] + ':')
			row.prop(props, 'export_lang', text='')


		col = layout.column(align=True)
		col.operator('jewelcraft.export_stats', text=l['export_stats'])






# Utility


def icon_tria(prop):
	if prop:
		return 'TRIA_DOWN'
	else:
		return 'TRIA_RIGHT'
