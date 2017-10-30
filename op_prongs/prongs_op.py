from math import radians

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty

from .. import var
from ..lib.asset import get_gem, bm_to_scene
from .prongs_draw import UI_Draw
from .prongs_presets import init_presets
from .prongs_mesh import create_prongs


class OBJECT_OT_JewelCraft_Prongs_Add(UI_Draw, Operator):
	"""Create prongs for selected gems"""
	bl_label = 'JewelCraft Make Prongs'
	bl_idname = 'object.jewelcraft_prongs_add'
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	auto_presets = BoolProperty(name='Use Automated Presets', description='Use automatically generated presets, discards user edits or presets', default=True)

	number = IntProperty(name='Prong Number', default=4, min=1, soft_max=10)

	diameter = FloatProperty(name='Diameter', default=0.4, min=0.0, step=1, unit='LENGTH')
	z_top = FloatProperty(name='Height Top', default=0.4, step=1, unit='LENGTH')
	z_btm = FloatProperty(name='Height Bottom', default=0.5, step=1, unit='LENGTH')

	position = FloatProperty(name='Position', default=radians(45.0), step=100, precision=0, unit='ROTATION')
	intersection = FloatProperty(name='Intersection', default=30.0, soft_min=0.0, soft_max=100.0, precision=0, subtype='PERCENTAGE')
	alignment = FloatProperty(name='Alignment', step=100, precision=0, unit='ROTATION')

	symmetry = BoolProperty(name='Symmetry')
	symmetry_pivot = FloatProperty(name='Symmetry Pivot', step=100, precision=0, unit='ROTATION')

	bump_scale = FloatProperty(name='Bump Scale', default=0.5, soft_min=0.0, soft_max=1.0, subtype='FACTOR')
	taper = FloatProperty(name='Taper', default=0.0, min=0.0, soft_max=1.0, subtype='FACTOR')

	detalization = IntProperty(name='Detalization', default=32, min=12, soft_max=64, step=1)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and bool(context.selected_objects)

	def __init__(self):
		if bpy.context.active_object is None:
			return

		get_gem(self)
		self.color = list(bpy.context.user_preferences.addons[var.addon_id].preferences.color_prongs)

		if self.auto_presets:
			init_presets(self)

	def execute(self, context):
		bm = create_prongs(self)
		bm_to_scene(bm, name='Prongs', color=self.color)

		return {'FINISHED'}
