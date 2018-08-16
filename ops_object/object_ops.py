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


from math import pi

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty, EnumProperty
from mathutils import Matrix, Vector

from ..lib import asset


tau = pi * 2


class OBJECT_OT_jewelcraft_mirror(Operator):
    bl_label = "JewelCraft Mirror"
    bl_description = "Mirror selected objects around one or more axes, keeping object data linked"
    bl_idname = "object.jewelcraft_mirror"
    bl_options = {"REGISTER", "UNDO"}

    x = BoolProperty(name="X", default=True, options={"SKIP_SAVE"})
    y = BoolProperty(name="Y", options={"SKIP_SAVE"})
    z = BoolProperty(name="Z", options={"SKIP_SAVE"})

    rot_z = FloatProperty(name="Z", step=10, soft_min=-tau, soft_max=tau, unit="ROTATION", options={"SKIP_SAVE"})

    use_cursor = BoolProperty(name="Use 3D Cursor")

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.label("Mirror Axis")
        col = split.column(align=True)
        col.prop(self, "x")
        col.prop(self, "y")
        col.prop(self, "z")

        layout.separator()

        split = layout.split()
        split.label("Pivot Point")
        split.prop(self, "use_cursor")

        layout.separator()

        split = layout.split()
        split.label("Adjust Rotation")
        split.prop(self, "rot_z")

    def execute(self, context):
        scene = context.scene
        ofst = scene.cursor_location if self.use_cursor else (0.0, 0.0, 0.0)

        mat_z = Matrix.Rotation(self.rot_z, 4, "Z")

        mat_y_180 = Matrix.Rotation(pi, 4, "Y")
        mat_z_180 = Matrix.Rotation(pi, 4, "Z")

        for ob in context.selected_objects:

            ob_copy = ob.copy()
            scene.objects.link(ob_copy)
            ob_copy.layers = ob.layers

            ob.select = False
            ob_copy.parent = None

            if ob_copy.constraints:
                for con in ob_copy.constraints:
                    ob_copy.constraints.remove(con)

            ob_copy.matrix_world = ob.matrix_world

            # Mirror axes
            # ---------------------------

            if self.x:

                ob_copy.rotation_euler[1] = -ob_copy.rotation_euler[1]
                ob_copy.rotation_euler[2] = -ob_copy.rotation_euler[2]

                ob_copy.location[0] = ob_copy.location[0] - (ob_copy.location[0] - ofst[0]) * 2

            if self.y:

                ob_copy.rotation_euler[0] = -ob_copy.rotation_euler[0]
                ob_copy.rotation_euler[2] = -ob_copy.rotation_euler[2]

                ob_copy.location[1] = ob_copy.location[1] - (ob_copy.location[1] - ofst[1]) * 2

                ob_copy.matrix_basis *= mat_z_180

            if self.z:

                ob_copy.rotation_euler[0] = -ob_copy.rotation_euler[0]
                ob_copy.rotation_euler[1] = -ob_copy.rotation_euler[1]

                ob_copy.location[2] = ob_copy.location[2] - (ob_copy.location[2] - ofst[2]) * 2

                ob_copy.matrix_basis *= mat_y_180

            # Adjust orientation for mirrored objects
            # ---------------------------------------------

            if self.rot_z:
                ob_copy.matrix_basis *= mat_z

        scene.objects.active = ob_copy

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            return {"CANCELLED"}

        return self.execute(context)


class OBJECT_OT_jewelcraft_make_dupliface(Operator):
    bl_label = "JewelCraft Make Dupli-face"
    bl_description = "Create dupli-face for selected objects"
    bl_idname = "object.jewelcraft_make_dupliface"
    bl_options = {"REGISTER", "UNDO"}

    apply_scale = BoolProperty(name="Apply Scale", default=True)

    def execute(self, context):
        scene = context.scene
        obs = context.selected_objects
        ob = context.active_object or obs[0]

        df_name = ob.name + " Dupli-faces"
        df_radius = min(ob.dimensions[:2]) * 0.15
        df_offset = ob.dimensions[0] * 1.5

        verts = [
            (df_offset - df_radius, -df_radius, 0.0),
            (df_offset + df_radius, -df_radius, 0.0),
            (df_offset + df_radius, df_radius, 0.0),
            (df_offset - df_radius, df_radius, 0.0),
        ]
        faces = [(0, 1, 2, 3)]

        me = bpy.data.meshes.new(df_name)
        me.from_pydata(verts, [], faces)

        df = bpy.data.objects.new(df_name, me)
        df.location = ob.location
        df.dupli_type = "FACES"
        df.select = True

        scene.objects.link(df)
        scene.objects.active = df
        df.layers = ob.layers

        mat_inv = Matrix.Translation(df.location).inverted()

        for ob in obs:

            if self.apply_scale:
                asset.apply_scale(ob)

            ob.select = False
            ob.parent = df
            ob.matrix_parent_inverse = mat_inv

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            return {"CANCELLED"}

        return self.execute(context)


class OBJECT_OT_jewelcraft_lattice_project(Operator):
    bl_label = "JewelCraft Lattice Project"
    bl_description = "Project selected objects onto active object using Lattice"
    bl_idname = "object.jewelcraft_lattice_project"
    bl_options = {"REGISTER", "UNDO"}

    axis = EnumProperty(
        items=(
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
            ("-X", "-X", ""),
            ("-Y", "-Y", ""),
            ("-Z", "-Z", ""),
        ),
        default="-Z",
    )

    def draw(self, context):
        layout = self.layout

        layout.separator()

        split = layout.split()
        split.label("Axis")
        split.row().prop(self, "axis", expand=True)

        layout.separator()

    def execute(self, context):
        surf = context.active_object
        surf.select = False
        obs = context.selected_objects

        bpy.ops.object.add(radius=1, type="LATTICE")
        lat = context.active_object

        md = lat.modifiers.new("Shrinkwrap", "SHRINKWRAP")
        md.target = surf
        md.wrap_method = "PROJECT"
        md.use_project_z = True
        md.use_negative_direction = True

        bbox = []

        for ob in obs:
            ob.select = True
            bbox += [ob.matrix_world * Vector(x) for x in ob.bound_box]
            md = ob.modifiers.new("Lattice", "LATTICE")
            md.object = lat

        x_min = min(x[0] for x in bbox)
        x_max = max(x[0] for x in bbox)
        y_min = min(x[1] for x in bbox)
        y_max = max(x[1] for x in bbox)
        z_min = min(x[2] for x in bbox)
        z_max = max(x[2] for x in bbox)

        x_loc = (x_max + x_min) / 2
        y_loc = (y_max + y_min) / 2
        z_loc = (z_max + z_min) / 2

        x_dim = x_max - x_min
        y_dim = y_max - y_min
        z_dim = z_max - z_min

        if "X" in self.axis:
            ratio = z_dim / y_dim

            lat.scale[0] = z_dim
            lat.scale[1] = y_dim

            if "-" in self.axis:
                lat.rotation_euler[1] = pi / 2
                lat.location = (x_min, y_loc, z_loc)
            else:
                lat.rotation_euler[1] = -pi / 2
                lat.location = (x_max, y_loc, z_loc)

        elif "Y" in self.axis:
            ratio = x_dim / z_dim

            lat.scale[0] = x_dim
            lat.scale[1] = z_dim

            if "-" in self.axis:
                lat.rotation_euler[0] = -pi / 2
                lat.location = (x_loc, y_min, z_loc)
            else:
                lat.rotation_euler[0] = pi / 2
                lat.location = (x_loc, y_max, z_loc)

        else:
            ratio = x_dim / y_dim

            lat.scale[0] = x_dim
            lat.scale[1] = y_dim

            if "-" in self.axis:
                lat.location = (x_loc, y_loc, z_min)
            else:
                lat.rotation_euler[0] = -pi
                lat.location = (x_loc, y_loc, z_max)

        if ratio >= 1.0:
            pt_u = round(10 * ratio)
            pt_v = 10
        else:
            pt_u = 10
            pt_v = round(10 / ratio)

        lat.data.points_u = pt_u
        lat.data.points_v = pt_v
        lat.data.points_w = 1

        return {"FINISHED"}

    def invoke(self, context, event):
        if len(context.selected_objects) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        return self.execute(context)


class OBJECT_OT_jewelcraft_lattice_profile(Operator):
    bl_label = "JewelCraft Lattice Profile"
    bl_description = "Deform active object profile with Lattice"
    bl_idname = "object.jewelcraft_lattice_profile"
    bl_options = {"REGISTER", "UNDO"}

    axis = EnumProperty(
        items=(
            ("X", "X", ""),
            ("Y", "Y", ""),
        ),
        default="X",
    )
    lat_type = EnumProperty(
        items=(
            ("1D", "1D", "Use one-dimensional lattice for even deformation"),
            ("2D", "2D", "Use two-dimensional lattice for proportional deformation"),
        ),
        default="1D",
    )
    scale = FloatProperty(default=1.0, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.label("Axis")
        split.row().prop(self, "axis", expand=True)

        split = layout.split()
        split.label("Lattice")
        split.row().prop(self, "lat_type", expand=True)

        split = layout.split()
        split.label("Curvature Scale")
        split.prop(self, "scale", text="")

    def execute(self, context):
        ob = context.active_object
        obs = context.selected_objects
        obs.remove(ob)

        bbox = [ob.matrix_world * Vector(x) for x in ob.bound_box]

        x_min = min(x[0] for x in bbox)
        x_max = max(x[0] for x in bbox)
        y_min = min(x[1] for x in bbox)
        y_max = max(x[1] for x in bbox)
        z_min = min(x[2] for x in bbox)
        z_max = max(x[2] for x in bbox)

        x_loc = (x_max + x_min) / 2
        y_loc = (y_max + y_min) / 2
        z_loc = (z_max + z_min) / 2

        x_dim = x_max - x_min
        y_dim = y_max - y_min
        z_dim = z_max - z_min

        if self.axis == "X":
            rot_z = 0.0
            xy_dim = y_dim
        else:
            rot_z = pi / 2
            xy_dim = x_dim

        bpy.ops.object.add(radius=1, type="LATTICE", rotation=(0.0, 0.0, rot_z))
        lat = context.active_object

        md = ob.modifiers.new("Lattice", "LATTICE")
        md.object = lat

        if self.lat_type == "2D":

            lat.location = (x_loc, y_loc, z_loc)
            lat.scale = (1.0, xy_dim * 1.5, z_dim)

            lat.data.interpolation_type_w = "KEY_LINEAR"

            lat.data.points_u = 1
            lat.data.points_v = 7
            lat.data.points_w = 2

            pt_co_ids = (
                (0.42, (9, 11)),
                (0.16, (8, 12)),
                (-0.49, (7, 13)),
            )

            pivot = 0.5

        else:

            lat.location = (x_loc, y_loc, z_max)
            lat.scale[1] = xy_dim * 1.5

            lat.data.points_u = 1
            lat.data.points_v = 7
            lat.data.points_w = 1

            pt_co_ids = (
                (-0.075, (2, 4)),
                (-0.3, (1, 5)),
                (-0.75, (0, 6)),
            )

            pivot = 0.0

            # Vertex group
            # ---------------------------

            if ob.type == "MESH":

                v_gr = ob.vertex_groups.get("Lattice profile")

                if not v_gr:
                    v_gr = ob.vertex_groups.new("Lattice profile")

                v_ids = [v.index for v in ob.data.vertices if v.co[2] > 0.1]
                v_gr.add(v_ids, 1.0, "ADD")

                md.vertex_group = v_gr.name

        # Transform lattice points
        # ---------------------------

        for co, index in pt_co_ids:
            for i in index:
                lat.data.points[i].co_deform[2] = (co - pivot) * self.scale + pivot

        # Add modifier to selected objects
        # ---------------------------

        for ob in obs:
            md = ob.modifiers.new("Lattice", "LATTICE")
            md.object = lat

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.active_object:
            return {"CANCELLED"}

        return self.execute(context)


def update_size(self, context):
    self.size = context.active_object.dimensions[int(self.axis)]


class OBJECT_OT_jewelcraft_resize(Operator):
    bl_label = "JewelCraft Resize"
    bl_description = "Scale selected objects to given size"
    bl_idname = "object.jewelcraft_resize"
    bl_options = {"REGISTER", "UNDO"}

    axis = EnumProperty(
        items=(
            ("0", "X", ""),
            ("1", "Y", ""),
            ("2", "Z", ""),
        ),
        update=update_size,
    )
    size = FloatProperty(min=0.0, unit="LENGTH")

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.label("Axis")
        split.row().prop(self, "axis", expand=True)

        split = layout.split()
        split.label("Size")
        split.prop(self, "size", text="")

    def execute(self, context):
        context.space_data.pivot_point = "ACTIVE_ELEMENT"

        scale = self.size / self.dim_orig[int(self.axis)]
        bpy.ops.transform.resize(value=(scale, scale, scale))

        context.space_data.pivot_point = self.pivot_point_orig
        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.active_object:
            return {"CANCELLED"}

        wm = context.window_manager
        dim = context.active_object.dimensions

        self.dim_orig = dim.to_tuple()
        self.size = dim[int(self.axis)]
        self.pivot_point_orig = context.space_data.pivot_point

        return wm.invoke_props_dialog(self)
