import bpy
from mathutils import Matrix
from collections import defaultdict
from random import choice
from .. import var
from . import (
	units,
	utility,
)


def make_gem():
	scene = bpy.context.scene
	props = scene.jewelcraft
	size = props.make_gem_size
	stone = props.make_gem_stone
	stone_name = stone.replace('_', ' ').title()
	cut = props.make_gem_cut
	cut_name = cut.title()

	bpy.ops.object.select_all(action='DESELECT')

	imported = asset_import(ob_name=cut_name)
	ob = imported.objects[0]

	ob['gem'] = {'cut': cut, 'stone': stone}
	ob.location = scene.cursor_location
	ob.dimensions = to_size(ob.dimensions, size)
	material_assign(ob, stone, stone_name)
	sce_link(ob, active=True)


def replace_cut():
	cut = bpy.context.scene.jewelcraft.make_gem_cut
	cut_name = cut.title()

	imported = asset_import(me_name=cut_name)
	me = imported.meshes[0]

	for ob in bpy.context.selected_objects:
		utility.ob_id_compatibility(ob)
		if ('gem' in ob and ob['gem']['cut'] != cut):

			ob['gem']['cut'] = cut

			orig_size = ob.dimensions[1]
			orig_mats = ob.data.materials

			ob.data = me.copy()

			curr_size = ob.dimensions[1]
			size = orig_size / curr_size
			ob.scale = (size * ob.scale[0], size * ob.scale[1], size * ob.scale[2])
			apply_transforms(ob)
			ob.name = cut_name
			append = ob.data.materials.append
			for mat in orig_mats:
				append(mat)

	bpy.data.meshes.remove(me)
	del me


def replace_stone():
	stone = bpy.context.scene.jewelcraft.make_gem_stone
	stone_name = stone.replace('_', ' ').title()

	for ob in bpy.context.selected_objects:
		utility.ob_id_compatibility(ob)
		if ('gem' in ob and ob['gem']['stone'] != stone):
			ob['gem']['stone'] = stone
			material_assign(ob, stone, stone_name)






def make_gem_suppl(asset_type, seat_only=False):
	mat_name = asset_type.title()
	suffix = ' (Seat only)' if seat_only else ''

	for obj in bpy.context.selected_objects:
		utility.ob_id_compatibility(obj)
		if 'gem' in obj:
			cut = obj['gem']['cut']
			asset_name = '%s %s%s' % (cut.title(), mat_name, suffix)

			imported = asset_import(ob_name=asset_name)
			ob = imported.objects[0]

			ob.location = obj.location
			ob.rotation_euler = obj.rotation_euler

			if asset_type == 'CUTTER':
				dim = to_dimensions(ob.dimensions, obj.dimensions)
			else:
				dim = to_size(ob.dimensions, obj.dimensions[1])

			if obj.parent:
				ob.parent = obj.parent
				ob.matrix_parent_inverse = obj.matrix_parent_inverse
				dim = (
					dim[0] / obj.parent.scale[0],
					dim[1] / obj.parent.scale[1],
					dim[2] / obj.parent.scale[1]
				)

			ob.dimensions = dim

			material_assign(ob, asset_type, mat_name, gem_asset=False)
			sce_link(ob)


def make_setting_suppl(asset_name):
	asset_type = 'PRONGS'
	mat_name = 'Prongs'

	bpy.ops.object.select_all(action='DESELECT')

	imported = asset_import(ob_name=asset_name)
	ob = imported.objects[0]

	ob.location = bpy.context.scene.cursor_location
	material_assign(ob, asset_type, mat_name, gem_asset=False)
	sce_link(ob, active=True)






def make_dupliface():
	context = bpy.context
	data = bpy.data

	obs = context.selected_objects
	for ob in reversed(obs):
		utility.ob_id_compatibility(ob)
		if 'gem' in ob:
			break
	else:
		ob = obs[-1]

	df_name = '%s Duplifaces' % ob.name

	verts = [(-0.15, 0.15, 0.0), (0.15, 0.15, 0.0), (0.15, -0.15, 0.0), (-0.15, -0.15, 0.0)]
	faces = [(3, 2, 1, 0)]
	offset = (ob.dimensions[0] + 1.0, 0.0, 0.0)

	for i in range(4):
		verts[i] = [x+y for x,y in zip(verts[i], offset)]

	me = data.meshes.new(df_name)
	me.from_pydata(verts, [], faces)
	me.update()

	df = data.objects.new(df_name, me)
	df.location = ob.location
	df.dupli_type = 'FACES'
	context.scene.objects.link(df)

	for ob in obs:
		ob.parent = df
		apply_transforms(ob)
	bpy.ops.object.origin_clear()


def select_doubles():
	context = bpy.context
	scene = context.scene
	gems_loc = []
	gems_name = []

	bpy.ops.object.select_all(action='DESELECT')

	loc_app = gems_loc.append
	name_app = gems_name.append
	for ob in context.visible_objects:
		utility.ob_id_compatibility(ob)
		if 'gem' in ob:
			loc_app(ob.location.freeze())
			name_app(ob.name)

	doubles = defaultdict(list)
	for i,item in enumerate(gems_loc):
		doubles[item].append(i)
	doubles = {k:v for k,v in doubles.items() if len(v)>1}

	if doubles:
		d = 0
		for i in doubles.items():
			for p in i[1][:-1]:
				scene.objects[gems_name[i[1][p]]].select = True
				d += 1
		return d

	return False






# Utility


def asset_import(ob_name=False, me_name=False):
	with bpy.data.libraries.load(var.asset_filepath) as (data_from, data_to):
		if ob_name:
			data_to.objects = [ob_name]
		if me_name:
			data_to.meshes = [me_name]

	return data_to


def sce_link(ob, active=False):
	bpy.context.scene.objects.link(ob)
	if active:
		bpy.context.scene.objects.active = ob
	ob.select = True
	apply_transforms(ob)


def material_assign(ob, ob_type, mat_name, gem_asset=True):

	mat = bpy.data.materials.get(mat_name)


	if not mat:
		mat = bpy.data.materials.new(mat_name)
		color = var.default_color.get(ob_type)
		if not color:
			seq = (0.0, 0.5, 1.0)
			color = [choice(seq), choice(seq), choice(seq)]
		mat.diffuse_color = color
		if not gem_asset:
			mat.specular_color = (0.0, 0.0, 0.0)

		if bpy.context.scene.render.engine == 'CYCLES':
			mat.use_nodes = True
			nodes = mat.node_tree.nodes
			nodes.remove(nodes['Diffuse BSDF'])
			if gem_asset:
				node = nodes.new('ShaderNodeBsdfGlass')
			else:
				node = nodes.new('ShaderNodeBsdfGlossy')
			node.location = (0.0, 300.0)
			node.inputs['Color'].default_value = color + [1.0]
			mat.node_tree.links.new(node.outputs['BSDF'], nodes['Material Output'].inputs['Surface'])


	if len(ob.material_slots) < 1:
		ob.data.materials.append(mat)
	else:
		ob.material_slots[0].material = mat






# Transform utility


def to_size(orig_dim, targ_size):
	return orig_dim * targ_size


def to_dimensions(orig_dim, targ_dim):
	gap = targ_dim[1] * 0.01 # Make cutter sligtly bigger than gem
	return (
		targ_dim[0] + gap,
		targ_dim[1] + gap,
		targ_dim[1] * orig_dim[2] + gap
	)


def apply_transforms(ob):
	if ob.type == 'MESH':
		me = ob.data
		vec = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

		for i in range(3):
			mx = Matrix.Scale(ob.scale[i], 4, vec[i])
			for v in me.vertices:
				v.co = mx * v.co

		ob.scale = (1.0, 1.0, 1.0)
