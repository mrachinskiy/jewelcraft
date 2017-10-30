import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty
from mathutils import Matrix

from ..lib import asset


class OBJECT_OT_JewelCraft_Make_Dupliface(Operator):
	"""Create dupli-face for selected objects\n""" \
	"""WARNING: Select Doubles do not work with dupli-faces, objects only"""
	bl_label = 'JewelCraft Make Dupli-face'
	bl_idname = 'object.jewelcraft_make_dupliface'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)

	def execute(self, context):
		scene = context.scene
		obs = context.selected_objects

		for ob in reversed(obs):
			if 'gem' in ob:
				break
		else:
			ob = obs[-1]

		df_name = ob.name + ' Dupli-faces'

		verts = [(-0.0866, -0.05, 0.0), (0.0866, -0.05, 0.0), (0.0, 0.1, 0.0)]
		faces = [(0, 1, 2)]
		offset = (ob.dimensions[0] + 1.0, 0.0, 0.0)

		for i in range(3):
			verts[i] = [x + y for x, y in zip(verts[i], offset)]

		me = bpy.data.meshes.new(df_name)
		me.from_pydata(verts, [], faces)

		df = bpy.data.objects.new(df_name, me)
		df.location = ob.location
		df.dupli_type = 'FACES'
		scene.objects.link(df)

		for ob in obs:
			asset.apply_scale(ob)
			ob.parent = df
			mat_loc = Matrix.Translation(ob.location[:])
			ob.matrix_parent_inverse = mat_loc.inverted()

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Dist_Helper_Add(Operator):
	"""Create distance helper for selected gems"""
	bl_label = 'JewelCraft Make Helper'
	bl_idname = 'object.jewelcraft_dist_helper_add'
	bl_options = {'REGISTER', 'UNDO'}

	helper_size_ofst = FloatProperty(name='Helper Size Offset', default=0.2, unit='LENGTH')
	remove = BoolProperty(options={'HIDDEN', 'SKIP_SAVE'})

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)

	def execute(self, context):
		obs = context.selected_objects

		if self.remove:
			for ob in context.scene.objects:
				if 'helper' in ob and ob.parent in obs:
					context.scene.objects.unlink(ob)
					bpy.data.objects.remove(ob)

		else:
			ob = obs[0]
			asset.dist_helper(ob, self.helper_size_ofst)

		return {'FINISHED'}
