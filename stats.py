import bpy
import math
from . import (
	var,
	locale,
	units,
	volume,
	)


def collect():
	scene = bpy.context.scene
	props = scene.jewelcraft
	obs = scene.objects

	stats = {}

	if (props.stats_size and props.stats_size in obs):
		stats['size'] = units.system(max(obs[props.stats_size].dimensions))

	if (props.stats_shank and props.stats_shank in obs):

		ob = obs[props.stats_shank]
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

	if (props.stats_dim and props.stats_dim in obs):
		stats['dim'] = (units.system(obs[props.stats_dim].dimensions[0]),
		                units.system(obs[props.stats_dim].dimensions[1]),
		                units.system(obs[props.stats_dim].dimensions[2]))

	if (props.stats_weight and props.stats_weight in obs):
		stats['weight'] = units.system(volume.calculate(obs[props.stats_weight]), volume=True)

	stats['metals'] = []
	metals = ('24G', '22G', '18WG', '18YG', '14WG', '14YG', 'STER', 'PD', 'PL', 'CUSTOM')
	for m in metals:
		if getattr(props, 'stats_' + m.lower()):
			stats['metals'].append(m)

	to_int = lambda x: int(x) if x.is_integer() else x
	sg = {}
	for ob in obs:

		ob_id_compatibility(ob)

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

			size = (to_int(length), to_int(width), to_int(depth))

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


def fmt():
	props = bpy.context.scene.jewelcraft
	l = stats_locale()
	stats = collect()
	f = ''

	if 'size' in stats:
		f += '{}\n    {} {}\n\n'.format(l['st_size'], round(stats['size'], 2), l['mm'])

	if 'shank' in stats:
		shank = stats['shank']
		f += '{}\n    {:.1f} × {:.1f} {}\n\n'.format(l['st_shank'], shank[0], shank[1], l['mm'])

	if 'dim' in stats:
		dim = stats['dim']
		f += '{}\n    {:.1f} × {:.1f} × {:.1f} {}\n\n'.format(l['st_dim'], dim[0], dim[1], dim[2], l['mm'])

	if ('weight' in stats and stats['metals']):
		f += l['st_weight'] + '\n    '
		vol = stats['weight']
		for metal in stats['metals']:
			if metal == 'CUSTOM':
				dens = units.convert(props.stats_custom_dens, 'cm3->mm3')
				mat = props.stats_custom_name
			else:
				dens = units.convert(var.metal_density[metal], 'cm3->mm3')
				mat = l[metal.lower()]
			f += '{} {} ({})\n    '.format(round(vol * dens, 2), l['g'], mat)
		f += '\n'

	if stats['gems']:
		cols_width = [len(l['gem']), len(l['cut']), len(l['size']), len(l['qty'])]
		rows = []
		rows_app = rows.append
		sg = stats['gems']
		for stone in sorted(sg):
			for cut in sorted(sg[stone]):
				for size in sorted(sg[stone][cut]):

					crt = ct_calc(stone, cut, l=size[0], w=size[1], h=size[2])
					qty = sg[stone][cut][size]
					qty_ct = round(qty * crt, 3)

					fmtstone = l[stone.lower()]
					fmtcut = l[cut.lower()]
					if cut in ('ROUND', 'SQUARE', 'ASSCHER', 'OCTAGON', 'FLANDERS'):
						fmtsize = '{} {} ({} {})'.format(size[0], l['mm'], crt, l['ct'])
					else:
						fmtsize = '{} × {} {} ({} {})'.format(size[0], size[1], l['mm'], crt, l['ct'])
					fmtqty = '{} {} ({} {})'.format(qty, l['items'], qty_ct, l['ct'])

					row = (fmtstone, fmtcut, fmtsize, fmtqty)
					rows_app(row)

					for i in range(len(cols_width)):
						if len(row[i]) > cols_width[i]:
							cols_width[i] = len(row[i])

		col = '{{:{}}} | {{:{}}} | {{:{}}} | {{}}\n    '.format(cols_width[0], cols_width[1], cols_width[2])

		f += l['st_settings'] + '\n    '
		f += col.format(l['gem'], l['cut'], l['size'], l['qty'])
		f += '—' * (sum(cols_width) + 10) + '\n    '

		for gem in rows:
			f += col.format(gem[0], gem[1], gem[2], gem[3])

	return f


def stats_locale():
	prefs = bpy.context.user_preferences.addons[var.addon_id].preferences
	props = bpy.context.scene.jewelcraft

	if props.stats_lang == 'AUTO':
		lang = prefs.lang
	else:
		lang = props.stats_lang

	return locale.locale[lang]


def polycount(ob):
	bm = volume.bmesh_copy_from_object(ob, triangulate=False)
	polycount = len(bm.faces)
	bm.free()
	return polycount


def ct_calc(stone, cut, l, w, h):
	dens = units.convert(var.stone_density[stone], 'cm3->mm3')
	corr = var.gem_volume_correction[cut]

	if cut in ('ROUND', 'OVAL', 'PEAR', 'MARQUISE', 'OCTAGON', 'HEART'):
		vol = math.pi * (l/2) * (w/2) * (h/3) # Cone

	elif cut in ('SQUARE', 'ASSCHER', 'PRINCESS', 'CUSHION', 'RADIANT', 'FLANDERS'):
		vol = l*w*h / 3 # Pyramid

	elif cut in ('BAGUETTE', 'EMERALD'):
		vol = l*w * (h/2) # Prism

	elif cut in ('TRILLION', 'TRILLIANT', 'TRIANGLE'):
		vol = l*w*h / 6 # Tetrahedron

	g = (vol * corr) * dens
	ct = units.convert(g, 'g->ct')

	return round(ct, 3)


def ob_id_compatibility(ob):
	# Forward compatibility function, should be removed at some point

	if (ob.type == 'MESH' and 'gem' in ob.data):

		if 'gem' not in ob:
			ob['gem'] = {}

		if 'TYPE' in ob.data['gem']:
			ob['gem']['stone'] = ob.data['gem']['TYPE']
		if 'CUT' in ob.data['gem']:
			ob['gem']['cut'] = ob.data['gem']['CUT']

		if 'type' in ob.data['gem']:
			ob['gem']['stone'] = ob.data['gem']['type']
		if 'cut' in ob.data['gem']:
			ob['gem']['cut'] = ob.data['gem']['cut']

		del ob.data['gem']
