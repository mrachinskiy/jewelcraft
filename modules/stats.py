import bpy
from os import path
from math import pi
from .. import (
	var,
	localization,
)
from . import (
	units,
	volume,
	report,
	utility,
)


def weight_display():
	context = bpy.context
	prefs = context.user_preferences.addons[var.addon_id].preferences
	props = context.scene.jewelcraft
	l = localization.locale[prefs.lang]
	m = props.weighting_metals
	vol = units.system(volume.calculate(context.active_object), volume=True)

	if m == 'VOL':
		report.data = '{} {}'.format(round(vol, 4), l['mm3'])

	elif m == 'CUSTOM':
		dens = units.convert(props.weighting_custom, 'cm3->mm3')
		report.data = '{} {}'.format(round(vol * dens, 2), l['g'])

	else:
		mdens = units.convert(var.metal_density[m], 'cm3->mm3')
		report.data = '{} {}'.format(round(vol * mdens, 2), l['g'])


def stats_export_to_file():
	if bpy.data.is_saved:

		stats = stats_format()

		filepath = bpy.data.filepath
		filename = bpy.path.display_name_from_filepath(filepath)
		save_path = path.join(path.dirname(filepath), filename + '_stats.txt')

		with open(save_path, 'w', encoding='utf-8') as file:
			file.write(stats)

		return True






def stats_collect():
	scene = bpy.context.scene
	props = scene.jewelcraft
	obs = scene.objects

	stats = {}

	if (props.export_size and props.export_size in obs):
		stats['size'] = units.system(max(obs[props.export_size].dimensions))

	if (props.export_shank and props.export_shank in obs):

		ob = obs[props.export_shank]
		mods = []
		for mod in ob.modifiers:
			if mod.type == 'CURVE':
				mods.append(mod.name)

		if mods:
			mod = ob.modifiers[mods[-1]]
			save_state = mod.show_viewport
			mod.show_viewport = False
			scene.update()
			dim = list(ob.dimensions)
			dim.remove(max(dim))
			mod.show_viewport = save_state
		else:
			dim = list(ob.dimensions)
			dim.remove(max(dim))

		stats['shank'] = (units.system(dim[0]), units.system(dim[1]))

	if (props.export_dim and props.export_dim in obs):
		stats['dim'] = (
			units.system(obs[props.export_dim].dimensions[0]),
			units.system(obs[props.export_dim].dimensions[1]),
			units.system(obs[props.export_dim].dimensions[2])
		)

	if (props.export_weight and props.export_weight in obs):
		stats['weight'] = units.system(volume.calculate(obs[props.export_weight]), volume=True)

	stats['metals'] = []
	append = stats['metals'].append
	if props.export_m_24g    : append('24G')
	if props.export_m_22g    : append('22G')
	if props.export_m_18wg   : append('18WG')
	if props.export_m_18yg   : append('18YG')
	if props.export_m_14wg   : append('14WG')
	if props.export_m_14yg   : append('14YG')
	if props.export_m_ster   : append('STER')
	if props.export_m_pd     : append('PD')
	if props.export_m_pl     : append('PL')
	if props.export_m_custom : append('CUSTOM')

	sg = {}
	for ob in obs:

		utility.ob_id_compatibility(ob)

		if 'gem' in ob:

			stone = ob['gem']['stone']
			cut = ob['gem']['cut']

			if (ob.parent and ob.parent.type == 'MESH'):
				if ob.parent.dupli_type == 'FACES':
					count = polycount(ob.parent)
				elif ob.parent.dupli_type == 'NONE':
					count = 0
			else:
				count = 1

			length = round(units.system(ob.dimensions[1]), 2)
			width  = round(units.system(ob.dimensions[0]), 2)
			depth  = round(units.system(ob.dimensions[2]), 2)
			if length.is_integer(): length = int(length)
			if width.is_integer():  width  = int(width)
			if depth.is_integer():  depth  = int(depth)
			size = (length, width, depth)

			if (stone in sg and cut in sg[stone] and size in sg[stone][cut]):
				sg[stone][cut][size] += count
			elif (stone in sg and cut in sg[stone]):
				sg[stone][cut][size] = count
			elif stone in sg:
				sg[stone][cut] = {size: count}
			else:
				sg[stone] = {cut: {size: count}}

	stats['gems'] = sg

	return stats


def stats_format():
	l = set_export_locale()
	stats = stats_collect()

	f = ''

	if 'size' in stats:
		f += '{}\n    {} {}\n\n'.format(l['f_size'], round(stats['size'], 2), l['mm'])

	if 'shank' in stats:
		shank = stats['shank']
		f += '{}\n    {:.1f} × {:.1f} {}\n\n'.format(l['f_shank'], shank[0], shank[1], l['mm'])

	if 'dim' in stats:
		dim = stats['dim']
		f += '{}\n    {:.1f} × {:.1f} × {:.1f} {}\n\n'.format(l['f_dim'], dim[0], dim[1], dim[2], l['mm'])

	if ('weight' in stats and stats['metals']):
		f += l['f_weight'] + '\n    '
		vol = stats['weight']
		for metal in stats['metals']:
			if metal == 'CUSTOM':
				dens = units.convert(props.export_m_custom_dens, 'cm3->mm3')
				mat = props.export_m_custom_name
			else:
				dens = units.convert(var.metal_density[metal], 'cm3->mm3')
				mat = l[metal.lower()]
			f += '{} {} ({})\n    '.format(round(vol * dens, 2), l['g'], mat)
		f += '\n'

	if stats['gems']:
		col_len = [len(l['gem']), len(l['cut']), len(l['size']), len(l['qty'])]
		rows = []
		append = rows.append
		sg = stats['gems']
		for stone in sorted(sg):
			for cut in sorted(sg[stone]):
				for size in sorted(sg[stone][cut]):

					crt = ct_calc(stone, cut, l=size[0], w=size[1], h=size[2])
					qty = sg[stone][cut][size]
					qty_ct = round(qty * crt, 3)
					fstone = l[stone.lower()]
					fcut = l[cut.lower()]

					if cut in ('ROUND', 'SQUARE', 'ASSCHER', 'OCTAGON', 'FLANDERS'):
						fsize = '{} {} ({} {})'.format(size[0], l['mm'], crt, l['ct'])
					else:
						fsize = '{} × {} {} ({} {})'.format(size[0], size[1], l['mm'], crt, l['ct'])

					fqty = '{} {} ({} {})'.format(qty, l['items'], qty_ct, l['ct'])

					row = (fstone, fcut, fsize, fqty)

					append(row)
					for i in range(len(col_len)):
						if len(row[i]) > col_len[i]:
							col_len[i] = len(row[i])

		col = '{{:{}}} | {{:{}}} | {{:{}}} | {{}}\n    '.format(col_len[0], col_len[1], col_len[2])

		f += l['f_settings'] + '\n    '
		f += col.format(l['gem'], l['cut'], l['size'], l['qty'])
		f += '—' * (sum(col_len) + 10) + '\n    '

		for gem in rows:
			f += col.format(gem[0], gem[1], gem[2], gem[3])

	return f






# Utility


def set_export_locale():
	props = bpy.context.scene.jewelcraft
	prefs = bpy.context.user_preferences.addons[var.addon_id].preferences

	if props.export_lang == 'AUTO':
		lang = prefs.lang
	else:
		lang = props.export_lang

	return localization.locale[lang]


def polycount(ob):
	bm = volume.bmesh_copy_from_object(ob, triangulate=False, apply_modifiers=True)
	polycount = len(bm.faces)
	bm.free()
	return polycount


def ct_calc(stone, cut, l, w, h):
	dens = units.convert(var.stone_density[stone], 'cm3->mm3')
	corr = var.gem_volume_correction[cut]

	if cut in ('ROUND', 'OVAL', 'PEAR', 'MARQUISE', 'OCTAGON', 'HEART'):
		vol = pi * (l/2) * (w/2) * (h/3) # Cone

	elif cut in ('SQUARE', 'ASSCHER', 'PRINCESS', 'CUSHION', 'RADIANT', 'FLANDERS'):
		vol = l*w*h / 3 # Pyramid

	elif cut in ('BAGUETTE', 'EMERALD'):
		vol = l*w * (h/2) # Prism

	elif cut in ('TRILLION', 'TRILLIANT', 'TRIANGLE'):
		vol = l*w*h / 6 # Tetrahedron

	g = (vol * corr) * dens
	ct = units.convert(g, 'g->ct')

	return round(ct, 3)
