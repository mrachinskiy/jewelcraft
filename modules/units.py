import bpy


def convert(value, units):

	if units == 'CM_MM':
		return value / 1000

	elif units == 'G_CT':
		return value * 5


def system(value, volume=False):

	us = bpy.context.scene.unit_settings.system

	if us == 'METRIC':

		scale = bpy.context.scene.unit_settings.scale_length

		if volume:
			return value * (1000 * 1000 * 1000) * (scale * scale * scale)
		else:
			return value * 1000 * scale

	return value
