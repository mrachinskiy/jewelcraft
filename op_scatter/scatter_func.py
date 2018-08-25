# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


from mathutils import Matrix

from ..lib import mesh, asset


class Scatter:

    def execute(self, context):
        scene = context.scene
        start = self.start
        end = self.end

        # Init
        # ---------------------------

        if self.is_scatter:

            num = self.number - 1
            curve = context.active_object
            curve.select = False
            ob = context.selected_objects[0]
            scene.objects.active = ob

        else:

            obs = context.selected_objects
            num = len(obs) - 1
            ob = obs[0]
            curve = ob.constraints["Follow Path"].target

        asset.apply_scale(curve)
        scene.update()
        curve.data.use_radius = False
        cyclic = curve.data.splines[0].use_cyclic_u

        # Offset
        # ---------------------------

        if self.absolute_ofst:

            curve_length = mesh.curve_length(curve)
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

        if self.is_scatter:

            ob.location = (0.0, 0.0, 0.0)
            ob.rotation_euler = (0.0, 0.0, 0.0)
            scene.update()

            if self.rot_y:
                mat_rot = Matrix.Rotation(self.rot_y, 4, "Y")
                ob.matrix_world *= mat_rot

            if self.rot_z:
                mat_rot = Matrix.Rotation(self.rot_z, 4, "Z")
                ob.matrix_world *= mat_rot

            if self.loc_z:
                mat_loc = Matrix.Translation((0.0, 0.0, self.loc_z))
                ob.matrix_world *= mat_loc

            ofst_fac = start + ofst

            for _ in range(num):
                ob_copy = ob.copy()
                scene.objects.link(ob_copy)
                ob_copy.layers = ob.layers
                con = ob_copy.constraints.new("FOLLOW_PATH")
                con.target = curve
                con.offset = -ofst_fac
                con.use_curve_follow = True
                ofst_fac += ofst

            con = ob.constraints.new("FOLLOW_PATH")
            con.target = curve
            con.offset = -start
            con.use_curve_follow = True

        else:

            obs_by_ofst = {}

            for ob in obs:
                con = ob.constraints.get("Follow Path")
                if con:
                    obs_by_ofst[ob] = con.offset

            obs_by_ofst = sorted(obs_by_ofst, key=obs_by_ofst.get, reverse=True)
            ofst_fac = start

            for ob in obs_by_ofst:

                if self.rot_y:
                    mat_rot = Matrix.Rotation(self.rot_y, 4, "Y")
                    ob.matrix_basis *= mat_rot

                if self.rot_z:
                    mat_rot = Matrix.Rotation(self.rot_z, 4, "Z")
                    ob.matrix_basis *= mat_rot

                if self.loc_z:
                    mat_loc = Matrix.Translation((0.0, 0.0, self.loc_z))
                    ob.matrix_basis *= mat_loc

                ob.constraints["Follow Path"].offset = -ofst_fac
                ofst_fac += ofst

        return {"FINISHED"}

    def invoke(self, context, event):
        if len(context.selected_objects) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        if self.is_scatter and context.active_object.type != "CURVE":
            self.report({"ERROR"}, "Active object must be a curve")
            return {"CANCELLED"}

        elif not self.is_scatter and "Follow Path" not in context.active_object.constraints:
            self.report({"ERROR"}, "Active object does not have a Follow Path constraint")
            return {"CANCELLED"}

        return self.execute(context)
