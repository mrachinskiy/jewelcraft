import bpy


def show_error_message(message):

	def draw(self, context):
		self.layout.label(message)

	bpy.context.window_manager.popup_menu(draw, title="Error", icon="ERROR")


# Forward compatibility function, should be removed somewhere in 2.x release
def ob_prop_style_convert(ob):
	if ob.data['gem'].get('TYPE'):
		ob.data['gem']['type'] = ob.data['gem']['TYPE']
		del ob.data['gem']['TYPE']
	if ob.data['gem'].get('CUT'):
		ob.data['gem']['cut'] = ob.data['gem']['CUT']
		del ob.data['gem']['CUT']
