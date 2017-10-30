import math

import bpy

from .. import var, dynamic_lists
from ..lib import unit
from ..lib.asset import get_stone_name, get_cut_name
from ..locale import getreporttext as _


def to_int(x):
	if x.is_integer():
		return int(x)
	return x


def ct_calc(stone, cut, l, w, h):
	dens = unit.convert(var.stone_density.get(stone), 'CM3_TO_MM3')
	corr = var.gem_volume_correction.get(cut)

	if not dens or not corr:
		return 0

	if cut in {'ROUND', 'OVAL', 'PEAR', 'MARQUISE', 'OCTAGON', 'HEART'}:
		vol = math.pi * (l / 2) * (w / 2) * (h / 3)  # Cone

	elif cut in {'SQUARE', 'ASSCHER', 'PRINCESS', 'CUSHION', 'RADIANT', 'FLANDERS'}:
		vol = l * w * h / 3  # Pyramid

	elif cut in {'BAGUETTE', 'EMERALD'}:
		vol = l * w * (h / 2)  # Prism

	elif cut in {'TRILLION', 'TRILLIANT', 'TRIANGLE'}:
		vol = l * w * h / 6  # Tetrahedron

	g = vol * corr * dens
	ct = unit.convert(g, 'G_TO_CT')

	return round(ct, 3)


def data_format(data):
	props = bpy.context.scene.jewelcraft
	report = ''

	if 'size' in data:
		report += '{}:\n    {} {}\n\n'.format(_('Size'), round(data['size'], 2), _('mm'))

	if 'shank' in data:
		shank = data['shank']
		report += '{}:\n    {} × {} {}\n\n'.format(_('Shank'), round(shank[0], 2), round(shank[1], 2), _('mm'))

	if 'dim' in data:
		dim = data['dim']
		report += '{}:\n    {} × {} × {} {}\n\n'.format(_('Dimensions'), round(dim[0], 2), round(dim[1], 2), round(dim[2], 2), _('mm'))

	if 'weight' in data:
		report += '{}:\n'.format(_('Weight'))
		vol = data['weight']
		alloy_list = dynamic_lists.alloys(None, bpy.context)

		for mat in data['weight_mats']:

			if mat == 'CUSTOM':
				dens = unit.convert(props.product_report_mat_custom_dens, 'CM3_TO_MM3')
				name = props.product_report_mat_custom_name
			else:
				dens = unit.convert(var.alloy_density[mat], 'CM3_TO_MM3')
				name = [x[1] for x in alloy_list if x[0] == mat][0]
				name = _(name)

			weight = round(vol * dens, 2)
			report += '    {} {} ({})\n'.format(weight, _('g'), name)

		report += '\n'

	if data['gems']:

		gems = data['gems']
		rows = []

		# Columns initial width
		col_width = [len(_('Gem')), len(_('Cut')), len(_('Size')), len(_('Qty'))]

		for stone in sorted(gems):
			for cut in sorted(gems[stone]):
				for size in sorted(gems[stone][cut]):

					# Values
					# ---------------------------
					ct = ct_calc(stone, cut, l=size[1], w=size[0], h=size[2])
					qty = gems[stone][cut][size]
					qty_ct = round(qty * ct, 3)

					# Format columns
					# ---------------------------
					col_stone = _(get_stone_name(stone))
					col_cut = _(get_cut_name(cut))

					if cut in {'ROUND', 'SQUARE', 'ASSCHER', 'OCTAGON', 'FLANDERS'}:
						col_size = '{} {} ({} {})'.format(to_int(size[1]), _('mm'), ct, _('ct.'))
					else:
						col_size = '{} × {} {} ({} {})'.format(to_int(size[1]), to_int(size[0]), _('mm'), ct, _('ct.'))

					col_qty = '{} {} ({} {})'.format(qty, _('items'), qty_ct, _('ct.'))

					# Format row
					# ---------------------------
					row = (col_stone, col_cut, col_size, col_qty)
					rows.append(row)

					# Columns width
					# ---------------------------
					for i, last_width in enumerate(col_width):

						new_width = len(row[i])

						if new_width > last_width:
							col_width[i] = new_width

		# Format table
		# ---------------------------

		report += '{}:\n'.format(_('Settings'))
		col = '    {{:{}}} | {{:{}}} | {{:{}}} | {{}}\n'.format(col_width[0], col_width[1], col_width[2])
		report += col.format(_('Gem'), _('Cut'), _('Size'), _('Qty'))
		report += '    {}\n'.format('—' * (sum(col_width) + 10))

		for row in rows:
			report += col.format(row[0], row[1], row[2], row[3])

	return report
