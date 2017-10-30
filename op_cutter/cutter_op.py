import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty

from .. import var
from ..lib.asset import get_gem, bm_to_scene
from .cutter_mesh import create_cutter
from .cutter_draw import UI_Draw
from .cutter_presets import init_presets


def update_coords_handle(self, context):
	self.girdle_z_top, self.table_z = self.table_z, self.girdle_z_top


def update_coords_hole(self, context):
	self.hole_z_top, self.culet_z = self.culet_z, self.hole_z_top


class OBJECT_OT_JewelCraft_Cutter_Add(UI_Draw, Operator):
	"""Create cutter for selected gems"""
	bl_label = 'JewelCraft Make Cutter'
	bl_idname = 'object.jewelcraft_cutter_add'
	bl_options = {'REGISTER', 'UNDO'}

	auto_presets = BoolProperty(name='Use Automated Presets', description='Use automatically generated presets, discards user edits or presets', default=True)

	detalization = IntProperty(name='Detalization', default=32, min=12, soft_max=64, step=1)

	handle = BoolProperty(name='Handle', default=True, update=update_coords_handle)
	handle_l_size = FloatProperty(name='Handle Length', step=0.1, unit='LENGTH')
	handle_w_size = FloatProperty(name='Handle Width', step=0.1, unit='LENGTH')
	handle_z_top = FloatProperty(name='Handle Height Top', default=0.5, step=0.1, unit='LENGTH')
	handle_z_btm = FloatProperty(name='Handle Height Bottom', default=0.5, step=0.1, unit='LENGTH')

	girdle_l_ofst = FloatProperty(name='Girdle Length Offset', step=0.1, unit='LENGTH')
	girdle_w_ofst = FloatProperty(name='Girdle Width Offset', step=0.1, unit='LENGTH')
	girdle_z_top = FloatProperty(name='Girdle Height Top', default=0.05, step=0.1, unit='LENGTH')
	girdle_z_btm = FloatProperty(name='Girdle Height Bottom', step=0.1, unit='LENGTH')
	table_z = FloatProperty(name='Table Height', options={'HIDDEN'})

	hole = BoolProperty(name='Hole', default=True, update=update_coords_hole)
	hole_z_top = FloatProperty(name='Hole Height Top/Culet', default=0.25, step=0.1, unit='LENGTH')
	hole_z_btm = FloatProperty(name='Hole Height Bottom', default=1.0, step=0.1, unit='LENGTH')
	hole_l_size = FloatProperty(name='Hole Length', step=0.1, unit='LENGTH')
	hole_w_size = FloatProperty(name='Hole Width', step=0.1, unit='LENGTH')
	hole_pos_ofst = FloatProperty(name='Hole Position Offset', step=0.1, unit='LENGTH')
	culet_z = FloatProperty(name='Height Culet', options={'HIDDEN'})

	curve_seat = BoolProperty(name='Curve Seat')
	curve_seat_segments = IntProperty(name='Curve Seat Segments', default=15, min=2, soft_max=30, step=1)
	curve_seat_profile = FloatProperty(name='Curve Seat Profile', default=0.5, min=0.15, max=1.0, subtype='FACTOR')

	curve_profile = BoolProperty(name='Curve Profile')
	curve_profile_segments = IntProperty(name='Curve Profile Segments', default=10, min=1, soft_max=30, step=1)
	curve_profile_factor = FloatProperty(name='Curve Profile Factor', default=0.1, min=0.0, step=1)

	mul_1 = FloatProperty(name='Marquise Profile Factor 1', default=0.47, min=0.0, soft_max=1.0, step=0.01, subtype='FACTOR')
	mul_2 = FloatProperty(name='Marquise Profile Factor 2', default=1.4, min=0.0, soft_max=2.0, step=0.01, subtype='FACTOR')

	bevel_corners = BoolProperty(name='Bevel Corners')
	bevel_corners_width = FloatProperty(name='Bevel Corners Width', default=0.1, min=0.0, step=0.1, unit='LENGTH')
	bevel_corners_percent = FloatProperty(name='Bevel Corners Width (%)', default=18.0, min=0.0, max=50.0, step=1, subtype='PERCENTAGE')
	bevel_corners_segments = IntProperty(name='Bevel Corners Segments', default=1, min=1, soft_max=30, step=1)
	bevel_corners_profile = FloatProperty(name='Bevel Corners Profile', default=0.5, min=0.15, max=1.0, subtype='FACTOR')

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and bool(context.selected_objects)

	def __init__(self):
		if bpy.context.active_object is None:
			return

		get_gem(self)
		self.color = list(bpy.context.user_preferences.addons[var.addon_id].preferences.color_cutter)

		if self.auto_presets:
			init_presets(self)

	def execute(self, context):
		if bpy.context.active_object is None:
			return {'FINISHED'}

		bm = create_cutter(self)
		bm_to_scene(bm, name='Cutter', color=self.color)

		return {'FINISHED'}
