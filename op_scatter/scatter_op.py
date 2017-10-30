from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty

from .scatter_draw import UI_Draw
from .scatter_func import Scatter


class OBJECT_OT_JewelCraft_Scatter_Along_Curve(UI_Draw, Scatter, Operator):
	"""Scatter selected object along active curve"""
	bl_idname = 'object.jewelcraft_scatter_along_curve'
	bl_label = 'JewelCraft Scatter Along Curve'
	bl_options = {'REGISTER', 'UNDO'}

	redistribute = False

	number = IntProperty(name='Object Number', default=10, min=2, soft_max=100)

	rot_y = FloatProperty(name='Orientation', step=10, unit='ROTATION')
	rot_z = FloatProperty(name='Rotation', step=10, unit='ROTATION')
	loc_z = FloatProperty(name='Position', unit='LENGTH')

	start = FloatProperty(name='Start')
	end = FloatProperty(name='End', default=100.0)

	absolute_ofst = BoolProperty(name='Absolute Offset')
	spacing = FloatProperty(name='Spacing', default=0.2, unit='LENGTH')

	helper = BoolProperty(name='Helper')
	helper_size_ofst = FloatProperty(name='Helper Size Offset', default=0.2, unit='LENGTH')

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) > 1


class OBJECT_OT_JewelCraft_Redistribute_Along_Curve(UI_Draw, Scatter, Operator):
	"""Redistribute scattering for selected objects"""
	bl_idname = 'object.jewelcraft_redistribute_along_curve'
	bl_label = 'JewelCraft Redistribute Along Curve'
	bl_options = {'REGISTER', 'UNDO'}

	redistribute = True

	rot_y = FloatProperty(name='Orientation', step=10, unit='ROTATION', options={'SKIP_SAVE'})
	rot_z = FloatProperty(name='Rotation', step=10, unit='ROTATION', options={'SKIP_SAVE'})
	loc_z = FloatProperty(name='Position', unit='LENGTH', options={'SKIP_SAVE'})

	start = FloatProperty(name='Start')
	end = FloatProperty(name='End', default=100.0)

	absolute_ofst = BoolProperty(name='Absolute Offset')
	spacing = FloatProperty(name='Spacing', default=0.2, unit='LENGTH')

	helper = BoolProperty(name='Helper')
	helper_size_ofst = FloatProperty(name='Helper Size Offset', default=0.2, unit='LENGTH')

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)
