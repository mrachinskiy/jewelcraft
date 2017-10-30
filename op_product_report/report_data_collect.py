import collections

import bpy

from .. import dynamic_lists
from ..lib import unit, mesh
from ..lib.compat import gem_id_compat


def data_collect():
	scene = bpy.context.scene
	props = scene.jewelcraft

	data = {}

	# Size
	# ---------------------------

	if props.product_report_ob_size:
		ob = props.product_report_ob_size
		size = max(ob.dimensions)
		data['size'] = unit.to_metric(size)

	# Shank
	# ---------------------------

	if props.product_report_ob_shank:
		ob = props.product_report_ob_shank

		for mod in reversed(ob.modifiers):
			if mod.type == 'CURVE':
				mod_state = mod.show_viewport
				mod.show_viewport = False
				scene.update()
				dim = list(ob.dimensions)
				mod.show_viewport = mod_state
				scene.update()
				break
		else:
			dim = list(ob.dimensions)

		dim.remove(max(dim))
		data['shank'] = unit.to_metric(dim, batch=True)

	# Dimensions
	# ---------------------------

	if props.product_report_ob_dim:
		ob = props.product_report_ob_dim
		data['dim'] = unit.to_metric(ob.dimensions.to_tuple(), batch=True)

	# Weight
	# ---------------------------

	materials = []
	alloy_list = dynamic_lists.alloys(None, bpy.context)[:-1]

	for mat in alloy_list:
		if getattr(props, 'product_report_mat_' + mat[0].lower()):
			materials.append(mat[0])

	if props.product_report_ob_weight and materials:
		ob = props.product_report_ob_weight
		vol = mesh.volume(ob)
		data['weight'] = unit.to_metric(vol, volume=True)
		data['weight_mats'] = materials

	# Gems
	# ---------------------------

	sg = {}
	hidden = False
	df_leftovers = False
	doubles = collections.defaultdict(int)

	for ob in scene.objects:

		gem_id_compat(ob)

		if 'gem' in ob:

			if ob.hide:
				hidden = True

			loc = ob.matrix_world.to_translation().to_tuple()
			doubles[loc] += 1

			stone = ob['gem']['stone']
			cut = ob['gem']['cut']
			size = tuple([round(x, 2) for x in unit.to_metric(ob.dimensions, batch=True)])

			# Handle Dupli-faces
			if ob.parent and ob.parent.type == 'MESH':
				if ob.parent.dupli_type == 'FACES':
					count = mesh.polycount(ob.parent)
				elif ob.parent.dupli_type == 'NONE':
					count = 1
					df_leftovers = True
			else:
				count = 1

			if stone in sg and cut in sg[stone] and size in sg[stone][cut]:
				sg[stone][cut][size] += count
			elif stone in sg and cut in sg[stone]:
				sg[stone][cut][size] = count
			elif stone in sg:
				sg[stone][cut] = {size: count}
			else:
				sg[stone] = {cut: {size: count}}

	data['gems'] = sg

	# Find duplicates
	# ---------------------------

	doubles = [x for x in doubles.values() if x > 1]

	# Warnings
	# ---------------------------

	data['warn'] = []

	if hidden:
		data['warn'].append('Discovered hidden gems in the scene (use Show Hidden/Alt H)')

	if df_leftovers:
		data['warn'].append('Discovered possible gem Dupli-face leftovers')

	if doubles:
		data['warn'].append('Discovered duplicated gems')

	return data
