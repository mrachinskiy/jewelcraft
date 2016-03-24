import bpy


def show_error_message(message):

	def draw(self, context):
		self.layout.label(message)

	bpy.context.window_manager.popup_menu(draw, title="Error", icon="ERROR")


def ob_prop_style_convert(ob):
	# Forward compatibility function, should be removed somewhere in 2.x release

	if 'TYPE' in ob.data['gem']:
		ob.data['gem']['type'] = ob.data['gem']['TYPE']
		del ob.data['gem']['TYPE']

	if 'CUT' in ob.data['gem']:
		ob.data['gem']['cut'] = ob.data['gem']['CUT']
		del ob.data['gem']['CUT']
