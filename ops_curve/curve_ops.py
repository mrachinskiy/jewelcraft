from math import radians

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty
from bpy.app.translations import pgettext_iface as _
import bmesh

from ..lib import unit, mesh
from ..lib.ui import popup_report


class CURVE_OT_JewelCraft_Size_Curve_Add(Operator):
	"""Create size curve"""
	bl_label = 'JewelCraft Make Size Curve'
	bl_idname = 'curve.jewelcraft_size_curve_add'
	bl_options = {'REGISTER', 'UNDO'}

	size = FloatProperty(name='Size', default=15.5, unit='LENGTH')
	up = BoolProperty(name='Start Up', default=True, description='Make curve start at the top', options={'SKIP_SAVE'})

	def execute(self, context):
		obs = context.selected_objects

		bpy.ops.curve.primitive_bezier_circle_add(radius=self.size / 2)

		obj = context.active_object
		obj.name = 'Size'
		obj.data.name = 'Size'
		obj.rotation_euler[0] = radians(90.0)
		obj.data.resolution_u = 512
		obj.data.use_radius = False

		if self.up:
			pp = context.space_data.pivot_point
			context.space_data.pivot_point = 'MEDIAN_POINT'

			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.transform.rotate(value=radians(180.0), axis=(0.0, 1.0, 0.0))
			bpy.ops.object.mode_set(mode='OBJECT')

			context.space_data.pivot_point = pp

		if obs:
			for ob in obs:
				md = ob.modifiers.new('Curve', 'CURVE')
				md.object = obj

		return {'FINISHED'}


class CURVE_OT_JewelCraft_Length_Display(Operator):
	"""Display curve length"""
	bl_idname = 'curve.jewelcraft_length_display'
	bl_label = 'JewelCraft Display Length'

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == 'CURVE'

	def execute(self, context):
		obj = context.active_object

		bv_dp = False
		bv_ob = False

		if obj.data.bevel_depth:
			bv_dp = obj.data.bevel_depth
			obj.data.bevel_depth = 0.0

		if obj.data.bevel_object:
			bv_ob = obj.data.bevel_object
			obj.data.bevel_object = None

		length = unit.to_metric(mesh.edges_length(obj))
		curve_length = '{:.2f} {}'.format(length, _('mm'))
		popup_report(self, curve_length, title=_('Curve Length'), icon='IPO_QUAD')

		if bv_dp:
			obj.data.bevel_depth = bv_dp

		if bv_ob:
			obj.data.bevel_object = bv_ob

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Stretch_Along_Curve(Operator):
	"""Stretch deformed objects along curve\n""" \
	"""IMPORTANT: Also works in Edit Mode with selected vertices"""
	bl_idname = 'object.jewelcraft_stretch_along_curve'
	bl_label = 'JewelCraft Stretch Along Curve'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects) or context.mode == 'EDIT_MESH'

	def execute(self, context):

		if context.mode == 'EDIT_MESH':

			obj = context.edit_object
			me = obj.data

			if obj.modifiers:
				for mod in obj.modifiers:
					if mod.type == 'CURVE' and mod.object:
						length = mesh.edges_length(mod.object)
						half_len = length / 2 / obj.scale[0]

						bm = bmesh.from_edit_mesh(me)

						for v in bm.verts:
							if v.select:
								if v.co[0] > 0.0:
									v.co[0] = half_len
								else:
									v.co[0] = -half_len

						bm.normal_update()
						bmesh.update_edit_mesh(me)

						break

		else:

			for ob in context.selected_objects:
				if ob.modifiers:
					for mod in ob.modifiers:
						if mod.type == 'CURVE' and mod.object:
							length = mesh.edges_length(mod.object)

							mod.show_viewport = False
							context.scene.update()
							ob.dimensions[0] = length
							mod.show_viewport = True

							break

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Move_Over_Under(Operator):
	"""Move deformed object over or under the curve"""
	bl_label = 'JewelCraft Move Over/Under'
	bl_idname = 'object.jewelcraft_move_over_under'
	bl_options = {'REGISTER', 'UNDO'}

	under = BoolProperty(name='Under', options={'SKIP_SAVE'})

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)

	def execute(self, context):
		scene = context.scene
		i = int(self.under)

		for ob in context.selected_objects:

			if ob.modifiers:
				for md in ob.modifiers:
					if md.type == 'CURVE':
						md_state = md.show_viewport
						md.show_viewport = False
						scene.update()
						ob.location[2] = md.object.location[2] - ob.bound_box[i][2] * ob.scale[2]
						md.show_viewport = md_state
						break
				else:
					ob.location[2] = -ob.bound_box[i][2] * ob.scale[2]

			else:
				ob.location[2] = -ob.bound_box[i][2] * ob.scale[2]

		return {'FINISHED'}
