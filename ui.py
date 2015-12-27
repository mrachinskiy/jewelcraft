from bpy.types import Panel
from . import (
	var,
	localization,
)
from .modules import report
from .modules.icons import preview_collections



def icon_tria(prop):
	if prop:
		icon = 'TRIA_DOWN'
	else:
		icon = 'TRIA_RIGHT'
	return icon



class JewelCraftImportPanel(Panel):

	bl_label = "Jewels"
	bl_idname = "JEWELCRAFT_IMPORT"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "JewelCraft"

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def draw(self, context):
		layout = self.layout
		prefs = context.user_preferences.addons[var.addon_id].preferences
		props = context.scene.jewelcraft
		l = localization.locale[prefs.lang]
		pcoll = preview_collections['main']

		col = layout.column(align=True)

		row = col.row(align=True)
		row.prop(props, 'import_gem_type', text="")
		row.operator("jewelcraft.import_type", text="", icon="COLOR")
		row = col.row(align=True)
		row.prop(props, 'import_gem_cut', text="")
		row.operator("jewelcraft.import_cut", text="", icon_value=pcoll['cut'].icon_id)
		col.prop(props, 'import_gem_size', text=l['size'])
		col.operator("jewelcraft.import_gem", text=l['make_gem'])

		col.separator()
		row = col.row(align=True)
		row.label(l['prongs'])
		row.operator("jewelcraft.import_single_prong", text="", icon="ROTATE")
		row.operator("jewelcraft.import_prongs", text="", icon="SURFACE_NCIRCLE")
		row = col.row(align=True)
		row.label(l['cutter'])
		row.operator("jewelcraft.import_cutter_seat_only", text="", icon_value=pcoll['cutter_s'].icon_id)
		row.operator("jewelcraft.import_cutter", text="", icon_value=pcoll['cutter'].icon_id)
		row = col.row(align=True)
		row.label(l['imitation'])
		row.operator("jewelcraft.import_imitation_3_prong", text="", icon="MOD_SKIN")

		col.separator()
		col.operator("jewelcraft.make_dupliface", text=l['make_dupliface'])



class JewelCraftWeightingPanel(Panel):

	bl_label = "Weighting"
	bl_idname = "JEWELCRAFT_WEIGHTING"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "JewelCraft"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def draw(self, context):
		prefs = context.user_preferences.addons[var.addon_id].preferences
		props = context.scene.jewelcraft
		l = localization.locale[prefs.lang]
		m = props.weighting_metals
		weight = report.data

		layout = self.layout

		col = layout.column(align=True)
		col.prop(props, "weighting_metals", text="")

		col.separator()
		if m == 'CUSTOM':
			col.prop(props, "weighting_custom", text=l['g/cm'])
		col.operator("jewelcraft.weight_display", text=l['wt_calc'])

		if weight:
			box = layout.box()
			box.label(weight)



class JewelCraftExportPanel(Panel):
	
	bl_label = "Export"
	bl_idname = "JEWELCRAFT_EXPORT"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "JewelCraft"

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def draw(self, context):
		layout = self.layout
		sce = context.scene
		prefs = context.user_preferences.addons[var.addon_id].preferences
		props = sce.jewelcraft
		l = localization.locale[prefs.lang]


		box = layout.box()


		row = box.row(align=True)
		row.prop(props, "export_options", icon=icon_tria(props.export_options), icon_only=True)
		row.label(l['export_options'])
		if props.export_options:
			col = box.column()
			col.prop_search(props, "export_size", sce, "objects", text=l['size'])
			col.prop_search(props, "export_shank", sce, "objects", text=l['shank'])
			col.prop_search(props, "export_dim", sce, "objects", text=l['dim'])
			col.prop_search(props, "export_weight", sce, "objects", text=l['weight'])


			row = box.row(align=True)
			row.prop(props, "export_metals", icon=icon_tria(props.export_metals), icon_only=True)
			row.label(l['metals'])
			if props.export_metals:
				col = box.column(align=True)
				col.prop(props, 'metal_24kt', text=l['24kt'])
				col.prop(props, 'metal_22kt', text=l['22kt'])
				col.prop(props, 'metal_18kt_white', text=l['18kt_white'])
				col.prop(props, 'metal_14kt_white', text=l['14kt_white'])
				col.prop(props, 'metal_18kt_yellow', text=l['18kt_yellow'])
				col.prop(props, 'metal_14kt_yellow', text=l['14kt_yellow'])
				col.prop(props, 'metal_silver', text=l['silver'])
				col.prop(props, 'metal_palladium', text=l['palladium'])
				col.prop(props, 'metal_platinum', text=l['platinum'])
				col.prop(props, 'metal_custom', text=l['custom'])
				col = col.column(align=True)
				if not props.metal_custom:
					col.enabled = False
				row = col.row()
				row.label(l['custom_name'])
				row.label(l['g/cm']+':')
				row = col.row()
				row.prop(props, "metal_custom_name", text="")
				row.prop(props, "metal_custom_density", text="")


			col = box.row(align=True)
			col.label(l['lang']+":")
			col.prop(props, 'lang', text="")


		col = layout.column(align=True)
		col.operator("jewelcraft.export_stats", text=l['export_stats'])
