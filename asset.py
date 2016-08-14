import bpy
import random
from mathutils import Matrix
from . import var


def asset_import(ob_name=False, me_name=False):
	with bpy.data.libraries.load(var.asset_filepath) as (data_from, data_to):
		if ob_name:
			data_to.objects = [ob_name]
		if me_name:
			data_to.meshes = [me_name]

	return data_to


def link_to_scene(ob, active=False):
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
			color = [random.choice(seq), random.choice(seq), random.choice(seq)]
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


def to_size(orig_dim, targ_size):
	return orig_dim * targ_size


def to_dimensions(orig_dim, targ_dim):
	gap = targ_dim[1] * 0.01 # Make cutter sligtly bigger than gem
	return (targ_dim[0] + gap,
	        targ_dim[1] + gap,
	        targ_dim[1] * orig_dim[2] + gap)


def apply_transforms(ob):
	if ob.type == 'MESH':
		me = ob.data
		vec = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

		for i in range(3):
			mx = Matrix.Scale(ob.scale[i], 4, vec[i])
			for v in me.vertices:
				v.co = mx * v.co

		ob.scale = (1.0, 1.0, 1.0)
