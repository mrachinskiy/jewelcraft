import bpy


def convert(value, units):

	if units == 'cm->mm':
		return value / 1000

	elif units == 'g->ct':
		return value * 5


def system(value, volume=False):

	unit = bpy.context.scene.unit_settings

	if unit.system == 'METRIC':

		scale = unit.scale_length

		if volume:
			return value * 1000**3 * scale**3
		else:
			return value * 1000 * scale

	return value
