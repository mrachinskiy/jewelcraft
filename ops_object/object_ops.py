from math import radians

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty
from bpy.app.translations import pgettext_iface as _
from mathutils import Matrix, Vector

from .. import var, dynamic_lists
from ..lib import unit, mesh
from ..lib.ui import popup_report


class OBJECT_OT_JewelCraft_Object_Mirror(Operator):
	"""Mirror selected objects"""
	bl_label = 'JewelCraft Mirror'
	bl_idname = 'object.jewelcraft_object_mirror'
	bl_options = {'REGISTER', 'UNDO'}

	x = BoolProperty(name='X', default=True, options={'SKIP_SAVE'})
	y = BoolProperty(name='Y', options={'SKIP_SAVE'})
	z = BoolProperty(name='Z', options={'SKIP_SAVE'})

	rot_z = FloatProperty(name='Z', step=10, soft_min=radians(-360.0), soft_max=radians(360.0), unit='ROTATION', options={'SKIP_SAVE'})

	use_cursor = BoolProperty(name='Use 3D Cursor')

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)

	def draw(self, context):
		layout = self.layout

		split = layout.split()
		split.label('Mirror Axis')
		col = split.column(align=True)
		col.prop(self, 'x')
		col.prop(self, 'y')
		col.prop(self, 'z')

		layout.separator()

		split = layout.split()
		split.label('Pivot Point')
		split.prop(self, 'use_cursor')

		layout.separator()

		split = layout.split()
		split.label('Adjust Rotation')
		split.prop(self, 'rot_z')

	def execute(self, context):
		scene = context.scene
		ofst = scene.cursor_location if self.use_cursor else (0.0, 0.0, 0.0)

		mat_z = Matrix.Rotation(self.rot_z, 4, 'Z')

		mat_y_180 = Matrix.Rotation(radians(180.0), 4, 'Y')
		mat_z_180 = Matrix.Rotation(radians(180.0), 4, 'Z')

		for ob in context.selected_objects:

			ob_copy = ob.copy()
			scene.objects.link(ob_copy)
			ob_copy.parent = None
			ob.select = False

			if ob_copy.constraints:
				for con in ob_copy.constraints:
					ob_copy.constraints.remove(con)

			ob_copy.matrix_world = ob.matrix_world

			# Mirror axes
			# ---------------------------

			if self.x:

				ob_copy.rotation_euler[1] = -ob_copy.rotation_euler[1]
				ob_copy.rotation_euler[2] = -ob_copy.rotation_euler[2]

				ob_copy.location[0] = ob_copy.location[0] - (ob_copy.location[0] - ofst[0]) * 2

			if self.y:

				ob_copy.rotation_euler[0] = -ob_copy.rotation_euler[0]
				ob_copy.rotation_euler[2] = -ob_copy.rotation_euler[2]

				ob_copy.location[1] = ob_copy.location[1] - (ob_copy.location[1] - ofst[1]) * 2

				ob_copy.matrix_basis *= mat_z_180

			if self.z:

				ob_copy.rotation_euler[0] = -ob_copy.rotation_euler[0]
				ob_copy.rotation_euler[1] = -ob_copy.rotation_euler[1]

				ob_copy.location[2] = ob_copy.location[2] - (ob_copy.location[2] - ofst[2]) * 2

				ob_copy.matrix_basis *= mat_y_180

			# Adjust orientation for mirrored objects
			# ---------------------------------------------

			if self.rot_z:
				ob_copy.matrix_basis *= mat_z

		scene.objects.active = ob_copy

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Lattice_Project(Operator):
	"""Project selected objects onto active object using Lattice"""
	bl_label = 'JewelCraft Lattice Project'
	bl_idname = 'object.jewelcraft_lattice_project'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) > 1

	def execute(self, context):
		surf = context.active_object
		surf.select = False

		obs = context.selected_objects

		bpy.ops.object.add(radius=1, type='LATTICE')
		lat = context.active_object
		md = lat.modifiers.new('Shrinkwrap', 'SHRINKWRAP')
		md.target = surf
		md.wrap_method = 'PROJECT'
		md.use_negative_direction = True
		md.use_project_z = True

		bbox = []

		for ob in obs:
			bbox += [ob.matrix_world * Vector(x) for x in ob.bound_box]
			ob.select = True
			md = ob.modifiers.new('Lattice', 'LATTICE')
			md.object = lat

		x_min = min(bbox, key=lambda x: x[0])[0]
		x_max = max(bbox, key=lambda x: x[0])[0]
		y_min = min(bbox, key=lambda x: x[1])[1]
		y_max = max(bbox, key=lambda x: x[1])[1]
		z_min = min(bbox, key=lambda x: x[2])[2]

		x_loc = (x_max + x_min) / 2
		y_loc = (y_max + y_min) / 2

		x_dim = abs(x_max - x_min)
		y_dim = abs(y_max - y_min)

		ratio = x_dim / y_dim

		if ratio >= 1.0:
			u_pt = round(10 * ratio)
			v_pt = 10
		else:
			u_pt = 10
			v_pt = round(10 / ratio)

		lat.location = (x_loc, y_loc, z_min)
		lat.scale[0] = x_dim
		lat.scale[1] = y_dim
		lat.data.points_u = u_pt
		lat.data.points_v = v_pt
		lat.data.points_w = 1

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Lattice_Profile(Operator):
	"""Deform active object profile with Lattice"""
	bl_label = 'JewelCraft Lattice Profile'
	bl_idname = 'object.jewelcraft_lattice_profile'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.active_object

		bpy.ops.object.add(radius=1, type='LATTICE')
		lat = context.active_object

		bbox = [ob.matrix_world * Vector(x) for x in ob.bound_box]

		lat.location = (ob.location[0], ob.location[1], bbox[1][2])
		lat.scale[1] = ob.dimensions[1] * 1.5

		lat.data.points_u = 1
		lat.data.points_v = 7
		lat.data.points_w = 1

		lat.data.points[0].co_deform[2] = -0.75
		lat.data.points[1].co_deform[2] = -0.3
		lat.data.points[2].co_deform[2] = -0.075

		lat.data.points[4].co_deform[2] = -0.075
		lat.data.points[5].co_deform[2] = -0.3
		lat.data.points[6].co_deform[2] = -0.75

		vgr = ob.vertex_groups.get('Group')

		if not vgr:
			ob.vertex_groups.new()
			vgr = ob.vertex_groups['Group']

		v_ids = []

		for v in ob.data.vertices:
			if v.co[2] > 0.1:
				v_ids.append(v.index)

		vgr.add(v_ids, 1.0, 'ADD')

		md = ob.modifiers.new('Lattice', 'LATTICE')
		md.object = lat
		md.vertex_group = vgr.name

		return {'FINISHED'}


class MESH_OT_JewelCraft_Weight_Display(Operator):
	"""Display weight or volume for active mesh object"""
	bl_label = 'JewelCraft Weighting'
	bl_idname = 'mesh.jewelcraft_weight_display'

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == 'MESH'

	def execute(self, context):
		props = context.window_manager.jewelcraft
		mat = props.weighting_mat
		obj = context.active_object
		vol = unit.to_metric(mesh.volume(obj), volume=True)

		if mat == 'VOLUME':
			weight = '{} {}'.format(round(vol, 4), _('mm³'))
			title = 'Volume'

		elif mat == 'CUSTOM':
			dens = unit.convert(props.weighting_dens, 'CM3_TO_MM3')
			weight = '{} {}'.format(round(vol * dens, 2), _('g'))
			title = 'Custom Density'

		else:
			dens = unit.convert(var.alloy_density[mat], 'CM3_TO_MM3')
			weight = '{} {}'.format(round(vol * dens, 2), _('g'))
			alloy_list = dynamic_lists.alloys(self, context)
			title = [x[1] for x in alloy_list if x[0] == mat][0]

		popup_report(self, weight, title=_(title))

		return {'FINISHED'}
