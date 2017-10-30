import bpy
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Operator

from .. import var, dynamic_lists
from ..lib import asset, compat


class OBJECT_OT_JewelCraft_Gem_Add(Operator):
	"""Create set gemstone"""
	bl_label = 'JewelCraft Make Gem'
	bl_idname = 'object.jewelcraft_gem_add'
	bl_options = {'REGISTER', 'UNDO'}

	cut = EnumProperty(name='Cut', items=dynamic_lists.cuts)
	stone = EnumProperty(name='Stone', items=dynamic_lists.stones)
	size = FloatProperty(name='Size', description='Gem size', default=1.0, min=0.0, step=10, precision=2, unit='LENGTH')

	def __init__(self):
		asset.init_gem(self)

	def draw(self, context):
		layout = self.layout

		split = layout.split()
		split.label('Size')
		split.prop(self, 'size', text='')

		split = layout.split()
		split.label('Stone')
		split.prop(self, 'stone', text='')

		layout.template_icon_view(self, 'cut', show_labels=True)

	def execute(self, context):

		if self.size == 0:
			self.report({'ERROR'}, 'Gem size cannot be 0 mm')
			return {'FINISHED'}

		scene = context.scene

		for ob in scene.objects:
			ob.select = False

		asset.set_stone_name(self)
		asset.set_cut_name(self)

		imported = asset.asset_import(filepath=var.gem_asset_filepath, ob_name=self.cut_name)
		ob = imported.objects[0]

		ob['gem'] = {'cut': self.cut, 'stone': self.stone}
		ob.scale = ob.scale * self.size
		ob.location = scene.cursor_location
		asset.add_material_for_gem(self, ob)

		asset.apply_scale(ob)
		scene.objects.link(ob)
		ob.select = True

		if context.mode == 'EDIT_MESH':
			asset.face_pos(ob)
			bpy.ops.object.mode_set(mode='OBJECT')

		scene.objects.active = ob

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Stone_Replace(Operator):
	"""Replace stone for selected gems"""
	bl_label = 'JewelCraft Replace Stone'
	bl_idname = 'object.jewelcraft_stone_replace'
	bl_options = {'REGISTER', 'UNDO'}

	stone = EnumProperty(name='Stone', items=dynamic_lists.stones)

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)

	def __init__(self):
		asset.init_gem(self)

	def draw(self, context):
		layout = self.layout

		split = layout.split()
		split.label('Stone')
		split.prop(self, 'stone', text='')

	def execute(self, context):
		asset.set_stone_name(self)

		for ob in context.selected_objects:
			compat.gem_id_compat(ob)
			if 'gem' in ob:
				ob['gem']['stone'] = self.stone
				asset.add_material_for_gem(self, ob)

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Cut_Replace(Operator):
	"""Replace cut for selected gems"""
	bl_label = 'JewelCraft Replace Cut'
	bl_idname = 'object.jewelcraft_cut_replace'
	bl_options = {'REGISTER', 'UNDO'}

	cut = EnumProperty(name='Cut', items=dynamic_lists.cuts)

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)

	def __init__(self):
		asset.init_gem(self)

	def draw(self, context):
		layout = self.layout
		layout.template_icon_view(self, 'cut', show_labels=True)

	def execute(self, context):
		asset.set_cut_name(self)
		scene = context.scene
		imported = asset.asset_import(filepath=var.gem_asset_filepath, me_name=self.cut_name)
		me = imported.meshes[0]

		for ob in context.selected_objects:
			compat.gem_id_compat(ob)
			if 'gem' in ob:

				orig_size = ob.dimensions[1]
				orig_mats = ob.data.materials

				asset.apply_scale(ob)

				ob.data = me.copy()
				ob['gem']['cut'] = self.cut
				ob.name = self.cut_name

				scene.update()

				curr_size = ob.dimensions[1]
				size = orig_size / curr_size
				ob.scale = ob.scale * size

				asset.apply_scale(ob)

				for mat in orig_mats:
					ob.data.materials.append(mat)

		bpy.data.meshes.remove(me)
		del me

		return {'FINISHED'}


class OBJECT_OT_JewelCraft_Gem_ID_Add(Operator):
	"""Add gem identifiers to selected objects"""
	bl_label = 'JewelCraft Add Gem ID'
	bl_idname = 'object.jewelcraft_gem_id_add'
	bl_options = {'REGISTER', 'UNDO'}

	cut = EnumProperty(name='Cut', items=dynamic_lists.cuts)
	stone = EnumProperty(name='Stone', items=dynamic_lists.stones)

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)

	def __init__(self):
		asset.init_gem(self)

	def draw(self, context):
		layout = self.layout

		split = layout.split()
		split.label('Stone')
		split.prop(self, 'stone', text='')

		layout.template_icon_view(self, 'cut', show_labels=True)

	def execute(self, context):
		for ob in context.selected_objects:
			compat.gem_id_compat(ob)
			if ob.type == 'MESH':
				ob['gem'] = {'cut': self.cut, 'stone': self.stone}

		return {'FINISHED'}
