from math import radians


def init_presets(self):

	# Defaults
	# ---------------------------

	self.detalization = 32
	self.number = 4
	self.diameter = 0.4
	self.intersection = 30.0
	self.position = radians(45.0)
	self.symmetry = False
	self.symmetry_pivot = 0.0
	self.bump_scale = 0.5
	self.z_top = 0.3
	self.z_btm = 0.5
	self.taper = 0.0
	self.alignment = 0.0

	# Sizes
	# ---------------------------

	if self.gem_l >= 2.5:
		self.diameter = 0.8
		self.z_top = 0.8
		self.z_btm = 1.2

	elif self.gem_l >= 1.7:
		self.diameter = 0.7
		self.z_top = 0.6
		self.z_btm = 0.9

	elif self.gem_l >= 1.5:
		self.diameter = 0.6
		self.z_top = 0.5
		self.z_btm = 0.7

	elif self.gem_l >= 1.2:
		self.diameter = 0.5
		self.z_top = 0.4
		self.z_btm = 0.6

	# Shapes
	# ---------------------------

	if self.shape_rnd:
		self.number = 2
		self.intersection = 30.0
		self.position = radians(-30.0)

		if self.cut == 'OVAL':
			self.intersection = 40.0
			self.position = radians(30.0)
			self.symmetry = True

	elif self.shape_tri:
		self.number = 3
		self.intersection = 0.0
		self.position = radians(60.0)
		self.alignment = radians(10.0)

	elif self.shape_sq:
		self.intersection = -20.0

		if self.cut == 'OCTAGON':
			self.intersection = 0.0

	elif self.shape_rect:
		self.number = 2
		self.intersection = -20.0
		self.position = radians(36.0)
		self.symmetry = True

		if self.cut == 'BAGUETTE':
			self.intersection = -10.0
			self.position = radians(29.0)

	elif self.shape_fant:
		self.number = 2
		self.intersection = 0.0
		self.position = radians(0.0)
		self.alignment = radians(10.0)

		if self.cut == 'HEART':
			self.number = 3
			self.intersection = -10.0
			self.position = radians(60.0)

		elif self.cut == 'PEAR':
			self.number = 1
			self.intersection = 40.0
			self.position = radians(50.0)
			self.symmetry = True
			self.symmetry_pivot = radians(-90.0)
