class UI_Draw:

	def draw(self, context):
		layout = self.layout

		layout.prop(self, 'auto_presets')

		layout.separator()

		split = layout.split()
		split.label('Prong Number')
		split.prop(self, 'number', text='')

		layout.separator()

		split = layout.split()
		split.label('Dimensions')
		col = split.column(align=True)
		col.prop(self, 'z_top', text='Top')
		col.prop(self, 'diameter', text='Diameter')
		col.prop(self, 'z_btm', text='Bottom')

		layout.separator()

		split = layout.split()
		split.label('Position')
		col = split.column(align=True)
		col.prop(self, 'position', text='Position')
		col.prop(self, 'intersection', text='Intersection')
		col.prop(self, 'alignment', text='Alignment')

		layout.separator()

		split = layout.split()
		split.prop(self, 'symmetry', text='Symmetry')
		split.prop(self, 'symmetry_pivot', text='Pivot')

		layout.separator()

		split = layout.split()
		split.label('Deformations')
		col = split.column(align=True)
		col.prop(self, 'bump_scale', text='Bump Scale')
		col.prop(self, 'taper', text='Taper')

		layout.separator()

		split = layout.split()
		split.label('Detalization')
		split.prop(self, 'detalization', text='')
