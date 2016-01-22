import bpy
from mathutils import Matrix
from collections import defaultdict
from .. import var
from . import units


def gem_import():
	props = bpy.context.scene.jewelcraft
	tpe = props.import_gem_type
	cut = props.import_gem_cut
	size = props.import_gem_size

	data_to = asset_import(ob_name=cut.title(), mat_name=tpe.replace('_', ' ').title())
	bpy.ops.object.select_all(action='DESELECT')

	ob = data_to.objects[0]
	ob.data['gem'] = {'CUT': cut}

	ob.location = bpy.context.scene.cursor_location
	to_size(ob, size)
	type_set(ob, tpe, data_to.materials)
	sce_link(ob, active=True)


def cut_replace():
	context = bpy.context
	props = context.scene.jewelcraft
	cut = props.import_gem_cut

	for obj in context.selected_objects:
		if obj.data.get('gem'):
			data_to = asset_import(ob_name=cut.title())

			ob = data_to.objects[0]
			ob.data['gem'] = {'CUT': cut}

			append_to(ob, obj)
			to_size(ob, obj.dimensions[1])
			type_copy(ob, obj)

			bpy.context.scene.objects.unlink(obj)
			bpy.data.objects.remove(obj)
			sce_link(ob, active=True)


def type_replace():
	context = bpy.context
	tpe = context.scene.jewelcraft.import_gem_type

	data_to = asset_import(mat_name=tpe.replace('_', ' ').title())
	for ob in context.selected_objects:
		if ob.data.get('gem'):
			type_set(ob, tpe, data_to.materials)






def prongs_import():
	for obj in bpy.context.selected_objects:
		if obj.data.get('gem'):
			cut = obj.data['gem']['CUT']
			data_to = asset_import(ob_name=cut.title()+' Prongs', mat_name='Prongs')

			ob = data_to.objects[0]
			append_to(ob, obj)
			to_size(ob, obj.dimensions[1])
			material_assign(ob, 'Prongs', data_to.materials)
			sce_link(ob)


def single_prong_import():
	data_to = asset_import(ob_name='Single Prong', mat_name='Prongs')
	bpy.ops.object.select_all(action='DESELECT')

	ob = data_to.objects[0]
	ob.location = bpy.context.scene.cursor_location
	material_assign(ob, 'Prongs', data_to.materials)
	sce_link(ob, active=True)


def cutter_import(seat_only=False):
	suffix = ''
	if seat_only:
		suffix = ' (Seat only)'

	for obj in bpy.context.selected_objects:
		if obj.data.get('gem'):
			cut = obj.data['gem']['CUT']
			data_to = asset_import(ob_name=cut.title()+' Cutter'+suffix, mat_name='Cutter')

			ob = data_to.objects[0]
			append_to(ob, obj)
			to_dimensions(ob, obj)
			material_assign(ob, 'Cutter', data_to.materials)
			sce_link(ob)


def imitation_import():
	data_to = asset_import(ob_name='Imitation (3 prong)', mat_name='Prongs')
	bpy.ops.object.select_all(action='DESELECT')

	ob = data_to.objects[0]
	ob.location = bpy.context.scene.cursor_location
	material_assign(ob, 'Prongs', data_to.materials)
	sce_link(ob, active=True)


def make_dupliface():
	context = bpy.context
	data = bpy.data

	gem = False
	obs = []
	obs_app = obs.append
	for ob in context.selected_objects:
		if (ob.data and ob.data.get('gem')):
			gem = ob
			obs_app(ob)
		else:
			obs_app(ob)

	if gem:
		ob = gem
		name = ob.name+' '
	else:
		ob = obs[0]
		name = ''


	verts = [(-0.15,0.15,0), (0.15,0.15,0), (0.15,-0.15,0), (-0.15,-0.15,0)]
	faces = [(3,2,1,0)]


	offset = (ob.dimensions[0]+1, 0, 0)
	for i in range(len(verts)):
		verts[i] = tuple(x+y for x,y in zip(verts[i], offset))


	me = data.meshes.new(name+'Duplifaces')
	me.from_pydata(verts, [], faces)
	me.update()

	df = data.objects.new(name+'Duplifaces', me)
	df.location = ob.location
	df.dupli_type = 'FACES'
	context.scene.objects.link(df)

	for ob in obs:
		ob.parent = df
		ob.location = [0,0,0]
		apply_transforms(ob)



def select_dupli():
	context = bpy.context
	sce = context.scene
	gems_loc = []
	gems_name = []

	bpy.ops.object.select_all(action='DESELECT')

	loc_app = gems_loc.append
	name_app = gems_name.append
	for ob in context.visible_objects:
		if (ob.type == 'MESH' and ob.data.get('gem')):
			loc_app(ob.location.freeze())
			name_app(ob.name)

	dupli = defaultdict(list)
	for i,item in enumerate(gems_loc):
		dupli[item].append(i)
	dupli = {k:v for k,v in dupli.items() if len(v)>1}

	if dupli:
		for i in dupli.items():
			for p in range(len(i[1])):
				if p != 0:
					sce.objects[gems_name[i[1][p]]].select = True
		return True






#############################################################################
# Utility ###################################################################
#############################################################################


def asset_import(ob_name=False, mat_name=False):
	data = bpy.data

	with data.libraries.load(var.asset_filepath) as (data_from, data_to):
		if ob_name:
			data_to.objects = [ob_name]
		if (mat_name and mat_name not in data.materials):
			data_to.materials.append(mat_name)

	return data_to


def type_set(ob, tpe, materials):
	ob.data['gem']['TYPE'] = tpe
	material_assign(ob, tpe.replace('_', ' ').title(), materials)


def type_copy(ob, obj):
	ob.data['gem']['TYPE'] = obj.data['gem']['TYPE']
	append = ob.data.materials.append
	for mat in obj.data.materials:
		append(mat)


def material_assign(ob, name, materials):
	material = False
	for mat in materials:
		if mat.name == name:
			material = mat
	if not material:
		material = bpy.data.materials[name]

	if bpy.context.scene.render.engine == 'BLENDER_RENDER':
		material.use_nodes = False

	if len(ob.material_slots) < 1:
		ob.data.materials.append(material)
	else:
		ob.material_slots[0].material = material


def append_to(ob, obj):
	if obj.parent:
		ob.location = [0,0,0]
		ob.parent = obj.parent
	else:
		ob.location = obj.location
	ob.rotation_euler = obj.rotation_euler


def sce_link(ob, active=False):
	sce = bpy.context.scene
	sce.objects.link(ob)
	if active:
		sce.objects.active = ob
	ob.select = True
	apply_transforms(ob)






#############################################################################
# Transform utility #########################################################
#############################################################################


def to_size(ob, size):
	ob.dimensions = ob.dimensions * size


def to_dimensions(ob, obj):
	size = obj.dimensions[1]
	if obj.dimensions[0] != obj.dimensions[1]:
		width = obj.dimensions[0]
	else:
		width = size

	ctr = 0.01 * size # Make cutter sligtly bigger than gem
	ob.dimensions = [width+ctr, size+ctr, ob.dimensions[2]*size+ctr]


def apply_transforms(ob):
	if ob.type == 'MESH':
		me = ob.data
		vec = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

		for i in range(3):
			mx = Matrix.Scale(ob.scale[i], 4, vec[i])
			for v in me.vertices:
				v.co = mx * v.co

		ob.scale = [1,1,1]
