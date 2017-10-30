class UI_Draw:

	def draw(self, context):
		layout = self.layout

		if not self.redistribute:

			split = layout.split()
			split.label('Object Number')
			split.prop(self, 'number', text='')

			layout.separator()

		split = layout.split()
		split.label('Transforms')
		col = split.column(align=True)
		col.prop(self, 'rot_y')
		col.prop(self, 'rot_z')
		col.prop(self, 'loc_z')

		layout.separator()

		split = layout.split()
		split.label('Scatter (%)')
		col = split.column(align=True)
		col.prop(self, 'start')
		col.prop(self, 'end')

		layout.separator()

		split = layout.split()
		split.prop(self, 'absolute_ofst')
		col = split.column(align=True)
		col.prop(self, 'spacing')

		layout.separator()

		split = layout.split()
		split.prop(self, 'helper')
		split.prop(self, 'helper_size_ofst')
