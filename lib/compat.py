def gem_id_compat(ob):
	"""Compatibility for old files from v1.5, should be removed at some point"""

	if ob.type == 'MESH' and 'gem' in ob.data:

		if 'gem' not in ob:

			ob['gem'] = {}

			for k in ('TYPE', 'type'):
				if k in ob.data['gem']:
					ob['gem']['stone'] = ob.data['gem'][k]

			for k in ('CUT', 'cut'):
				if k in ob.data['gem']:
					ob['gem']['cut'] = ob.data['gem'][k]

		del ob.data['gem']
