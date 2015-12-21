import bpy


def show_error_message(message, wrap=80):
	lines = []
	if wrap > 0:
		while len(message) > wrap:
			i = message.rfind(' ',0,wrap)
			if i == -1:
				lines.append(message[:wrap])
				message = message[wrap:]
			else:
				lines.append(message[:i])
				message = message[i+1:]
	if message:
		lines.append(message)
	def draw(self, context):
		for line in lines:
			self.layout.label(line)
	bpy.context.window_manager.popup_menu(draw, title="Error Message", icon="ERROR")
