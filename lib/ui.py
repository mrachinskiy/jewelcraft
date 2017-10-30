import bpy


def popup_report(self, info, title='', icon='NONE'):

	def draw(self, context):
		self.layout.label(info)

	bpy.context.window_manager.popup_menu(draw, title, icon)

	self.report({'INFO'}, '{}: {}'.format(title, info))
