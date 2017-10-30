import bpy


def convert(x, units):
	if units == 'CM3_TO_MM3':
		return x / 1000

	elif units == 'G_TO_CT':
		return x * 5


def to_metric(x, volume=False, batch=False):
	unit = bpy.context.scene.unit_settings
	scale = unit.scale_length

	if unit.system == 'METRIC' and scale != 0.001:

		if batch:
			return tuple([v * 1000 * scale for v in x])

		if volume:
			return x * 1000**3 * scale**3

		return x * 1000 * scale

	return x
