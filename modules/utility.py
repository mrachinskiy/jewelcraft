import bpy


def show_error_message(message):

	def draw(self, context):
		self.layout.label(message)

	bpy.context.window_manager.popup_menu(draw, title='Error', icon='ERROR')


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
