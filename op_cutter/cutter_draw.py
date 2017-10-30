class UI_Draw:

	def draw(self, context):
		layout = self.layout

		layout.prop(self, 'auto_presets')

		layout.separator()

		split = layout.split()
		split.prop(self, 'handle', text='Handle')
		col = split.column(align=True)
		col.prop(self, 'handle_z_top', text='Top')

		if self.shape_rnd or self.shape_sq:
			col.prop(self, 'handle_l_size', text='Size')
		else:
			col.prop(self, 'handle_l_size', text='Length')
			col.prop(self, 'handle_w_size', text='Width')

		col.prop(self, 'handle_z_btm', text='Bottom')

		layout.separator()

		split = layout.split()
		split.label('Girdle')
		col = split.column(align=True)
		col.prop(self, 'girdle_z_top', text='Top')

		if not self.shape_tri:
			col.prop(self, 'girdle_l_ofst', text='Size Offset')
		else:
			col.prop(self, 'girdle_l_ofst', text='Length Offset')
			col.prop(self, 'girdle_w_ofst', text='Width Offset')

		col.prop(self, 'girdle_z_btm', text='Bottom')

		layout.separator()

		split = layout.split()
		split.prop(self, 'hole', text='Hole')
		col = split.column(align=True)
		col.prop(self, 'hole_z_top', text='Top/Culet')

		if self.shape_rnd or self.shape_sq:
			col.prop(self, 'hole_l_size', text='Size')
		else:
			col.prop(self, 'hole_l_size', text='Length')
			col.prop(self, 'hole_w_size', text='Width')

		col.prop(self, 'hole_z_btm', text='Bottom')

		if self.shape_fant and self.cut in {'PEAR', 'HEART'}:
			col.prop(self, 'hole_pos_ofst', text='Position Offset')

		if not self.shape_rnd:

			layout.separator()

			split = layout.split()
			split.prop(self, 'curve_seat', text='Curve Seat')
			col = split.column(align=True)
			col.prop(self, 'curve_seat_segments', text='Segments')
			col.prop(self, 'curve_seat_profile', text='Profile')

			if self.shape_tri:

				layout.separator()

				split = layout.split()
				split.prop(self, 'curve_profile', text='Curve Profile')
				col = split.column(align=True)
				col.prop(self, 'curve_profile_segments', text='Segments')
				col.prop(self, 'curve_profile_factor', text='Factor')

			elif self.cut == 'MARQUISE':

				layout.separator()

				split = layout.split()
				split.label('Profile')
				col = split.column(align=True)
				col.prop(self, 'mul_1', text='Factor 1')
				col.prop(self, 'mul_2', text='Factor 2')

			if not self.shape_fant:

				layout.separator()

				split = layout.split()
				split.prop(self, 'bevel_corners', text='Bevel Corners')
				col = split.column(align=True)

				if self.shape_rect:
					col.prop(self, 'bevel_corners_width', text='Width')
				else:
					col.prop(self, 'bevel_corners_percent', text='Width')

				col.prop(self, 'bevel_corners_segments', text='Segments')
				col.prop(self, 'bevel_corners_profile', text='Profile')

		if self.shape_rnd or self.cut in {'OVAL', 'MARQUISE'}:

			layout.separator()

			split = layout.split()
			split.label('Detalization')
			split.prop(self, 'detalization', text='')
