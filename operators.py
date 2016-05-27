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
	utility,
)


class SEARCH_STONE(Operator):
	"""Search stone by name"""
	bl_label = 'Search Stone'
	bl_idname = 'jewelcraft.search_stone'
	bl_property = 'prop'
	bl_options = {'INTERNAL'}

	prop = bpy.props.EnumProperty(items=props_utility.stones)

	def execute(self, context):
		context.scene.jewelcraft.make_gem_stone = self.prop
		context.area.tag_redraw()
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'FINISHED'}






class MAKE_GEM(Operator):
	"""Create gemstone"""
	bl_label = 'JewelCraft: Make Gem'
	bl_idname = 'jewelcraft.make_gem'

	def execute(self, context):
		assets.make_gem()
		return {'FINISHED'}


class REPLACE_STONE(Operator):
	"""Replace selected gems"""
	bl_label = 'JewelCraft: Replace Stone'
	bl_idname = 'jewelcraft.replace_stone'

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.replace_stone()
		return {'FINISHED'}


class REPLACE_CUT(Operator):
	"""Replace cut for selected gems"""
	bl_label = 'JewelCraft: Replace Cut'
	bl_idname = 'jewelcraft.replace_cut'

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.replace_cut()
		return {'FINISHED'}






class MAKE_PRONGS(Operator):
	"""Create prongs for selected gems"""
	bl_label = 'JewelCraft: Make Prongs'
	bl_idname = 'jewelcraft.make_prongs'

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.make_gem_suppl('PRONGS')
		return {'FINISHED'}


class MAKE_CUTTER(Operator):
	"""Create cutter for selected gems"""
	bl_label = 'JewelCraft: Make Cutter'
	bl_idname = 'jewelcraft.make_cutter'

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.make_gem_suppl('CUTTER')
		return {'FINISHED'}


class MAKE_CUTTER_SEAT(Operator):
	"""Create (seat only) cutter for selected gems"""
	bl_label = 'JewelCraft: Make Cutter (Seat only)'
	bl_idname = 'jewelcraft.make_cutter_seat'

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.make_gem_suppl('CUTTER', seat_only=True)
		return {'FINISHED'}


class MAKE_SINGLE_PRONG(Operator):
	"""Create single prong"""
	bl_label = 'JewelCraft: Make Single Prong'
	bl_idname = 'jewelcraft.make_single_prong'

	def execute(self, context):
		assets.make_setting_suppl('Single Prong')
		return {'FINISHED'}


class MAKE_IMITATION(Operator):
	"""Create imitation (3 prong)"""
	bl_label = 'JewelCraft: Make Imitation'
	bl_idname = 'jewelcraft.make_imitation'

	def execute(self, context):
		assets.make_setting_suppl('Imitation (3 prong)')
		return {'FINISHED'}






class MAKE_DUPLIFACE(Operator):
	"""Create dupli-face for selected objects"""
	bl_label = 'JewelCraft: Make Dupli-face'
	bl_idname = 'jewelcraft.make_dupliface'

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		assets.make_dupliface()
		return {'FINISHED'}


class SELECT_DOUBLES(Operator):
	"""Select duplicated gems (share same location)\n""" \
	"""WARNING: it does not work with dupli-faces, objects only"""
	bl_label = 'JewelCraft: Select Doubles'
	bl_idname = 'jewelcraft.select_doubles'

	def execute(self, context):
		prefs = context.user_preferences.addons[var.addon_id].preferences
		l = localization.locale[prefs.lang]

		doubles = assets.select_doubles()

		if doubles is not False:
			self.report({'WARNING'}, l['report_doubles'] % doubles)
		else:
			self.report({'INFO'}, l['report_no_doubles'])

		return {'FINISHED'}






class WEIGHT_DISPLAY(Operator):
	"""Display weight or volume for active mesh object"""
	bl_label = 'JewelCraft: Weighting'
	bl_idname = 'jewelcraft.weight_display'

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		stats.weight_display()
		return {'FINISHED'}






class EXPORT_PICK_SIZE(Operator):
	"""Pick active object"""
	bl_label = 'Pick Size'
	bl_idname = 'jewelcraft.export_pick_size'
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_size = context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_SHANK(Operator):
	"""Pick active object"""
	bl_label = 'Pick Shank'
	bl_idname = 'jewelcraft.export_pick_shank'
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_shank = context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_DIM(Operator):
	"""Pick active object"""
	bl_label = 'Pick Dim'
	bl_idname = 'jewelcraft.export_pick_dim'
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_dim = context.active_object.name
		return {'FINISHED'}


class EXPORT_PICK_WEIGHT(Operator):
	"""Pick active object"""
	bl_label = 'Pick Weight'
	bl_idname = 'jewelcraft.export_pick_weight'
	bl_options = {'INTERNAL'}

	def execute(self, context):
		context.scene.jewelcraft.export_weight = context.active_object.name
		return {'FINISHED'}


class EXPORT_STATS(Operator):
	"""Export project statistics"""
	bl_label = 'JewelCraft: Export Stats'
	bl_idname = 'jewelcraft.export_stats'

	def execute(self, context):
		prefs = context.user_preferences.addons[var.addon_id].preferences
		l = localization.locale[prefs.lang]

		export = stats.stats_export_to_file()

		if export is True:
			self.report({'INFO'}, l['report_stats'])
		else:
			utility.show_error_message(l['error_file'])

		return {'FINISHED'}
