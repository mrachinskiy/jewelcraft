import bpy
from bpy.types import Operator
from . import (
	var,
	localization,
)
from .modules import (
	assets,
	stats,
	props_utility,
)


class SEARCH_TYPE(Operator):
	'''Search stone type'''
	bl_label = "Search Type"
	bl_idname = "jewelcraft.search_type"
	bl_property = "prop"
	bl_options = {'INTERNAL'}

	prop = bpy.props.EnumProperty(items=props_utility.gem_type)

	def execute(self, context):
		context.scene.jewelcraft.import_gem_type = self.prop
		context.area.tag_redraw()
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'FINISHED'}






class IMPORT_GEM(Operator):
	'''Create gem'''
	bl_label = "JewelCraft: Make Gem"
	bl_idname = "jewelcraft.import_gem"

	def execute(self, context):
		assets.gem_import()
		return {'FINISHED'}


class IMPORT_TYPE(Operator):
	'''Change type of selected gems'''
	bl_label = "JewelCraft: Change Type"
	bl_idname = "jewelcraft.import_type"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.type_replace()
		return {'FINISHED'}


class IMPORT_CUT(Operator):
	'''Change cut of selected gems'''
	bl_label = "JewelCraft: Change Cut"
	bl_idname = "jewelcraft.import_cut"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.cut_replace()
		return {'FINISHED'}






class IMPORT_PRONGS(Operator):
	'''Create prongs for selected gems'''
	bl_label = "JewelCraft: Add Prongs"
	bl_idname = "jewelcraft.import_prongs"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.prongs_import()
		return {'FINISHED'}


class IMPORT_SINGLE_PRONG(Operator):
	'''Create single prong'''
	bl_label = "JewelCraft: Make Single Prong"
	bl_idname = "jewelcraft.import_single_prong"

	def execute(self, context):
		assets.single_prong_import()
		return {'FINISHED'}


class IMPORT_CUTTER(Operator):
	'''Create cutter for selected gems'''
	bl_label = "JewelCraft: Add Cutter"
	bl_idname = "jewelcraft.import_cutter"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.cutter_import()
		return {'FINISHED'}


class IMPORT_CUTTER_SEAT(Operator):
	'''Create (seat only) cutter for selected gems'''
	bl_label = "JewelCraft: Add Cutter (Seat only)"
	bl_idname = "jewelcraft.import_cutter_seat"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.cutter_import(seat_only=True)
		return {'FINISHED'}


class IMPORT_IMITATION_3_PRONG(Operator):
	'''Create imitation (3 prong)'''
	bl_label = "JewelCraft: Make Imitation (3 prong)"
	bl_idname = "jewelcraft.import_imitation_3_prong"

	def execute(self, context):
		assets.imitation_import()
		return {'FINISHED'}


class MAKE_DUPLIFACE(Operator):
	'''Create dupliface for selected objects'''
	bl_label = "JewelCraft: Make Dupli-face"
	bl_idname = "jewelcraft.make_dupliface"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.make_dupliface()
		return {'FINISHED'}


class SELECT_DUPLI(Operator):
	'''Select duplicated gems (have same location); WARNING: it does not work with dupli-faces, objects only'''
	bl_label = "JewelCraft: Select duplicated gems"
	bl_idname = "jewelcraft.select_dupli"

	def execute(self, context):
		prefs = context.user_preferences.addons[var.addon_id].preferences
		l = localization.locale[prefs.lang]

		if assets.select_dupli() == True:
			self.report({'WARNING'}, l['report_dupli'])
		else:
			self.report({'INFO'}, l['report_no_dupli'])

		return {'FINISHED'}






class WEIGHT_DISPLAY(Operator):
	'''Display weight or volume of the active mesh object'''
	bl_label = "JewelCraft: Weighting"
	bl_idname = "jewelcraft.weight_display"

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		stats.weight_display()
		return {'FINISHED'}






class EXPORT_PICK_SIZE(Operator):
	'''Pick active object'''
	bl_label = "JewelCraft: Pick Size"
	bl_idname = "jewelcraft.export_pick_size"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_size = context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_SHANK(Operator):
	'''Pick active object'''
	bl_label = "JewelCraft: Pick Shank"
	bl_idname = "jewelcraft.export_pick_shank"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_shank = context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_DIM(Operator):
	'''Pick active object'''
	bl_label = "JewelCraft: Pick Dim"
	bl_idname = "jewelcraft.export_pick_dim"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_dim = context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_WEIGHT(Operator):
	'''Pick active object'''
	bl_label = "JewelCraft: Pick Weight"
	bl_idname = "jewelcraft.export_pick_weight"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_weight = context.active_object.name
		return {'FINISHED'}


class EXPORT_STATS(Operator):
	'''Export project statistics'''
	bl_label = "JewelCraft: Export Stats"
	bl_idname = "jewelcraft.export_stats"

	def execute(self, context):
		prefs = context.user_preferences.addons[var.addon_id].preferences
		l = localization.locale[prefs.lang]

		if stats.export() == True:
			self.report({'INFO'}, l['report_stats'])

		return {'FINISHED'}
