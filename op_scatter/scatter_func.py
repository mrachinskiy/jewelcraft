from mathutils import Matrix

from ..lib import mesh
from ..lib.asset import apply_scale, dist_helper


class Scatter:

	def execute(self, context):
		scene = context.scene
		start = self.start
		end = self.end

		# Init
		# ---------------------------

		if self.redistribute:

			obs = context.selected_objects
			num = len(obs) - 1
			ob = obs[0]
			curve = ob.constraints['Follow Path'].target

		else:

			num = self.number - 1
			curve = context.active_object
			curve.select = False
			ob = context.selected_objects[0]
			scene.objects.active = ob

		apply_scale(curve)
		scene.update()
		curve.data.use_radius = False
		cyclic = curve.data.splines[0].use_cyclic_u

		# Offset
		# ---------------------------

		if self.absolute_ofst:

			curve_length = mesh.edges_length(curve)
			ob_size = ob.dimensions[1]
			base_unit = 100.0 / curve_length

			ofst = base_unit * (ob_size + self.spacing)

		else:

			closed_scattering = True if round(end - start, 1) == 100.0 else False

			if cyclic and closed_scattering:
				ofst = (end - start) / (num + 1)

			else:
				if not cyclic:
					start = start if start >= 0.0 else 0.0
					end = end if end <= 100.0 else 100.0

				ofst = (end - start) / num

		# Scatter/Redistribute
		# ---------------------------

		if self.redistribute:

			obs_by_ofst = {}

			for ob in obs:
				obs_by_ofst[ob] = ob.constraints['Follow Path'].offset

			obs_by_ofst = sorted(obs_by_ofst, key=obs_by_ofst.get, reverse=True)
			ofst_fac = start

			for ob in obs_by_ofst:

				if self.rot_y:
					mat_rot = Matrix.Rotation(self.rot_y, 4, 'Y')
					ob.matrix_basis *= mat_rot

				if self.rot_z:
					mat_rot = Matrix.Rotation(self.rot_z, 4, 'Z')
					ob.matrix_basis *= mat_rot

				if self.loc_z:
					mat_loc = Matrix.Translation((0.0, 0.0, self.loc_z))
					ob.matrix_basis *= mat_loc

				ob.constraints['Follow Path'].offset = -ofst_fac
				ofst_fac += ofst

		else:

			ob.location = (0.0, 0.0, 0.0)
			ob.rotation_euler = (0.0, 0.0, 0.0)
			scene.update()

			if self.rot_y:
				mat_rot = Matrix.Rotation(self.rot_y, 4, 'Y')
				ob.matrix_world *= mat_rot

			if self.rot_z:
				mat_rot = Matrix.Rotation(self.rot_z, 4, 'Z')
				ob.matrix_world *= mat_rot

			if self.loc_z:
				mat_loc = Matrix.Translation((0.0, 0.0, self.loc_z))
				ob.matrix_world *= mat_loc

			ofst_fac = start + ofst

			for _ in range(num):
				new_ob = ob.copy()
				scene.objects.link(new_ob)
				con = new_ob.constraints.new('FOLLOW_PATH')
				con.target = curve
				con.offset = -ofst_fac
				con.use_curve_follow = True
				ofst_fac += ofst

			con = ob.constraints.new('FOLLOW_PATH')
			con.target = curve
			con.offset = -start
			con.use_curve_follow = True

		# Helper
		# ---------------------------

		if self.helper:
			dist_helper(ob, self.helper_size_ofst)

		return{'FINISHED'}
