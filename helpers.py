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




class Utils():


	def make_dupliface(self):
		D = bpy.data
		C = bpy.context
		convert = Convert()

		gem = False
		name = ''
		obs = []
		append = obs.append
		for ob in C.selected_objects:
			if ob.data.get('gem'):
				gem = ob
				append(ob)
			else:
				append(ob)

		if gem:
			ob = gem
			name = ob.name+' '
		else:
			ob = obs[0]
		

		verts = [(-0.15, 0.15, 0), (0.15, 0.15, 0), (0.15, -0.15, 0), (-0.15, -0.15, 0)]
		faces = [(3, 2, 1, 0)]

		me = D.meshes.new(name+'Duplifaces')
		me.from_pydata(verts, [], faces)
		me.update()
		
		df = D.objects.new(name+'Duplifaces', me)
		df.location = ob.location
		df.dupli_type = 'FACES'
		C.scene.objects.link(df)

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
			size = round(Vector(x * y for x, y in zip(v_co[0]-v_co[1], ob.scale)).length, 2)
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


	def to_size(self, size, ob, obj=False, tolength=False):
		utils = Utils()
		
		if obj:
			for vg in obj.vertex_groups:
				if vg.name == 'Size 1':
					size = utils.get_size(obj, vg.index)

		if not tolength:
			if size <= 0:
				size = 1
			ob.dimensions = ob.dimensions * size

		else:
			size2 = size
			for vg in obj.vertex_groups:
				if vg.name == 'Size 2':
					size2 = utils.get_size(obj, vg.index)
			ob.dimensions = [ob.dimensions[0] * size, size2, ob.dimensions[2] * size]

	def apply_transforms(self, ob):
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


	def __init__(self):
		self.D = bpy.data
		self.C = bpy.context
		self.sce = self.C.scene


	def gem(self, data_to, cut, tpe, size, obj=False):
		sce = self.sce
		ob = data_to.objects[0]
		convert = Convert()
		ob_type = 'GEM'
		
		ob.data['gem'] = {'CUT': cut}
		
		if not obj:
			ob.location = [0,0,0]
			convert.to_size(size, ob)
			self.material(ob_type, ob, data_to.materials, tpe)
		
		else:
			if obj.parent:
				ob.location = [0,0,0]
				ob.parent = obj.parent
			else:
				ob.location = obj.location

			convert.to_size(size, ob, obj)
			self.material(ob_type, ob, [obj.material_slots[0].material], tpe)

			sce.objects.unlink(obj)
			self.D.objects.remove(obj)
		
		sce.objects.link(ob)
		sce.objects.active = ob
		ob.select = True
		convert.apply_transforms(ob)


	def material(self, ob_type, ob, materials, tpe=False):
		D = self.D


		def get_material(name):
			material = False
			for mat in materials:
				if mat.name == name:
					material = mat
			if not material:
				material = D.materials[name]
			return material


		if ob_type == 'GEM':
			ob.data['gem']['TYPE'] = tpe
			material = get_material(tpe.title())

		elif ob_type == 'PRONGS':
			material = get_material('Prongs')

		elif ob_type == 'CUTTER':
			material = get_material('Cutter')


		if self.sce.render.engine == 'BLENDER_RENDER':
			material.use_nodes = False

		if len(ob.material_slots) < 1:
			ob.data.materials.append(material)
		else:
			ob.material_slots[0].material = material


	def prongs(self, data_to, size, obj=False):
		convert = Convert()
		ob_type = 'PRONGS'
		
		if not obj:
			for iob in data_to.objects:
				if 'Prongs' in iob.name:
					ob = iob
					ob.location = [0,0,0]
					ob.dimensions = ob.dimensions * size

		else:
			ob = data_to.objects[0]
			if obj.parent:
				ob.location = [0,0,0]
				ob.parent = obj.parent
			else:
				ob.location = obj.location
			convert.to_size(size, ob, obj)
		
		self.material(ob_type, ob, data_to.materials)
		self.sce.objects.link(ob)
		ob.select = True
		convert.apply_transforms(ob)


	def cutter(self, data_to, size, obj=False):
		convert = Convert()
		ob_type = 'CUTTER'
		
		if not obj:
			for iob in data_to.objects:
				if 'Cutter' in iob.name:
					ob = iob
					ob.location = [0,0,0]
					ob.dimensions = ob.dimensions * size

		else:
			ob = data_to.objects[0]
			if obj.parent:
				ob.location = [0,0,0]
				ob.parent = obj.parent
			else:
				ob.location = obj.location
			convert.to_size(size, ob, obj, True)

		self.material(ob_type, ob, data_to.materials)
		self.sce.objects.link(ob)
		ob.select = True
		convert.apply_transforms(ob)




class Import():


	def __init__(self):
		self.D = bpy.data
		self.C = bpy.context
		self.props = self.C.scene.jewelcraft
		self.l = localization.locale[self.props.lang]
		self.filepath = path.join(path.dirname(__file__), 'assets', 'gems.blend')


	def gem(self):
		D = self.D
		props = self.props
		tpe = props.import_gem_type
		cut = props.import_gem_cut
		size = Check().size(cut)
		prongs = props.import_prongs
		cutter = props.import_cutter
		asset = Asset()

		if not size:
			return ShowErrorMessage(self.l['error_digit'])

		with D.libraries.load(self.filepath) as (data_from, data_to):
			
			data_to.objects = [cut.title()]
			if prongs:
				data_to.objects.append(cut.title()+' Prongs')
			if cutter:
				data_to.objects.append(cut.title()+' Cutter')

			if tpe.title() not in D.materials:
				data_to.materials.append(tpe.title())
			if 'Prongs' not in D.materials:
				data_to.materials.append('Prongs')
			if 'Cutter' not in D.materials:
				data_to.materials.append('Cutter')

		bpy.ops.object.select_all(action='DESELECT')

		asset.gem(data_to, cut, tpe, size)
		if prongs:
			asset.prongs(data_to, size)
		if cutter:
			asset.cutter(data_to, size)
		


	def type(self):
		D = self.D
		props = self.props
		tpe = props.import_gem_type
		obs = self.C.selected_objects
		asset = Asset()
		ob_type = 'GEM'

		with D.libraries.load(self.filepath) as (data_from, data_to):
			if tpe.title() not in D.materials:
				data_to.materials = [tpe.title()]

		for ob in obs:
			if ob.data.get('gem'):
				asset.material(ob_type, ob, data_to.materials, tpe)


	def cut(self):
		D = self.D
		props = self.props
		tpe = props.import_gem_type
		cut = props.import_gem_cut
		obs = self.C.selected_objects
		asset = Asset()
		size = None

		for ob in obs:
			if ob.data.get('gem'):

				with D.libraries.load(self.filepath) as (data_from, data_to):
					data_to.objects = [cut.title()]

				asset.gem(data_to, cut, tpe, size, ob)


	def prongs(self):
		D = self.D
		obs = self.C.selected_objects
		asset = Asset()
		size = None

		for ob in obs:
			if ob.data.get('gem'):
				cut = ob.data['gem']['CUT']

				with D.libraries.load(self.filepath) as (data_from, data_to):

					data_to.objects = [cut.title()+' Prongs']

					if 'Prongs' not in D.materials:
						data_to.materials.append('Prongs')

				asset.prongs(data_to, size, ob)


	def cutter(self):
		D = self.D
		obs = self.C.selected_objects
		asset = Asset()
		size = None

		for ob in obs:
			if ob.data.get('gem'):
				cut = ob.data['gem']['CUT']

				with D.libraries.load(self.filepath) as (data_from, data_to):

					data_to.objects = [cut.title()+' Cutter']

					if 'Cutter' not in D.materials:
						data_to.materials.append('Cutter')

				asset.cutter(data_to, size, ob)




class Stats():


	def __init__(self):
		self.C = bpy.context
		self.sce = self.C.scene


	def get(self):
		sce = self.sce
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
			self.sce.update()
			stats = [str(round(ob.dimensions[1], 1)),
			         str(round(ob.dimensions[2], 1))]
			mo.show_viewport = save_state
		else:
			stats = [str(round(ob.dimensions[1], 1)),
			         str(round(ob.dimensions[2], 1))]

		return stats


	def gems(self):
		sce = self.sce
		obs = sce.objects
		utils = Utils()
		stats = {}
		
		for ob in sce.objects:
			
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


	def __init__(self):
		self.C = bpy.context
		self.l = localization.locale[bpy.context.scene.jewelcraft.lang]


	def make(self, stats):
		l = self.l
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
			table_columns = '{:9} | {:8} | {:25} | {}\n    '
			
			t += l['t_settings'] + '\n    '
			t += table_columns.format(l['type'], l['cut'], l['size'], l['qty'])
			t += '—' * 70 + '\n    '
			for tpe in sorted(stats['GEMS']):
				for cut in sorted(stats['GEMS'][tpe]):
					for size in sorted(stats['GEMS'][tpe][cut]):
						t += self.gems(stats['GEMS'][tpe][cut][size], tpe, cut, size, table_columns)
		return t


	def weight(self, vol, metal):
		props = self.C.scene.jewelcraft
		l = self.l
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


	def gems(self, qty, tpe, cut, size, table_columns):
		dt = self.C.scene.jewelcraft.diamonds_table
		l = self.l
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

		return table_columns.format(Type, Cut, Size, Qty)




class Export():


	def __init__(self):
		self.C = bpy.context
		self.l = localization.locale[self.C.scene.jewelcraft.lang]

		self.export_stats()


	def export_stats(self):
		t = Template().make(Stats().get())

		self.save(t)


	def save(self, t):
		filepath = bpy.data.filepath
		
		if filepath:
			if filepath.rfind('\\') != -1:
				last_slash = filepath.rfind('\\')
			else:
				last_slash = filepath.rfind('/')
			
			save_path = path.join(filepath[:last_slash], 'stats.txt')
			
			f = open(save_path, 'w', encoding='utf-8')
			f.write(t)
			f.close()
		else:
			return ShowErrorMessage(self.l['error_file'])
