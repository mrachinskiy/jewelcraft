import os

import bpy
from bpy.types import Operator
from bpy.app.translations import pgettext_tip as _

from .. import var
from .report_data_collect import data_collect
from .report_data_format import data_format


class WM_OT_JewelCraft_Product_Report(Operator):
	"""Save product report to text file"""
	bl_label = 'JewelCraft Product Report'
	bl_idname = 'wm.jewelcraft_product_report'

	def execute(self, context):
		prefs = context.user_preferences.addons[var.addon_id].preferences

		data_raw = data_collect()
		data_fmt = data_format(data_raw)

		# Compose text datablock
		# ---------------------------

		if data_raw['warn']:
			sep = '—' * 64
			warns = '{}\n{}\n'.format(_('WARNING'), sep)

			for msg in data_raw['warn']:
				warns += '-{}\n'.format(_(msg))

			warns += '{}\n\n'.format(sep)
			data_fmt = warns + data_fmt

		if 'JewelCraft Product Report' in bpy.data.texts:
			txt = bpy.data.texts['JewelCraft Product Report']
			txt.clear()
		else:
			txt = bpy.data.texts.new('JewelCraft Product Report')

		txt.write(data_fmt)
		txt.current_line_index = 0

		# Display report
		# ---------------------------

		if prefs.product_report_display:
			bpy.ops.screen.userpref_show('INVOKE_DEFAULT')

			area = bpy.context.window_manager.windows[-1].screen.areas[0]
			area.type = 'TEXT_EDITOR'

			space = area.spaces[0]
			space.text = txt

		# Write to file
		# ---------------------------

		if prefs.product_report_save:

			if bpy.data.is_saved:
				filepath = bpy.data.filepath
				filename = os.path.splitext(os.path.basename(filepath))[0]
				save_path = os.path.join(os.path.dirname(filepath), '{} {}'.format(filename, 'Report.txt'))

				with open(save_path, 'w', encoding='utf-8') as file:
					file.write(data_fmt)

				msg_header = _('Product Report')
				msg_saved = _('Text file successfully created in the project folder')

				if not prefs.product_report_display and data_raw['warn']:

					# Popup
					# ---------------------------

					def draw(self, context):
						for msg in data_raw['warn']:
							self.layout.label(_(msg), icon='ERROR')

						self.layout.label(msg_saved, icon='FILE_TICK')

					context.window_manager.popup_menu(draw, title=_('Report'))

					# Reports
					# ---------------------------

					for msg in data_raw['warn']:
						self.report({'WARNING'}, '{}: {}'.format(msg_header, _(msg)))

				self.report({'INFO'}, '{}: {}'.format(msg_header, msg_saved))

			else:
				self.report({'ERROR'}, '{}: {}'.format(msg_header, _('First save your blend file')))

		return {'FINISHED'}
