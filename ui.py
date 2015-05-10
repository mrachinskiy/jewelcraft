# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2015 Mikhail Rachinskiy
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ##### END MIT LICENSE BLOCK #####

from bpy.types import Panel
from . import localization


def icon_tria(prop):
	if prop: icon = 'TRIA_DOWN'
	else: icon = 'TRIA_RIGHT'
	return icon




class JewelCraftLocalePanel(Panel):
	
	bl_label = "Localization"
	bl_idname = "JEWELCRAFT_LOCALE"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "JewelCraft"

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.prop(context.scene.jewelcraft, 'lang', expand=True)



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
		props = context.scene.jewelcraft
		l = localization.locale[props.lang]

		col = layout.column(align=True)

		row = col.row(align=True)
		row.prop(props, 'import_gem_type', text="")
		row.operator("jewelcraft.import_type", text="", icon="COLOR")
		row = col.row(align=True)
		row.prop(props, 'import_gem_cut', text="")
		row.operator("jewelcraft.import_cut", text="", icon="MESH_ICOSPHERE")
		row = col.row(align=True)
		row.prop(props, 'import_prongs', text=l['prongs'])
		row.operator("jewelcraft.import_prongs", text="", icon="SURFACE_NCIRCLE")
		row = col.row(align=True)
		row.prop(props, 'import_cutter', text=l['cutter'])
		row.operator("jewelcraft.import_cutter", text="", icon="MESH_CONE")

		col.separator()
		row = col.row(align=True)
		row.prop(props, 'import_gem_size', text=l['size'])
		
		col.separator()
		col.operator("jewelcraft.import_gem", text=l['make_gem'])
		col.operator("jewelcraft.make_dupliface", text=l['make_dupliface'])
		




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
		props = sce.jewelcraft
		l = localization.locale[props.lang]


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
				row.label(l['g/cm'])
				row = col.row()
				row.prop(props, "metal_custom_name", text="")
				row.prop(props, "metal_custom_density", text="")


		col = layout.column(align=True)
		col.operator("jewelcraft.export_stats", text=l['export_stats'])
