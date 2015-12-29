import bpy
from bpy.types import Operator
from .modules import (
	assets,
	stats,
)


class IMPORT_GEM(Operator):
	'''Create gemstone'''
	bl_label = "JewelCraft: Make Gemstone"
	bl_idname = "jewelcraft.import_gem"

	def execute(self, context):
		assets.gem_import()
		return {'FINISHED'}


class IMPORT_TYPE(Operator):
	'''Change type of selected gemstones'''
	bl_label = "JewelCraft: Change Type"
	bl_idname = "jewelcraft.import_type"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.type_replace()
		return {'FINISHED'}


class IMPORT_CUT(Operator):
	'''Change cut of selected gemstones'''
	bl_label = "JewelCraft: Change Cut"
	bl_idname = "jewelcraft.import_cut"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.cut_replace()
		return {'FINISHED'}






class IMPORT_PRONGS(Operator):
	'''Create prongs for selected gemstones'''
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
	'''Create cutters for selected gemstones'''
	bl_label = "JewelCraft: Add Cutter"
	bl_idname = "jewelcraft.import_cutter"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.cutter_import()
		return {'FINISHED'}


class IMPORT_CUTTER_SEAT_ONLY(Operator):
	'''Create (seat only) cutters for selected gemstones'''
	bl_label = "JewelCraft: Add Cutter (Seat only)"
	bl_idname = "jewelcraft.import_cutter_seat_only"

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
		props = bpy.context.scene.jewelcraft
		props.export_size = bpy.context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_SHANK(Operator):
	'''Pick active object'''
	bl_label = "JewelCraft: Pick Shank"
	bl_idname = "jewelcraft.export_pick_shank"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		props = bpy.context.scene.jewelcraft
		props.export_shank = bpy.context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_DIM(Operator):
	'''Pick active object'''
	bl_label = "JewelCraft: Pick Dim"
	bl_idname = "jewelcraft.export_pick_dim"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		props = bpy.context.scene.jewelcraft
		props.export_dim = bpy.context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_WEIGHT(Operator):
	'''Pick active object'''
	bl_label = "JewelCraft: Pick Weight"
	bl_idname = "jewelcraft.export_pick_weight"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		props = bpy.context.scene.jewelcraft
		props.export_weight = bpy.context.active_object.name
		return {'FINISHED'}


class EXPORT_STATS(Operator):
	'''Export statistics for the project'''
	bl_label = "JewelCraft: Export Stats"
	bl_idname = "jewelcraft.export_stats"

	def execute(self, context):
		stats.export()
		return {'FINISHED'}
