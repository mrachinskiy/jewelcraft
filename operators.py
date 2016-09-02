import bpy
import os
import collections
from bpy.types import Operator
from bpy.props import (
	EnumProperty,
	StringProperty,
	BoolProperty,
	)
from . import (
	var,
	locale,
	asset,
	stats,
	prop_items,
	units,
	volume,
	)


class Locale:

	def __init__(self):
		prefs = bpy.context.user_preferences.addons[var.addon_id].preferences
		self.l = locale.locale[prefs.lang]


class SEARCH_STONE(Operator):
	"""Search stone by name"""
	bl_label = 'Search Stone'
	bl_idname = 'jewelcraft.search_stone'
	bl_property = 'stone'
	bl_options = {'INTERNAL'}

	stone = EnumProperty(items=prop_items.stones)

	def execute(self, context):
		context.scene.jewelcraft.gem_stone = self.stone
		context.area.tag_redraw()
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'FINISHED'}


class Gem(Locale):

	def __init__(self):
		super().__init__()
		self.props = bpy.context.scene.jewelcraft
		self.size = self.props.gem_size
		self.stone = self.props.gem_stone
		self.stone_name = self.stone.replace('_', ' ').title()
		self.cut = self.props.gem_cut
		self.cut_name = self.cut.title()


class MAKE_GEM(Gem, Operator):
	"""Create gemstone"""
	bl_label = 'Make Gem'
	bl_idname = 'jewelcraft.make_gem'

	def execute(self, context):
		if self.size == 0.0:
			self.report({'WARNING'}, self.l['error_zero_gem'])
			return {'FINISHED'}

		bpy.ops.object.select_all(action='DESELECT')

		imported = asset.asset_import(ob_name=self.cut_name)
		ob = imported.objects[0]

		ob['gem'] = {'cut': self.cut, 'stone': self.stone}
		ob.location = context.scene.cursor_location
		ob.dimensions = asset.to_size(ob.dimensions, self.size)
		asset.material_assign(ob, self.stone, self.stone_name)
		asset.link_to_scene(ob, active=True)

		return {'FINISHED'}


class REPLACE_STONE(Gem, Operator):
	"""Replace stone for selected gems"""
	bl_label = 'Replace Stone'
	bl_idname = 'jewelcraft.replace_stone'

	def execute(self, context):
		obs = context.selected_objects
		if not obs:
			self.report({'WARNING'}, self.l['error_no_selected'])
			return {'FINISHED'}

		for ob in obs:
			stats.ob_id_compatibility(ob)
			if ('gem' in ob and ob['gem']['stone'] != self.stone):
				ob['gem']['stone'] = self.stone
				asset.material_assign(ob, self.stone, self.stone_name)

		return {'FINISHED'}


class REPLACE_CUT(Gem, Operator):
	"""Replace cut for selected gems"""
	bl_label = 'Replace Cut'
	bl_idname = 'jewelcraft.replace_cut'

	def execute(self, context):
		obs = context.selected_objects
		if not obs:
			self.report({'WARNING'}, self.l['error_no_selected'])
			return {'FINISHED'}

		imported = asset.asset_import(me_name=self.cut_name)
		me = imported.meshes[0]

		for ob in obs:

			stats.ob_id_compatibility(ob)

			if ('gem' in ob and ob['gem']['cut'] != self.cut):

				ob['gem']['cut'] = self.cut

				orig_size = ob.dimensions[1]
				orig_mats = ob.data.materials

				ob.data = me.copy()

				curr_size = ob.dimensions[1]
				size = orig_size / curr_size
				ob.scale = (size * ob.scale[0], size * ob.scale[1], size * ob.scale[2])
				asset.apply_transforms(ob)
				ob.name = self.cut_name
				append = ob.data.materials.append
				for mat in orig_mats:
					append(mat)

		bpy.data.meshes.remove(me)
		del me

		return {'FINISHED'}


class GemSuppl(Locale):
	bl_options = {'INTERNAL'}

	def make_gem_suppl(self, context):
		mat_name = self.asset_type.title()
		suffix = ' (Seat only)' if self.seat_only else ''

		for obj in context.selected_objects:

			stats.ob_id_compatibility(obj)

			if 'gem' in obj:
				cut_name = obj['gem']['cut'].title()
				asset_name = '%s %s%s' % (cut_name, mat_name, suffix)

				imported = asset.asset_import(ob_name=asset_name)
				ob = imported.objects[0]

				ob.location = obj.location
				ob.rotation_euler = obj.rotation_euler

				if self.asset_type == 'CUTTER':
					dim = asset.to_dimensions(ob.dimensions, obj.dimensions)
				else:
					dim = asset.to_size(ob.dimensions, obj.dimensions[1])

				if obj.parent:
					ob.parent = obj.parent
					ob.matrix_parent_inverse = obj.matrix_parent_inverse
					dim = (dim[0] / obj.parent.scale[0],
					       dim[1] / obj.parent.scale[1],
					       dim[2] / obj.parent.scale[1])

				ob.dimensions = dim

				asset.material_assign(ob, self.asset_type, mat_name, gem_asset=False)
				asset.link_to_scene(ob)


class MAKE_PRONGS(GemSuppl, Operator):
	"""Create prongs for selected gems"""
	bl_label = 'Make Prongs'
	bl_idname = 'jewelcraft.make_prongs'

	asset_type = 'PRONGS'
	seat_only = False

	def execute(self, context):
		if not context.selected_objects:
			self.report({'WARNING'}, self.l['error_no_selected'])
		self.make_gem_suppl(context)
		return {'FINISHED'}


class MAKE_CUTTER(GemSuppl, Operator):
	"""Create cutter for selected gems"""
	bl_label = 'Make Cutter'
	bl_idname = 'jewelcraft.make_cutter'

	asset_type = 'CUTTER'
	seat_only = BoolProperty(options={'HIDDEN', 'SKIP_SAVE'})

	def execute(self, context):
		if not context.selected_objects:
			self.report({'WARNING'}, self.l['error_no_selected'])
		self.make_gem_suppl(context)
		return {'FINISHED'}


class SettingSuppl(Operator):
	bl_options = {'INTERNAL'}

	def make_setting_suppl(self, context):
		asset_type = 'PRONGS'
		mat_name = 'Prongs'

		bpy.ops.object.select_all(action='DESELECT')

		imported = asset.asset_import(ob_name=self.asset_name)
		ob = imported.objects[0]

		ob.location = context.scene.cursor_location
		asset.material_assign(ob, asset_type, mat_name, gem_asset=False)
		asset.link_to_scene(ob, active=True)


class MAKE_SINGLE_PRONG(SettingSuppl, Operator):
	"""Create single prong"""
	bl_label = 'Make Single Prong'
	bl_idname = 'jewelcraft.make_single_prong'

	asset_name = 'Single Prong'

	def execute(self, context):
		self.make_setting_suppl(context)
		return {'FINISHED'}


class MAKE_IMITATION(SettingSuppl, Operator):
	"""Create imitation (3 prong)"""
	bl_label = 'Make Imitation'
	bl_idname = 'jewelcraft.make_imitation'

	asset_name = 'Imitation (3 prong)'

	def execute(self, context):
		self.make_setting_suppl(context)
		return {'FINISHED'}


class MAKE_DUPLIFACE(Locale, Operator):
	"""Create dupli-face for selected objects"""
	bl_label = 'Make Dupli-face'
	bl_idname = 'jewelcraft.make_dupliface'

	def execute(self, context):
		obs = context.selected_objects
		if not obs:
			self.report({'WARNING'}, self.l['error_no_selected'])
			return {'FINISHED'}

		for ob in reversed(obs):
			stats.ob_id_compatibility(ob)
			if 'gem' in ob:
				break
		else:
			ob = obs[-1]

		df_name = ob.name + ' Duplifaces'

		verts = [(-0.15, 0.15, 0.0), (0.15, 0.15, 0.0), (0.15, -0.15, 0.0), (-0.15, -0.15, 0.0)]
		faces = [(3, 2, 1, 0)]
		offset = (ob.dimensions[0] + 1.0, 0.0, 0.0)

		for i in range(4):
			verts[i] = [x+y for x,y in zip(verts[i], offset)]

		me = bpy.data.meshes.new(df_name)
		me.from_pydata(verts, [], faces)
		me.update()

		df = bpy.data.objects.new(df_name, me)
		df.location = ob.location
		df.dupli_type = 'FACES'
		context.scene.objects.link(df)

		for ob in obs:
			ob.parent = df
			asset.apply_transforms(ob)
		bpy.ops.object.origin_clear()

		return {'FINISHED'}


class SELECT_DOUBLES(Locale, Operator):
	"""Select duplicated gems (share same location)\n""" \
	"""WARNING: it does not work with dupli-faces, objects only"""
	bl_label = 'Select Doubles'
	bl_idname = 'jewelcraft.select_doubles'

	def execute(self, context):
		scene = context.scene
		gems_loc = []
		gems_name = []

		bpy.ops.object.select_all(action='DESELECT')

		loc_app = gems_loc.append
		name_app = gems_name.append
		for ob in context.visible_objects:
			stats.ob_id_compatibility(ob)
			if 'gem' in ob:
				loc_app(ob.location.freeze())
				name_app(ob.name)

		doubles = collections.defaultdict(list)
		for i,item in enumerate(gems_loc):
			doubles[item].append(i)
		doubles = {k:v for k,v in doubles.items() if len(v)>1}

		if doubles:
			d = 0
			for i in doubles.items():
				for p in i[1][:-1]:
					scene.objects[gems_name[i[1][p]]].select = True
					d += 1
			doubles = d

		if doubles:
			self.report({'WARNING'}, self.l['report_doubles'] % doubles)
		else:
			self.report({'INFO'}, self.l['report_no_doubles'])

		return {'FINISHED'}


class WEIGHT_DISPLAY(Locale, Operator):
	"""Display weight or volume for active mesh object"""
	bl_label = 'Weighting'
	bl_idname = 'jewelcraft.weight_display'

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		props = context.scene.jewelcraft
		metal = props.weighting_metals
		ob_volume = units.system(volume.calculate(context.active_object), volume=True)

		if metal == 'VOLUME':
			var.weighting_report = '{} {}'.format(round(ob_volume, 4), self.l['mm3'])

		elif metal == 'CUSTOM':
			dens = units.convert(props.weighting_custom, 'cm3->mm3')
			var.weighting_report = '{} {}'.format(round(ob_volume * dens, 2), self.l['g'])

		else:
			mdens = units.convert(var.metal_density[metal], 'cm3->mm3')
			var.weighting_report = '{} {}'.format(round(ob_volume * mdens, 2), self.l['g'])

		return {'FINISHED'}


class STATS_PICK(Operator):
	"""Pick active object"""
	bl_label = 'Pick'
	bl_idname = 'jewelcraft.stats_pick'
	bl_options = {'INTERNAL'}

	prop = StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

	def execute(self, context):
		props = context.scene.jewelcraft
		ob_name = context.active_object.name
		setattr(props, self.prop, ob_name)
		return {'FINISHED'}


class STATS_EXPORT(Locale, Operator):
	"""Export project statistics to text file"""
	bl_label = 'Export Stats'
	bl_idname = 'jewelcraft.stats_export'

	def execute(self, context):
		if bpy.data.is_saved:
			stats_data = stats.fmt()
			filepath = bpy.data.filepath
			filename = os.path.splitext(os.path.basename(filepath))[0]
			save_path = os.path.join(os.path.dirname(filepath), filename + ' stats.txt')

			with open(save_path, 'w', encoding='utf-8') as file:
				file.write(stats_data)

			self.report({'INFO'}, self.l['report_stats'])

		else:
			self.report({'ERROR'}, self.l['error_file'])

		return {'FINISHED'}
