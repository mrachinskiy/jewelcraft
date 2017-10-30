import collections

import bpy
from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from bpy.app.translations import pgettext_tip as _

from .. import dynamic_lists


class OBJECT_OT_JewelCraft_Select_Gems_By_Trait(Operator):
	"""Select gems by trait"""
	bl_label = 'JewelCraft Select Gems By Trait'
	bl_idname = 'object.jewelcraft_select_gems_by_trait'
	bl_options = {'REGISTER', 'UNDO'}

	filter_size = BoolProperty(name='Size', options={'SKIP_SAVE'})
	filter_stone = BoolProperty(name='Stone', options={'SKIP_SAVE'})
	filter_cut = BoolProperty(name='Cut', options={'SKIP_SAVE'})
	filter_similar = BoolProperty(options={'SKIP_SAVE', 'HIDDEN'})

	size = FloatProperty(name='Size', default=1.0, min=0.0, step=10, precision=2, unit='LENGTH')
	stone = EnumProperty(name='Stone', items=dynamic_lists.stones)
	cut = EnumProperty(name='Cut', items=dynamic_lists.cuts)

	def __init__(self):
		props = bpy.context.window_manager.jewelcraft
		obj = bpy.context.active_object

		if self.filter_similar and obj and 'gem' in obj:
			self.filter_size = True
			self.filter_stone = True
			self.filter_cut = True
			self.size = obj.dimensions[1]
			self.stone = obj['gem']['stone']
			self.cut = obj['gem']['cut']
		else:
			self.stone = props.gem_stone
			self.cut = props.gem_cut

	def draw(self, context):
		layout = self.layout

		split = layout.split()
		split.prop(self, 'filter_size')
		split.prop(self, 'size')

		split = layout.split()
		split.prop(self, 'filter_stone')
		split.prop(self, 'stone', text='')

		split = layout.split()
		split.prop(self, 'filter_cut', text='Cut', text_ctxt='JewelCraft')
		split.template_icon_view(self, 'cut', show_labels=True)

	def execute(self, context):
		obs = context.visible_objects
		size = round(self.size, 2)

		condition = 'for ob in obs:'
		condition += '\n\tif "gem" in ob'

		if self.filter_size:
			condition += ' and round(ob.dimensions[1], 2) == size'
		if self.filter_stone:
			condition += ' and ob["gem"]["stone"] == self.stone'
		if self.filter_cut:
			condition += ' and ob["gem"]["cut"] == self.cut'

		condition += ': ob.select = True'
		condition += '\n\telse: ob.select = False'

		exec(condition)

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Select_Doubles(Operator):
	"""Select duplicated gems (located in the same spot)\n""" \
	"""WARNING: it does not work with dupli-faces, objects only"""
	bl_label = 'JewelCraft Select Doubles'
	bl_idname = 'object.jewelcraft_select_doubles'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		doubles = collections.defaultdict(list)

		for ob in context.visible_objects:
			ob.select = False
			if 'gem' in ob:
				loc = ob.matrix_world.to_translation().to_tuple()
				doubles[loc].append(ob)

		doubles = {k: v for k, v in doubles.items() if len(v) > 1}

		if doubles:
			d = 0
			for obs in doubles.values():
				for ob in obs[:-1]:
					ob.select = True
					d += 1

			self.report({'WARNING'}, _('Found {} duplicates').format(d))

		else:
			self.report({'INFO'}, 'No duplicates found')

		return {'FINISHED'}
