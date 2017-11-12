import os
import random
import sys
import subprocess

import bpy
from mathutils import Matrix

from . import mesh
from .. import var


def face_pos(ob):
	scene = bpy.context.scene
	obj = bpy.context.active_object

	# Update mesh
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT')

	mods_ignore = [(x, x.show_viewport) for x in obj.modifiers if x.type == 'SUBSURF']

	if mods_ignore:
		for mod in mods_ignore:
			mod[0].show_viewport = False
		scene.update()

	bm = mesh.to_bmesh(obj, triangulate=False)
	bm.normal_update()

	if mods_ignore:
		for mod in mods_ignore:
			mod[0].show_viewport = mod[1]

	faces = [x for x in bm.faces if x.select]

	if faces:

		if len(faces) > 1:
			for f in faces[:-1]:
				ob_copy = ob.copy()
				scene.objects.link(ob_copy)

				loc = Matrix.Translation(f.calc_center_median())
				quat = f.normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()

				ob_copy.matrix_world = loc * quat

		f = faces[-1]

		loc = Matrix.Translation(f.calc_center_median())
		quat = f.normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()

		ob.matrix_world = loc * quat

	bm.free()


def open_folder(path):
	if os.path.exists(path):
		if sys.platform == 'win32':
			os.startfile(path)
		elif sys.platform == 'darwin':
			subprocess.Popen(["open", path])
		else:
			subprocess.Popen(["xdg-open", path])


def init_gem(self):
	props = bpy.context.window_manager.jewelcraft

	self.stone = props.gem_stone
	self.cut = props.gem_cut
	self.color = gen_color(contrast=True)


def get_gem(self):
	obj = bpy.context.active_object

	self.gem_l = obj.dimensions[1]
	self.gem_w = obj.dimensions[0]
	self.gem_h = obj.dimensions[2]

	self.cut = obj['gem']['cut'] if 'gem' in obj else ''

	self.shape_rnd = self.shape_sq = self.shape_rect = self.shape_tri = self.shape_fant = False

	if self.cut == 'ROUND':
		self.shape_rnd = True
	elif self.cut in {'SQUARE', 'ASSCHER', 'PRINCESS', 'CUSHION', 'RADIANT', 'FLANDERS', 'OCTAGON'}:
		self.shape_sq = True
	elif self.cut in {'BAGUETTE', 'EMERALD'}:
		self.shape_rect = True
	elif self.cut in {'TRILLION', 'TRILLIANT', 'TRIANGLE'}:
		self.shape_tri = True
	elif self.cut in {'PEAR', 'MARQUISE', 'HEART', 'OVAL'}:
		self.shape_fant = True


def get_stone_name(stone):
	return stone.replace('_', ' ').title()


def get_cut_name(cut):
	return cut.title()


def set_stone_name(self):
	self.stone_name = self.stone.replace('_', ' ').title()


def set_cut_name(self):
	self.cut_name = self.cut.title()


def bm_to_scene(bm, name='New Object', color=None):
	me = bpy.data.meshes.new(name)
	bm.to_mesh(me)
	bm.free()

	scene = bpy.context.scene

	for obj in bpy.context.selected_objects:

		ob = bpy.data.objects.new(name, me)
		ob.show_all_edges = True
		ob.location = obj.location
		ob.rotation_euler = obj.rotation_euler

		ob.parent = obj
		ob.matrix_parent_inverse = obj.matrix_basis.inverted()

		add_material(ob, mat_name=name, color_rnd=color)

		scene.objects.link(ob)


def dist_helper(ob, ofst):
	size = max(ob.dimensions[:2]) + ofst * 2
	bm = mesh.make_circle(size)

	me = bpy.data.meshes.new('Helper')
	bm.to_mesh(me)
	bm.free()

	scene = bpy.context.scene

	for obj in bpy.context.selected_objects:

		ob = bpy.data.objects.new('Helper', me)
		ob.show_all_edges = True
		ob.location = obj.location
		ob.rotation_euler = obj.rotation_euler

		ob.parent = obj
		ob.matrix_parent_inverse = obj.matrix_basis.inverted()

		scene.objects.link(ob)

		ob['helper'] = True
		ob.hide_select = True
		ob.hide_render = True


def gen_color(contrast=False):
	if contrast:
		seq = (0.0, 0.5, 1.0)
		color = [random.choice(seq), random.choice(seq), random.choice(seq)]
	else:
		color = [random.random(), random.random(), random.random()]

	return color


def user_asset_library_folder():
	prefs = bpy.context.user_preferences.addons[var.addon_id].preferences

	if prefs.use_custom_asset_dir:
		return bpy.path.abspath(prefs.custom_asset_dir)

	return var.user_asset_dir


def asset_import(filepath='', ob_name=False, me_name=False):

	with bpy.data.libraries.load(filepath) as (data_from, data_to):
		if ob_name:
			data_to.objects = [ob_name]
		if me_name:
			data_to.meshes = [me_name]

	return data_to


def asset_import_batch(filepath=''):

	with bpy.data.libraries.load(filepath) as (data_from, data_to):
		data_to.objects = data_from.objects

	return data_to


def asset_export(folder='', filename=''):
	filepath = os.path.join(folder, filename)
	data_blocks = set(bpy.context.selected_objects)

	if not os.path.exists(folder):
		os.makedirs(folder)

	bpy.data.libraries.write(filepath, data_blocks, compress=True)


def render_preview(filepath=''):
	render = bpy.context.scene.render

	# Store settings
	# ---------------------------

	fpath = render.filepath
	x = render.resolution_x
	y = render.resolution_y
	res = render.resolution_percentage
	ext = render.image_settings.file_format
	alpha = render.alpha_mode
	color = render.image_settings.color_mode
	comp = render.image_settings.compression

	# Apply settings
	# ---------------------------

	render.filepath = filepath
	render.resolution_x = 256
	render.resolution_y = 256
	render.resolution_percentage = 100
	render.image_settings.file_format = 'PNG'
	render.alpha_mode = 'TRANSPARENT'
	render.image_settings.color_mode = 'RGBA'
	render.image_settings.compression = 100

	# Render and save
	# ---------------------------

	bpy.ops.render.opengl(write_still=True)

	# Revert settings
	# ---------------------------

	render.filepath = fpath
	render.resolution_x = x
	render.resolution_y = y
	render.resolution_percentage = res
	render.image_settings.file_format = ext
	render.alpha_mode = alpha
	render.image_settings.color_mode = color
	render.image_settings.compression = comp


def add_material_for_gem(self, ob):
	add_material(ob, mat_name=self.stone_name, mat_type=self.stone, is_gem=True, color_rnd=self.color)


def add_material(ob, mat_name='New Material', mat_type=None, is_gem=False, color_rnd=None):

	mat = bpy.data.materials.get(mat_name)
	mat_type = mat_type if mat_type else mat_name.upper()

	if not mat:

		mat = bpy.data.materials.new(mat_name)
		color = var.default_color.get(mat_type)

		if not color:
			color = color_rnd if color_rnd else gen_color()

		mat.diffuse_color = color
		if not is_gem:
			mat.specular_color = (0.0, 0.0, 0.0)

		if bpy.context.scene.render.engine == 'CYCLES':
			mat.use_nodes = True
			nodes = mat.node_tree.nodes

			for nd in nodes:
				nodes.remove(nd)

			if is_gem:
				node = nodes.new('ShaderNodeBsdfGlass')
			else:
				node = nodes.new('ShaderNodeBsdfGlossy')

			node.location = (0.0, 200.0)
			node.inputs['Color'].default_value = color + [1.0]

			node_out = nodes.new('ShaderNodeOutputMaterial')
			node_out.location = (200.0, 200.0)

			mat.node_tree.links.new(node.outputs['BSDF'], node_out.inputs['Surface'])

	if len(ob.material_slots) < 1:
		ob.data.materials.append(mat)
	else:
		ob.material_slots[0].material = mat


def apply_scale(ob):

	scale_mat = Matrix((
		(ob.scale[0], 0.0, 0.0, 0.0),
		(0.0, ob.scale[1], 0.0, 0.0),
		(0.0, 0.0, ob.scale[2], 0.0),
		(0.0, 0.0, 0.0, 1.0),
		))

	ob.data.transform(scale_mat)

	ob.scale = (1.0, 1.0, 1.0)
