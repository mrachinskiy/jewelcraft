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
		dens = units.convert(props.weighting_custom, 'cm->mm')
		report.data = '{} {}'.format(round(vol * dens, 2), l['g'])

	else:
		mdens = units.convert(var.metal_density[m], 'cm->mm')
		report.data = '{} {}'.format(round(vol * mdens, 2), l['g'])






def stats_get():
	sce = bpy.context.scene
	obs = sce.objects
	props = sce.jewelcraft
	stats = {}

	stats['METALS'] = []
	append = stats['METALS'].append
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

	if (props.export_size and obs.get(props.export_size)):
		stats['SIZE'] = units.system(obs[props.export_size].dimensions[0])

	if (props.export_shank and obs.get(props.export_shank)):
		stats['SHANK'] = stats_shank(obs[props.export_shank])

	if (props.export_dim and obs.get(props.export_dim)):
		stats['DIM'] = [units.system(obs[props.export_dim].dimensions[0]),
		                units.system(obs[props.export_dim].dimensions[1]),
		                units.system(obs[props.export_dim].dimensions[2])]

	if (props.export_weight and obs.get(props.export_weight)):
		stats['WEIGHT'] = units.system(volume.calculate(obs[props.export_weight]), volume=True)

	stats['GEMS'] = stats_gems()

	return stats






def template():
	stats = stats_get()
	l = export_locale()
	t = ''
	mm = l['mm']

	if 'SIZE' in stats:
		t += '{}\n    {} {}\n\n'.format(l['t_size'], round(stats['SIZE'], 2), mm)

	if 'SHANK' in stats:
		t += '{}\n    {:.1f} {}\n\n'.format(l['t_width'], stats['SHANK'][0], mm)
		t += '{}\n    {:.1f} {}\n\n'.format(l['t_thickness'], stats['SHANK'][1], mm)

	if 'DIM' in stats:
		dim = stats['DIM']
		t += '{}\n    {:.1f} × {:.1f} × {:.1f} {}\n\n'.format(l['t_dim'], dim[0], dim[1], dim[2], mm)

	if ('WEIGHT' in stats and stats['METALS']):
		t += l['t_weight'] + '\n    '
		for metal in stats['METALS']:
			t += format_weight(stats['WEIGHT'], metal, l) + '\n    '
		t += '\n'

	if stats['GEMS']:
		col_len = [len(l['type']), len(l['cut']), len(l['size']), len(l['qty'])]
		rows = []
		append = rows.append
		for tpe in sorted(stats['GEMS']):
			for cut in sorted(stats['GEMS'][tpe]):
				for size in sorted(stats['GEMS'][tpe][cut]):
					row = format_gems(tpe, cut, size, stats['GEMS'][tpe][cut][size], l)
					append(row)
					for i in range(len(col_len)):
						if len(row[i]) > col_len[i]:
							col_len[i] = len(row[i])

		table_columns = '{{:{}}} | {{:{}}} | {{:{}}} | {{}}\n    '.format(col_len[0], col_len[1], col_len[2])
		underline_len = col_len[0] + col_len[1] + col_len[2] + col_len[3] + 10

		t += l['t_settings'] + '\n    '
		t += table_columns.format(l['type'], l['cut'], l['size'], l['qty'])
		t += '—' * underline_len + '\n    '
		for gem in rows:
			t += table_columns.format(gem[0], gem[1], gem[2], gem[3])

	return t






def export():
	filepath = bpy.data.filepath

	if filepath:
		stats = template()
		filename = bpy.path.display_name_from_filepath(filepath)
		save_path = path.join(path.dirname(filepath), filename + '_stats.txt')

		f = open(save_path, 'w', encoding='utf-8')
		f.write(stats)
		f.close()
		return True

	else:
		prefs = bpy.context.user_preferences.addons[var.addon_id].preferences
		l = localization.locale[prefs.lang]
		utility.show_error_message(l['error_file'])
		return False






#############################################################################
# Stats utility #############################################################
#############################################################################


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
		stats = [units.system(ob.dimensions[1]),
		         units.system(ob.dimensions[2])]
		mo.show_viewport = save_state
	else:
		stats = [units.system(ob.dimensions[1]),
		         units.system(ob.dimensions[2])]

	return stats


def stats_gems():
	stats = {}

	for ob in bpy.context.scene.objects:

		if (ob.type == 'MESH' and ob.data.get('gem')):

			utility.ob_prop_style_convert(ob)
			tpe = ob.data['gem']['type']
			cut = ob.data['gem']['cut']

			if (ob.parent and ob.parent.dupli_type == 'FACES'):
				count = polycount(ob.parent)
			elif (ob.parent and ob.parent.dupli_type == 'NONE'):
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

			if (stats.get(tpe) and stats[tpe].get(cut) and stats[tpe][cut].get(size)):
				stats[tpe][cut][size] = stats[tpe][cut][size] + count
			elif (stats.get(tpe) and stats[tpe].get(cut)):
				stats[tpe][cut][size] = count
			elif stats.get(tpe):
				stats[tpe][cut] = {size : count}
			else:
				stats[tpe] = {cut : {size : count}}

	return stats


def polycount(obj):
	bm = volume.bmesh_copy_from_object(obj, triangulate=False, apply_modifiers=True)
	polycount = len(bm.faces)
	bm.free()
	return polycount






#############################################################################
# Template utility ##########################################################
#############################################################################


def export_locale():
	context = bpy.context
	prefs = context.user_preferences.addons[var.addon_id].preferences
	props = context.scene.jewelcraft

	if props.export_lang == 'AUTO':
		l = prefs.lang
	else:
		l = props.export_lang

	return localization.locale[l]


def format_weight(vol, metal, l):
	if metal == 'CUSTOM':
		props = bpy.context.scene.jewelcraft
		dens = units.convert(props.export_m_custom_dens, 'cm->mm')
		mat = props.export_m_custom_name
	else:
		dens = units.convert(var.metal_density[metal], 'cm->mm')
		mat = l[metal.lower()]

	return '{} {} ({})'.format(round(vol * dens, 2), l['g'], mat)


def format_gems(tpe, cut, size, qty, l):

	crt = ct_calc(tpe, cut, l=size[0], w=size[1], h=size[2])
	qty_ct = round(qty * crt, 3)

	if cut in ['ROUND', 'SQUARE', 'ASSCHER', 'OCTAGON', 'FLANDERS']:
		Size = '{} {} ({} {})'.format(size[0], l['mm'], crt, l['ct'])
	else:
		Size = '{} × {} {} ({} {})'.format(size[0], size[1], l['mm'], crt, l['ct'])

	Qty = '{} {} ({} {})'.format(qty, l['items'], qty_ct, l['ct'])
	Type = l[tpe.lower()]
	Cut = l[cut.lower()]

	return (Type, Cut, Size, Qty)


def ct_calc(tpe, cut, l=None, w=None, h=None):
	props = bpy.context.scene.jewelcraft
	dens = units.convert(var.stone_density[tpe], 'cm->mm')
	corr = var.gem_volume_correction[cut]

	if cut in ['ROUND', 'OCTAGON']:
		l = (l + w) / 2
		vol = pi * (l/2)**2 * (h/3) # Cone

	elif cut in ['OVAL', 'PEAR', 'MARQUISE', 'HEART']:
		vol = pi * (l/2) * (w/2) * (h/3) # Cone rectangular

	elif cut in ['SQUARE', 'ASSCHER', 'PRINCESS', 'CUSHION', 'RADIANT', 'FLANDERS']:
		vol = l*w*h / 3 # Pyramid

	elif cut in ['BAGUETTE', 'EMERALD']:
		vol = l*w * (h/2) # Prism

	elif cut in ['TRILLION', 'TRILLIANT', 'TRIANGLE']:
		vol = l*w*h / 6 # Tetrahedron

	g = (vol * corr) * dens
	ct = units.convert(g, 'g->ct')

	return round(ct, 3)
