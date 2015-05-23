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






def ShowErrorMessage(message, wrap=80):
	lines = []
	append = lines.append
	if wrap > 0:
		while len(message) > wrap:
			i = message.rfind(' ',0,wrap)
			if i == -1:
				append(message[:wrap])
				message = message[wrap:]
			else:
				append(message[:i])
				message = message[i+1:]
	if message:
		append(message)
	def draw(self, context):
		for line in lines:
			self.layout.label(line)
	bpy.context.window_manager.popup_menu(draw, title="Error Message", icon="ERROR")






class Utils():


	def make_dupliface(self):
		context = bpy.context
		data = bpy.data
		convert = Convert()

		gem = False
		name = ''
		obs = []
		append = obs.append
		for ob in context.selected_objects:
			if (ob.data and ob.data.get('gem')):
				gem = ob
				append(ob)
			else:
				append(ob)

		if gem:
			ob = gem
			name = ob.name+' '
		else:
			ob = obs[0]
		

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
			convert.apply_transforms(ob)


	def get_size(self, ob, index):
		v_co = []

		for v in ob.data.vertices:
			if v.groups:
				for vg in v.groups:
					if vg.group == index:
						v_co.append(v.co)

		if v_co:
			size = round(Vector(x*y for x,y in zip(v_co[0]-v_co[1], ob.scale)).length, 2)
		else:
			size = False

		return size


	def calc_ct(self, tpe, cut, d, d2=False, h=False):
		props = bpy.context.scene.jewelcraft
		dens = props.crystal_density[tpe]
		corr = props.gems_volume_correction[cut]

		if d2 == False:
			d2 = d

		if h == False:
			if d <= d2:
				h = d * 0.606
			else:
				h = d2 * 0.606

		if cut == 'ROUND':
			vol = (3.1415 * ((d/2)**2) * h/3) * corr

		elif (cut == 'OVAL' or cut == 'PEARL' or cut == 'MARQUISE'):
			vol = (3.1415 * (d/2) * (d2/2) * h/3) * corr

		elif (cut == 'SQUARE' or cut == 'BAGUETTE' or cut == 'EMERALD'):
			vol = ((d*d2*h) / 3) * corr

		weight = round(vol * dens, 4)

		return weight


	def polycount(self, obj):
		# Face count
		count = len(obj.data.polygons)
		# Face count if modifiers
		for mo in obj.modifiers:
			if mo.type == 'ARRAY':
				count = count * mo.count
			if mo.type == 'MIRROR':
				if mo.use_x == True:
					count = count * 2
				if mo.use_y == True:
					count = count * 2
				if mo.use_z == True:
					count = count * 2
		return count






class Check():


	def digit(self, value):
		return value.replace('.', '').replace(',', '').isdigit()


	def size(self, cut):
		size = bpy.context.scene.jewelcraft.import_gem_size
		
		if self.digit(size):
			size = Convert().to_float(size)
		else:
			size = False

		return size






class Convert():


	def to_float(self, value):
		return float(value.replace(',', '.'))


	def to_length(self, ob, obj):
		utils = Utils()

		for vg in obj.vertex_groups:
			if vg.name == 'Size 1':
				size = utils.get_size(obj, vg.index)

		size2 = size
		for vg in obj.vertex_groups:
			if vg.name == 'Size 2':
				size2 = utils.get_size(obj, vg.index)

		ob.dimensions = [ob.dimensions[0]*size, size2, ob.dimensions[2]*size]


	def to_width(self, ob, obj):
		for vg in obj.vertex_groups:
			if vg.name == 'Size 1':
				size = Utils().get_size(obj, vg.index)
		self.to_size(ob, size)


	def to_size(self, ob, size):
		if size <= 0:
			size = 1
		ob.dimensions = ob.dimensions * size


	def apply_transforms(self, ob):
		if ob.type == 'MESH':
			me = ob.data
			vectors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]

			i = 0
			for vec in vectors:
				mx = Matrix.Scale(ob.scale[i], 4, vec)
				
				for vert in me.vertices:
					vert.co = mx * vert.co
				i+=1
			
			ob.scale = [1, 1, 1]






class Asset():


	def gem_import(self, data_to, cut, tpe, size):
		ob = data_to.objects[0]
		ob.data['gem'] = {}
		ob.location = bpy.context.scene.cursor_location
		Convert().to_size(ob, size)

		self.type_set(ob, tpe, data_to.materials)
		self.gem_sce_link(ob, cut)


	def gem_replace(self, data_to, cut, tpe, obj):
		ob = data_to.objects[0]
		ob.data['gem'] = {}
		if obj.parent:
			ob.location = [0,0,0]
			ob.parent = obj.parent
		else:
			ob.location = obj.location
		ob.rotation_euler = obj.rotation_euler

		Convert().to_width(ob, obj)
		self.type_copy(ob, obj)

		bpy.context.scene.objects.unlink(obj)
		bpy.data.objects.remove(obj)
		self.gem_sce_link(ob, cut)


	def gem_sce_link(self, ob, cut):
		sce = bpy.context.scene

		ob.data['gem']['CUT'] = cut
		sce.objects.link(ob)
		sce.objects.active = ob
		ob.select = True
		Convert().apply_transforms(ob)


	def type_set(self, ob, tpe, materials):
		ob.data['gem']['TYPE'] = tpe
		self.material_assign(ob, tpe.title(), materials)


	def type_copy(self, ob, obj):
		ob.data['gem']['TYPE'] = obj.data['gem']['TYPE']
		append = ob.data.materials.append
		for mat in obj.data.materials:
			append(mat)


	def material_assign(self, ob, name, materials):
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


	def prongs_import(self, data_to, size):
		for ob in data_to.objects:
			if 'Prongs' in ob.name:
				ob.location = bpy.context.scene.cursor_location
				ob.dimensions = ob.dimensions * size
				self.prongs_sce_link(ob, data_to)


	def prongs_append(self, data_to, obj):
		ob = data_to.objects[0]
		if obj.parent:
			ob.location = [0,0,0]
			ob.parent = obj.parent
		else:
			ob.location = obj.location
		ob.rotation_euler = obj.rotation_euler
		Convert().to_width(ob, obj)
		self.prongs_sce_link(ob, data_to)


	def prongs_sce_link(self, ob, data_to):
		self.material_assign(ob, 'Prongs', data_to.materials)
		bpy.context.scene.objects.link(ob)
		ob.select = True
		Convert().apply_transforms(ob)


	def cutter_import(self, data_to, size):
		for ob in data_to.objects:
			if 'Cutter' in ob.name:
				ob.location = bpy.context.scene.cursor_location
				ob.dimensions = ob.dimensions * size
				self.cutter_sce_link(ob, data_to)


	def cutter_append(self, data_to, obj):
		ob = data_to.objects[0]
		if obj.parent:
			ob.location = [0,0,0]
			ob.parent = obj.parent
		else:
			ob.location = obj.location
		ob.rotation_euler = obj.rotation_euler
		Convert().to_length(ob, obj)
		self.cutter_sce_link(ob, data_to)


	def cutter_sce_link(self, ob, data_to):
		self.material_assign(ob, 'Cutter', data_to.materials)
		bpy.context.scene.objects.link(ob)
		ob.select = True
		Convert().apply_transforms(ob)






class Import():
	filepath = path.join(path.dirname(__file__), 'assets', 'gems.blend')


	def gem(self):
		data = bpy.data
		props = bpy.context.scene.jewelcraft
		l = localization.locale[props.lang]
		tpe = props.import_gem_type
		cut = props.import_gem_cut
		size = Check().size(cut)
		prongs = props.import_prongs
		cutter = props.import_cutter
		asset = Asset()

		if not size:
			return ShowErrorMessage(l['error_digit'])

		with data.libraries.load(self.filepath) as (data_from, data_to):
			
			data_to.objects = [cut.title()]
			if prongs:
				data_to.objects.append(cut.title()+' Prongs')
			if cutter:
				data_to.objects.append(cut.title()+' Cutter')

			if tpe.title() not in data.materials:
				data_to.materials.append(tpe.title())
			if 'Prongs' not in data.materials:
				data_to.materials.append('Prongs')
			if 'Cutter' not in data.materials:
				data_to.materials.append('Cutter')

		bpy.ops.object.select_all(action='DESELECT')

		asset.gem_import(data_to, cut, tpe, size)
		if prongs:
			asset.prongs_import(data_to, size)
		if cutter:
			asset.cutter_import(data_to, size)


	def type(self):
		context = bpy.context
		data = bpy.data
		tpe = context.scene.jewelcraft.import_gem_type
		asset = Asset()

		with data.libraries.load(self.filepath) as (data_from, data_to):
			if tpe.title() not in data.materials:
				data_to.materials = [tpe.title()]

		for ob in context.selected_objects:
			if ob.data.get('gem'):
				asset.type_set(ob, tpe, data_to.materials)


	def cut(self):
		context = bpy.context
		data = bpy.data
		props = context.scene.jewelcraft
		tpe = props.import_gem_type
		cut = props.import_gem_cut
		asset = Asset()

		for ob in context.selected_objects:
			if ob.data.get('gem'):

				with data.libraries.load(self.filepath) as (data_from, data_to):
					data_to.objects = [cut.title()]

				asset.gem_replace(data_to, cut, tpe, ob)


	def prongs(self):
		data = bpy.data
		asset = Asset()

		for ob in bpy.context.selected_objects:
			if ob.data.get('gem'):
				cut = ob.data['gem']['CUT']

				with data.libraries.load(self.filepath) as (data_from, data_to):

					data_to.objects = [cut.title()+' Prongs']

					if 'Prongs' not in data.materials:
						data_to.materials.append('Prongs')

				asset.prongs_append(data_to, ob)


	def cutter(self):
		data = bpy.data
		asset = Asset()

		for ob in bpy.context.selected_objects:
			if ob.data.get('gem'):
				cut = ob.data['gem']['CUT']

				with data.libraries.load(self.filepath) as (data_from, data_to):

					data_to.objects = [cut.title()+' Cutter']

					if 'Cutter' not in data.materials:
						data_to.materials.append('Cutter')

				asset.cutter_append(data_to, ob)






class Stats():


	def get(self):
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
			stats['SHANK'] = self.shank(obs[props.export_shank])

		if (props.export_dim and obs.get(props.export_dim)):
			stats['DIM'] = [str(round(obs[props.export_dim].dimensions[0], 1)),
			                str(round(obs[props.export_dim].dimensions[1], 1)),
			                str(round(obs[props.export_dim].dimensions[2], 1))]

		if (props.export_weight and obs.get(props.export_weight)):
			stats['WEIGHT'] = volume.volume_calculate(obs[props.export_weight])

		stats['GEMS'] = self.gems()

		return stats


	def shank(self, ob):
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


	def gems(self):
		utils = Utils()
		stats = {}
		
		for ob in bpy.context.scene.objects:
			
			if (ob.type == 'MESH' and ob.data.get('gem') and ob.vertex_groups):

				tpe = ob.data['gem']['TYPE']
				cut = ob.data['gem']['CUT']


				if (ob.parent and ob.parent.dupli_type == 'FACES'):
					count = utils.polycount(ob.parent)
				elif (ob.parent and ob.parent.dupli_type == 'NONE'):
					count = 0
				else:
					count = 1


				size = []
				for vg in ob.vertex_groups:
					for vname in ['Size 1', 'Size 2']:
						if vg.name == vname:
							size.append(utils.get_size(ob, vg.index))


				if (size[0] != False or size[1] != False):
					if len(size) > 1:
						if size[0].is_integer():
							size[0] = int(size[0])
						if size[1].is_integer():
							size[1] = int(size[1])
						
						if size[0] <= size[1]:
							size1 = size[0]
							size2 = size[1]
						else:
							size1 = size[1]
							size2 = size[0]

						size = (size1, size2)

					else:
						if size[0].is_integer(): size[0] = int(size[0])
						size = size[0]


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






class Template():


	def make(self, stats):
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
				t += self.weight(stats['WEIGHT'], metal) + '\n    '
			t += '\n'

		if stats['GEMS']:
			col_len = [len(l['type']), len(l['cut']), len(l['size']), len(l['qty'])]
			rows = []
			append = rows.append
			for tpe in sorted(stats['GEMS']):
				for cut in sorted(stats['GEMS'][tpe]):
					for size in sorted(stats['GEMS'][tpe][cut]):
						row = self.gems(tpe, cut, size, stats['GEMS'][tpe][cut][size])
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


	def gems(self, tpe, cut, size, qty):
		props = bpy.context.scene.jewelcraft
		l = localization.locale[props.lang]
		dt = props.diamonds_table
		mm = l['mm']
		ct = l['ct']
		itms = l['items']


		if type(size) == tuple:
			crt = Utils().calc_ct(tpe, cut, size[0], size[1])

			Size = '{} × {} ({})'.format(str(size[0]), str(size[1])+mm, str(crt)+ct)

		else:
			if (tpe == 'DIAMOND' and cut == 'ROUND' and dt.get(size)):
				crt = dt[size]
			else:
				crt = Utils().calc_ct(tpe, cut, size)

			Size = '{} ({})'.format(str(size)+mm, str(crt)+ct)


		Qty = '{} {} ({})'.format(str(qty), itms, str(round(qty*crt,5))+ct)
		Type = l[tpe.lower()]
		Cut = l[cut.lower()]

		return (Type, Cut, Size, Qty)


	def weight(self, vol, metal):
		props = bpy.context.scene.jewelcraft
		l = localization.locale[props.lang]
		g = l['g']

		if metal == 'CUSTOM':
			if (props.metal_custom_density and Check().digit(props.metal_custom_density)):
				custom_density = Convert().to_float(props.metal_custom_density) / 1000

				result = str(round(vol * custom_density, 2)) + g + ' ('+props.metal_custom_name+')'
			else:
				result = 0

		else:
			dens = props.metal_density[metal]

			result = str(round(vol * dens, 2)) + g + ' ('+l[metal.lower()]+')'

		return result






class Export():


	def stats(self):
		filepath = bpy.data.filepath
		l = localization.locale[bpy.context.scene.jewelcraft.lang]
		
		if filepath:
			t = Template().make(Stats().get())

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
			return ShowErrorMessage(l['error_file'])
