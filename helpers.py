# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2015 Mikhail Rachinskiy
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ##### END MIT LICENSE BLOCK #####

import bpy
from mathutils import (Vector, Matrix)
from os import path
from . import localization
from . import volume






# Utils_____________________________________________________________


def ShowErrorMessage(message, wrap=80):
	lines = []
	if wrap > 0:
		while len(message) > wrap:
			i = message.rfind(' ',0,wrap)
			if i == -1:
				lines.append(message[:wrap])
				message = message[wrap:]
			else:
				lines.append(message[:i])
				message = message[i+1:]
	if message:
		lines.append(message)
	def draw(self, context):
		for line in lines:
			self.layout.label(line)
	bpy.context.window_manager.popup_menu(draw, title="Error Message", icon="ERROR")


def asset_import(ob_name=False, mat_name=False):
	data = bpy.data
	filepath = path.join(path.dirname(__file__), 'assets', 'gems.blend')

	with data.libraries.load(filepath) as (data_from, data_to):
		if ob_name:
			data_to.objects = [ob_name]
		if (mat_name and mat_name not in data.materials):
			data_to.materials.append(mat_name)

	return data_to


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


def get_size(ob, index):
	v_co = []

	for v in ob.data.vertices:
		if v.groups:
			for vg in v.groups:
				if vg.group == index:
					v_co.append(v.co)

	if len(v_co) == 2:
		size = round(Vector(x*y for x,y in zip(v_co[0]-v_co[1], ob.scale)).length, 2)
	else:
		size = False

	return size


def polycount(obj):
	bm = volume.bmesh_copy_from_object(obj, triangulate=False, apply_modifiers=True)
	polycount = len(bm.faces)
	bm.free()
	return polycount


def ct_calc(tpe, cut, l, w, h):
	props = bpy.context.scene.jewelcraft
	dens = props.crystal_density[tpe]
	corr = props.gems_volume_correction[cut]
	pi = 3.141592

	if cut == 'ROUND':
		vol = (pi * ((l/2)**2) * h/3) * corr

	elif (cut == 'OVAL' or cut == 'PEARL' or cut == 'MARQUISE'):
		vol = (pi * (l/2) * (w/2) * h/3) * corr

	elif (cut == 'SQUARE' or cut == 'BAGUETTE' or cut == 'EMERALD'):
		vol = ((l*w*h) / 3) * corr

	ct = vol * dens

	return ct_round(ct)


def ct_round(ct):
	if ct < 0.004:
		rnd = 4

	elif ct < 0.1:
		rnd = 3

	else:
		rnd = 2

	return round(ct, rnd)






# Convert_____________________________________________________________


def to_size(ob, size):
	ob.dimensions = ob.dimensions * size


def to_gem_size(ob, obj):
	for vg in obj.vertex_groups:
		if vg.name == 'Length':
			size = get_size(obj, vg.index)
	to_size(ob, size)


def to_gem_dimensions(ob, obj):
	for vg in obj.vertex_groups:
		if vg.name == 'Length':
			size = get_size(obj, vg.index)

	width = size
	for vg in obj.vertex_groups:
		if vg.name == 'Width':
			width = get_size(obj, vg.index)

	ctr = 0.01 * size # Make cutter sligtly bigger than gemstone
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






# Gemstone_____________________________________________________________


def gem_import():
	props = bpy.context.scene.jewelcraft
	tpe = props.import_gem_type
	cut = props.import_gem_cut
	size = props.import_gem_size

	data_to = asset_import(ob_name=cut.title(), mat_name=tpe.title())
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
			to_gem_size(ob, obj)
			type_copy(ob, obj)

			bpy.context.scene.objects.unlink(obj)
			bpy.data.objects.remove(obj)
			sce_link(ob, active=True)


def type_replace():
	context = bpy.context
	tpe = context.scene.jewelcraft.import_gem_type

	data_to = asset_import(mat_name=tpe.title())
	for ob in context.selected_objects:
		if ob.data.get('gem'):
			type_set(ob, tpe, data_to.materials)


def type_set(ob, tpe, materials):
	ob.data['gem']['TYPE'] = tpe
	material_assign(ob, tpe.title(), materials)


def type_copy(ob, obj):
	ob.data['gem']['TYPE'] = obj.data['gem']['TYPE']
	append = ob.data.materials.append
	for mat in obj.data.materials:
		append(mat)






# Accessories_____________________________________________________________


def prongs_import():
	for obj in bpy.context.selected_objects:
		if obj.data.get('gem'):
			cut = obj.data['gem']['CUT']
			data_to = asset_import(ob_name=cut.title()+' Prongs', mat_name='Prongs')

			ob = data_to.objects[0]
			append_to(ob, obj)
			to_gem_size(ob, obj)
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
			to_gem_dimensions(ob, obj)
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






# Stats_____________________________________________________________


def stats():
	sce = bpy.context.scene
	obs = sce.objects
	props = sce.jewelcraft
	stats = {}

	stats['METALS'] = []
	append = stats['METALS'].append
	if props.metal_24kt        : append('24KT')
	if props.metal_22kt        : append('22KT')
	if props.metal_18kt_white  : append('18KT_WHITE')
	if props.metal_14kt_white  : append('14KT_WHITE')
	if props.metal_18kt_yellow : append('18KT_YELLOW')
	if props.metal_14kt_yellow : append('14KT_YELLOW')
	if props.metal_silver      : append('SILVER')
	if props.metal_palladium   : append('PALLADIUM')
	if props.metal_platinum    : append('PLATINUM')
	if props.metal_custom      : append('CUSTOM')

	if (props.export_size and obs.get(props.export_size)):
		stats['SIZE'] = str(round(obs[props.export_size].dimensions[0], 2))

	if (props.export_shank and obs.get(props.export_shank)):
		stats['SHANK'] = stats_shank(obs[props.export_shank])

	if (props.export_dim and obs.get(props.export_dim)):
		stats['DIM'] = [str(round(obs[props.export_dim].dimensions[0], 1)),
		                str(round(obs[props.export_dim].dimensions[1], 1)),
		                str(round(obs[props.export_dim].dimensions[2], 1))]

	if (props.export_weight and obs.get(props.export_weight)):
		stats['WEIGHT'] = volume.calculate(obs[props.export_weight])

	stats['GEMS'] = stats_gems()

	return stats


def stats_shank(ob):
	mos = []
	for mo in ob.modifiers:
		if mo.type == 'CURVE':
			mos.append(mo.name)

	if mos:
		mo = ob.modifiers[mos[-1]]
		save_state = mo.show_viewport
		mo.show_viewport = False
		bpy.context.scene.update()
		stats = [str(round(ob.dimensions[1], 1)),
		         str(round(ob.dimensions[2], 1))]
		mo.show_viewport = save_state
	else:
		stats = [str(round(ob.dimensions[1], 1)),
		         str(round(ob.dimensions[2], 1))]

	return stats


def stats_gems():
	stats = {}

	for ob in bpy.context.scene.objects:

		if (ob.type == 'MESH' and ob.data.get('gem') and ob.vertex_groups):

			tpe = ob.data['gem']['TYPE']
			cut = ob.data['gem']['CUT']

			if (ob.parent and ob.parent.dupli_type == 'FACES'):
				count = polycount(ob.parent)
			elif (ob.parent and ob.parent.dupli_type == 'NONE'):
				count = 0
			else:
				count = 1

			size = []
			for vg in ob.vertex_groups:
				for vname in ['Length', 'Width', 'Depth']:
					if vg.name == vname:
						size.append(get_size(ob, vg.index))

			if (size and len(size) == len([x for x in size if x != False])):

				if len(size) == 2:
					if size[0].is_integer():
						size[0] = int(size[0])
					if size[1].is_integer():
						size[1] = int(size[1])

					size = (size[0], size[1])

				else:
					if size[0].is_integer():
						size[0] = int(size[0])
					if size[1].is_integer():
						size[1] = int(size[1])
					if size[2].is_integer():
						size[2] = int(size[2])

					size = (size[0], size[1], size[2])


				if (stats.get(tpe) and stats[tpe].get(cut) and stats[tpe][cut].get(size)):
					stats[tpe][cut][size] = stats[tpe][cut][size] + count
				elif (stats.get(tpe) and stats[tpe].get(cut)):
					stats[tpe][cut][size] = count
				elif stats.get(tpe):
					stats[tpe][cut] = {size : count}
				else:
					stats[tpe] = {cut : {size : count}}

			else:
				pass

	return stats






# Template_____________________________________________________________


def template(stats):
	l = localization.locale[bpy.context.scene.jewelcraft.lang]
	t = ''
	mm = l['mm']


	if 'SIZE' in stats:
		t += '{}\n    {}\n\n'.format(l['t_size'], stats['SIZE']+mm)

	if 'SHANK' in stats:
		t += '{}\n    {}\n\n'.format(l['t_width'], stats['SHANK'][0]+mm)
		t += '{}\n    {}\n\n'.format(l['t_thickness'], stats['SHANK'][1]+mm)

	if 'DIM' in stats:
		dim = stats['DIM']
		t += '{}\n    {} × {} × {}\n\n'.format(l['t_dim'], dim[0], dim[1], dim[2]+mm)

	if ('WEIGHT' in stats and stats['METALS']):
		t += l['t_weight'] + '\n    '
		for metal in stats['METALS']:
			t += format_weight(stats['WEIGHT'], metal) + '\n    '
		t += '\n'

	if stats['GEMS']:
		col_len = [len(l['type']), len(l['cut']), len(l['size']), len(l['qty'])]
		rows = []
		append = rows.append
		for tpe in sorted(stats['GEMS']):
			for cut in sorted(stats['GEMS'][tpe]):
				for size in sorted(stats['GEMS'][tpe][cut]):
					row = format_gems(tpe, cut, size, stats['GEMS'][tpe][cut][size])
					append(row)
					for i in range(len(col_len)):
						if len(row[i]) > col_len[i]:
							col_len[i] = len(row[i])

		table_columns = '{:'+str(col_len[0])+'} | {:'+str(col_len[1])+'} | {:'+str(col_len[2])+'} | {}\n    '
		underline_len = col_len[0]+col_len[1]+col_len[2]+col_len[3]+10

		t += l['t_settings']+'\n    '
		t += table_columns.format(l['type'], l['cut'], l['size'], l['qty'])
		t += '—'*underline_len+'\n    '
		for gem in rows:
			t += table_columns.format(gem[0], gem[1], gem[2], gem[3])

	return t


def format_gems(tpe, cut, size, qty):
	props = bpy.context.scene.jewelcraft
	l = localization.locale[props.lang]
	dt = props.diamonds_table
	mm = l['mm']
	ct = l['ct']
	itms = l['items']


	if len(size) == 2:

		if (tpe == 'DIAMOND' and cut == 'ROUND' and dt.get(size[0])):
			crt = dt[size[0]]
		else:
			crt = ct_calc(tpe, cut, size[0], size[0], size[1])

		Size = '{} ({})'.format(str(size[0])+mm, str(crt)+ct)

	else:

		crt = ct_calc(tpe, cut, size[0], size[1], size[2])

		Size = '{} × {} ({})'.format(str(size[0]), str(size[1])+mm, str(crt)+ct)

	qty_ct = ct_round(qty*crt)


	Qty = '{} {} ({})'.format(str(qty), itms, str(qty_ct)+ct)
	Type = l[tpe.lower()]
	Cut = l[cut.lower()]

	return (Type, Cut, Size, Qty)


def format_weight(vol, metal):
	props = bpy.context.scene.jewelcraft
	l = localization.locale[props.lang]
	g = l['g']

	if metal == 'CUSTOM':
		dens = props.metal_custom_density / 1000 # cm → mm
		mat = props.metal_custom_name
	else:
		dens = props.metal_density[metal]
		mat = l[metal.lower()]

	return str(round(vol * dens, 2))+g+' ('+mat+')'






# Export_____________________________________________________________


def export_stats():
	filepath = bpy.data.filepath

	if filepath:
		t = template(stats())

		if filepath.rfind('\\') != -1:
			last_slash = filepath.rfind('\\')
		else:
			last_slash = filepath.rfind('/')

		filename = bpy.path.display_name_from_filepath(filepath)
		save_path = path.join(filepath[:last_slash], filename+'_stats.txt')

		f = open(save_path, 'w', encoding='utf-8')
		f.write(t)
		f.close()

	else:
		l = localization.locale[bpy.context.scene.jewelcraft.lang]
		return ShowErrorMessage(l['error_file'])
