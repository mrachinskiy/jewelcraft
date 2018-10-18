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
from mathutils import Matrix

from ..lib import asset


class OBJECT_OT_jewelcraft_mirror(Operator):
    bl_label = "JewelCraft Mirror"
    bl_description = "Mirror selected objects around one or more axes, keeping object data linked"
    bl_idname = "object.jewelcraft_mirror"
    bl_options = {"REGISTER", "UNDO"}

    x = BoolProperty(name="X", options={"SKIP_SAVE"})
    y = BoolProperty(name="Y", options={"SKIP_SAVE"})
    z = BoolProperty(name="Z", options={"SKIP_SAVE"})

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

    def execute(self, context):
        axes = []
        if self.x: axes.append(0)
        if self.y: axes.append(1)
        if self.z: axes.append(2)

        if not axes:
            return {"FINISHED"}

        scene = context.scene
        cursor_offset = scene.cursor_location * 2
        is_odd_axis_count = len(axes) != 2
        rotate_types = {"CAMERA", "LAMP", "SPEAKER", "FONT"}
        duplimap = {}
        children = {}

        for ob_orig in context.selected_objects:
            is_gem = "gem" in ob_orig
            use_rot = ob_orig.type in rotate_types or is_gem

            ob = ob_orig.copy()

            if not is_gem and ob.data:
                ob.data = ob_orig.data.copy()

            scene.objects.link(ob)

            ob.layers = ob_orig.layers
            ob.matrix_world = ob_orig.matrix_world
            ob_orig.select = False

            duplimap[ob_orig] = ob

            if ob.parent:
                children[ob] = ob.parent
                ob.parent = None

            if ob.constraints:
                for con in ob.constraints:
                    ob.constraints.remove(con)

            for i in axes:

                if use_rot:
                    quat = ob.matrix_world.to_quaternion()
                    mat_rot_inv = quat.to_matrix().to_4x4().inverted()
                    w, x, y, z = quat

                    if i == 0:
                        quat[:] = w, x, -y, -z
                    elif i == 1:
                        quat[:] = z, y, x, w
                    else:
                        quat[:] = y, -z, w, -x

                    ob.matrix_world *= mat_rot_inv * quat.to_matrix().to_4x4()
                else:
                    ob.matrix_world[i][0] *= -1
                    ob.matrix_world[i][1] *= -1
                    ob.matrix_world[i][2] *= -1

                ob.matrix_world[i][3] *= -1

                if self.use_cursor:
                    ob.matrix_world[i][3] += cursor_offset[i]

            if is_odd_axis_count and not use_rot and ob.type == "MESH":
                asset.apply_scale(ob)
                ob.data.flip_normals()

        scene.objects.active = ob

        # Handle relations
        # -------------------------

        for child, parent in children.items():
            parent = duplimap.get(parent)
            if parent:
                child.parent = parent
                child.matrix_parent_inverse = parent.matrix_world.inverted()

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            return {"CANCELLED"}

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


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
        scene.objects.link(df)

        df.location = ob.location
        df.dupli_type = "FACES"
        df.select = True
        df.layers = ob.layers

        scene.objects.active = df

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

    direction = EnumProperty(
        items=(
            ("NONE", "", ""),
            ("POS_X", "X", ""),
            ("POS_Y", "Y", ""),
            ("POS_Z", "Z", ""),
            ("NEG_X", "-X", ""),
            ("NEG_Y", "-Y", ""),
            ("NEG_Z", "-Z", ""),
        ),
        default="NONE",
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.label("Direction")

        col = split.column(align=True)
        row = col.row(align=True)
        row.prop_enum(self, "direction", "POS_X")
        row.prop_enum(self, "direction", "POS_Y")
        row.prop_enum(self, "direction", "POS_Z")
        row = col.row(align=True)
        row.prop_enum(self, "direction", "NEG_X")
        row.prop_enum(self, "direction", "NEG_Y")
        row.prop_enum(self, "direction", "NEG_Z")

    def execute(self, context):
        direction = self.direction.split("_")

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

        for ob in obs:
            ob.select = True
            md = ob.modifiers.new("Lattice", "LATTICE")
            md.object = lat

        if "X" in direction:
            ratio = self.dim[2] / self.dim[1]
            lat.scale[0] = self.dim[2]
            lat.scale[1] = self.dim[1]

            if "NEG" in direction:
                lat.rotation_euler[1] = pi / 2
                lat.location = (self.bbox_min[0], self.loc[1], self.loc[2])
            else:
                lat.rotation_euler[1] = -pi / 2
                lat.location = (self.bbox_max[0], self.loc[1], self.loc[2])

        elif "Y" in direction:
            ratio = self.dim[0] / self.dim[2]
            lat.scale[0] = self.dim[0]
            lat.scale[1] = self.dim[2]

            if "NEG" in direction:
                lat.rotation_euler[0] = -pi / 2
                lat.location = (self.loc[0], self.bbox_min[1], self.loc[2])
            else:
                lat.rotation_euler[0] = pi / 2
                lat.location = (self.loc[0], self.bbox_max[1], self.loc[2])

        else:
            ratio = self.dim[0] / self.dim[1]
            lat.scale[0] = self.dim[0]
            lat.scale[1] = self.dim[1]

            if "NEG" in direction:
                lat.location = (self.loc[0], self.loc[1], self.bbox_min[2])
            else:
                lat.rotation_euler[0] = -pi
                lat.location = (self.loc[0], self.loc[1], self.bbox_max[2])

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
        obs = context.selected_objects

        if len(obs) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        obs.remove(context.active_object)
        self.loc, self.dim, self.bbox_min, self.bbox_max = asset.calc_bbox(obs)

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


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

        if self.axis == "X":
            rot_z = 0.0
            dim_xy = self.dim[1]
        else:
            rot_z = pi / 2
            dim_xy = self.dim[0]

        bpy.ops.object.add(radius=1, type="LATTICE", rotation=(0.0, 0.0, rot_z))
        lat = context.active_object

        md = ob.modifiers.new("Lattice", "LATTICE")
        md.object = lat

        if self.lat_type == "2D":

            lat.location = self.loc
            lat.scale = (1.0, dim_xy * 1.5, self.dim[2])

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

            lat.location = (self.loc[0], self.loc[1], self.bbox_max[2])
            lat.scale[1] = dim_xy * 1.5

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
        ob = context.active_object

        if not ob:
            return {"CANCELLED"}

        self.loc, self.dim, self.bbox_min, self.bbox_max = asset.calc_bbox((ob,))

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
