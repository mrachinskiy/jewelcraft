# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


from math import pi, tau

import bpy
from bpy.types import Operator
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    StringProperty,
)
from mathutils import Matrix


class OBJECT_OT_mirror(Operator):
    bl_label = "Mirror"
    bl_description = "Mirror selected objects around one or more axes, keeping object data linked"
    bl_idname = "object.jewelcraft_mirror"
    bl_options = {"REGISTER", "UNDO"}

    x: BoolProperty(name="X", options={"SKIP_SAVE"})
    y: BoolProperty(name="Y", options={"SKIP_SAVE"})
    z: BoolProperty(name="Z", options={"SKIP_SAVE"})
    use_cursor: BoolProperty(name="Use 3D Cursor")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        col = layout.column(heading="Mirror Axis", align=True)
        col.prop(self, "x")
        col.prop(self, "y")
        col.prop(self, "z")

        layout.separator()

        col = layout.column(heading="Pivot Point")
        col.prop(self, "use_cursor")

        layout.separator()

    def execute(self, context):
        from ..lib import asset

        axes = []
        if self.x: axes.append(0)
        if self.y: axes.append(1)
        if self.z: axes.append(2)

        if not axes:
            return {"FINISHED"}

        space_data = context.space_data
        use_local_view = bool(space_data.local_view)
        cursor_offset = context.scene.cursor.location * 2
        is_odd_axis_count = len(axes) != 2
        rotate_types = {"CAMERA", "LAMP", "SPEAKER", "FONT"}
        duplimap = {}
        children = {}

        for ob_orig in context.selected_objects:
            is_gem = "gem" in ob_orig
            use_rot = ob_orig.type in rotate_types or is_gem

            ob = ob_orig.copy()

            duplimap[ob_orig] = ob

            if ob.parent:
                children[ob] = ob.parent
                ob.parent = None

            if not is_gem and ob.data:
                ob.data = ob_orig.data.copy()

            for coll in ob_orig.users_collection:
                coll.objects.link(ob)

            if use_local_view:
                ob.local_view_set(space_data, True)

            if ob.constraints:
                for con in ob.constraints:
                    ob.constraints.remove(con)

            ob.select_set(True)
            ob_orig.select_set(False)
            ob.matrix_world = ob_orig.matrix_world

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

                    ob.matrix_world @= mat_rot_inv @ quat.to_matrix().to_4x4()
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

        context.view_layer.objects.active = ob

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


class OBJECT_OT_radial_instance(Operator):
    bl_label = "Radial Instance"
    bl_description = (
        "Create collection instances of selected objects in radial order.\n"
        "Use on existing collection instances to redo"
    )
    bl_idname = "object.jewelcraft_radial_instance"
    bl_options = {"REGISTER", "UNDO"}

    new_instance = True

    axis: EnumProperty(
        name="Axis",
        items=(
            ("0", "X", ""),
            ("1", "Y", ""),
            ("2", "Z", ""),
        ),
        default="2",
    )
    number: IntProperty(name="Number", default=1, min=1, options={"SKIP_SAVE"})
    angle: FloatProperty(name="Angle", default=tau, step=10, unit="ROTATION", options={"SKIP_SAVE"})
    use_cursor: BoolProperty(name="Use 3D Cursor")
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        col = layout.column()
        col.alert = not self.collection_name

        if self.new_instance:
            col.prop(self, "collection_name", text="Collection Name")
        else:
            col.prop_search(self, "collection_name", bpy.data, "collections")

        layout.prop(self, "number")
        layout.prop(self, "angle")
        layout.row().prop(self, "axis", expand=True)

        layout.separator()

        col = layout.column(heading="Pivot Point")
        col.prop(self, "use_cursor")

        layout.separator()

    def execute(self, context):
        if self.number == 1 or not self.collection_name:
            return {"FINISHED"}

        if self.new_instance:
            coll_rad = bpy.data.collections.new(self.collection_name)
            context.scene.collection.children.link(coll_rad)
            colls_inst = context.selected_objects[0].users_collection

            for ob in context.selected_objects:
                for coll in ob.users_collection:
                    coll.objects.unlink(ob)
                coll_rad.objects.link(ob)
                ob.select_set(False)
        else:
            coll_rad = bpy.data.collections[self.collection_name]
            colls_inst = None

            for ob in context.selected_objects:
                if ob.type == "EMPTY" and ob.instance_collection is not None:
                    if colls_inst is None:
                        colls_inst = ob.users_collection
                    bpy.data.objects.remove(ob)

        if self.use_cursor:
            coll_rad.instance_offset = context.scene.cursor.location

        dup_number = self.number - 1
        is_cyclic = round(self.angle, 2) == round(tau, 2)
        angle_offset = self.angle / (self.number if is_cyclic else dup_number)
        angle = angle_offset
        i = int(self.axis)

        for _ in range(dup_number):
            ob = bpy.data.objects.new(coll_rad.name, None)

            for coll in colls_inst:
                coll.objects.link(ob)

            ob.instance_type = "COLLECTION"
            ob.instance_collection = coll_rad
            ob.rotation_euler[i] = angle
            ob.select_set(True)

            ob.location = coll_rad.instance_offset

            angle += angle_offset

        context.view_layer.objects.active = ob

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            return {"CANCELLED"}

        obs = [
            ob for ob in context.selected_objects
            if ob.type == "EMPTY" and ob.instance_collection is not None
        ]

        if obs:
            self.new_instance = False
            self.use_cursor = False
            self.number = len(obs) + 1
            self.collection_name = obs[0].instance_collection.name

            if self.number > 2:
                ob1, ob2 = obs[:2]
                mat1 = ob1.matrix_local.to_quaternion().to_matrix()
                mat2 = ob2.matrix_local.to_quaternion().to_matrix()

                for i in range(3):
                    if mat1.col[i] == mat2.col[i]:
                        self.axis = str(i)
                        break
        else:
            self.collection_name = context.selected_objects[0].name

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_make_instance_face(Operator):
    bl_label = "Make Instance Face"
    bl_description = "Create instance face for selected objects"
    bl_idname = "object.jewelcraft_make_instance_face"
    bl_options = {"REGISTER", "UNDO"}

    apply_scale: BoolProperty(name="Apply Scale", default=True)

    def execute(self, context):
        from ..lib import asset

        space_data = context.space_data
        obs = context.selected_objects
        ob = context.object or obs[0]

        df_name = ob.name + " Instance Face"
        df_radius = min(ob.dimensions.xy) * 0.15
        df_offset = ob.dimensions.x * 1.5

        verts = [
            (df_offset - df_radius, -df_radius, 0.0),
            (df_offset + df_radius, -df_radius, 0.0),
            (df_offset + df_radius,  df_radius, 0.0),
            (df_offset - df_radius,  df_radius, 0.0),
        ]
        faces = [(0, 1, 2, 3)]

        me = bpy.data.meshes.new(df_name)
        me.from_pydata(verts, [], faces)

        df = bpy.data.objects.new(df_name, me)

        for coll in ob.users_collection:
            coll.objects.link(df)

        if space_data.local_view:
            df.local_view_set(space_data, True)

        df.location = ob.location
        df.instance_type = "FACES"
        df.select_set(True)

        context.view_layer.objects.active = df

        mat_inv = Matrix.Translation(df.location).inverted()

        for ob in obs:

            if self.apply_scale:
                asset.apply_scale(ob)

            ob.select_set(False)
            ob.parent = df
            ob.matrix_parent_inverse = mat_inv

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            return {"CANCELLED"}

        return self.execute(context)


def get_ratio(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 0.0


class OBJECT_OT_lattice_project(Operator):
    bl_label = "Lattice Project"
    bl_description = "Project selected objects onto active object using Lattice"
    bl_idname = "object.jewelcraft_lattice_project"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
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
        row = split.row()
        row.alignment = "RIGHT"
        row.label(text="Direction")

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

        surf = context.object
        surf.select_set(False)

        obs = context.selected_objects

        lat_data = bpy.data.lattices.new("Lattice Project")
        lat = bpy.data.objects.new("Lattice Project", lat_data)

        md = lat.modifiers.new("Shrinkwrap", "SHRINKWRAP")
        md.target = surf
        md.wrap_method = "PROJECT"
        md.use_project_z = True
        md.use_negative_direction = True

        colls = set()

        for ob in obs:
            md = ob.modifiers.new("Lattice", "LATTICE")
            md.object = lat
            colls.update(ob.users_collection)

        for coll in colls:
            coll.objects.link(lat)

        lat.select_set(True)
        context.view_layer.objects.active = lat

        if "X" in direction:
            ratio = get_ratio(self.BBox.dim.z, self.BBox.dim.y)
            sca_x = self.BBox.dim.z
            sca_y = self.BBox.dim.y

            if "NEG" in direction:
                lat.rotation_euler.y = pi / 2
                lat.location = (self.BBox.min.x, *self.BBox.loc.yz)
            else:
                lat.rotation_euler.y = -pi / 2
                lat.location = (self.BBox.max.x, *self.BBox.loc.yz)

        elif "Y" in direction:
            ratio = get_ratio(self.BBox.dim.x, self.BBox.dim.z)
            sca_x = self.BBox.dim.x
            sca_y = self.BBox.dim.z

            if "NEG" in direction:
                lat.rotation_euler.x = -pi / 2
                lat.location = (self.BBox.loc.x, self.BBox.min.y, self.BBox.loc.z)
            else:
                lat.rotation_euler.x = pi / 2
                lat.location = (self.BBox.loc.x, self.BBox.max.y, self.BBox.loc.z)

        else:
            ratio = get_ratio(self.BBox.dim.x, self.BBox.dim.y)
            sca_x = self.BBox.dim.x
            sca_y = self.BBox.dim.y

            if "NEG" in direction:
                lat.location = (*self.BBox.loc.xy, self.BBox.min.z)
            else:
                lat.rotation_euler.x = -pi
                lat.location = (*self.BBox.loc.xy, self.BBox.max.z)

        if not ratio:
            pt_u = 10 if sca_x else 1
            pt_v = 10 if sca_y else 1
        elif ratio >= 1.0:
            pt_u = round(10 * ratio)
            pt_v = 10
        else:
            pt_u = 10
            pt_v = round(10 / ratio)

        lat_data.points_u = pt_u
        lat_data.points_v = pt_v
        lat_data.points_w = 1

        lat.scale.x = sca_x or 1.0
        lat.scale.y = sca_y or 1.0

        return {"FINISHED"}

    def invoke(self, context, event):
        from ..lib import asset

        obs = context.selected_objects

        if len(obs) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        obs.remove(context.object)
        self.BBox = asset.GetBoundBox(obs)

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_lattice_profile(Operator):
    bl_label = "Lattice Profile"
    bl_description = (
        "Deform active object profile with Lattice, "
        "also works in Edit Mode with selected vertices"
    )
    bl_idname = "object.jewelcraft_lattice_profile"
    bl_options = {"REGISTER", "UNDO"}

    axis: EnumProperty(
        name="Axis",
        items=(
            ("X", "X", ""),
            ("Y", "Y", ""),
        ),
        default="X",
    )
    lat_type: EnumProperty(
        name="Lattice",
        items=(
            ("1D", "1D", "Use one-dimensional lattice for even deformation"),
            ("2D", "2D", "Use two-dimensional lattice for proportional deformation"),
        ),
        default="1D",
    )
    scale: FloatProperty(name="Curvature Scale", default=1.0, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.row().prop(self, "axis", expand=True)
        layout.row().prop(self, "lat_type", expand=True)
        layout.prop(self, "scale")

        layout.separator()

    def execute(self, context):
        ob = context.object
        obs = context.selected_objects
        is_editmesh = context.mode == "EDIT_MESH"

        if ob.select_get():
            obs.remove(ob)
        else:
            ob.select_set(True)

        if self.axis == "X":
            rot_z = 0.0
            dim_xy = self.BBox.dim.y or 1.0
        else:
            rot_z = pi / 2
            dim_xy = self.BBox.dim.x or 1.0

        if is_editmesh:
            bpy.ops.object.mode_set(mode="OBJECT")

        lat_data = bpy.data.lattices.new("Lattice Profile")
        lat = bpy.data.objects.new("Lattice Profile", lat_data)
        lat.rotation_euler.z = rot_z

        for coll in ob.users_collection:
            coll.objects.link(lat)

        lat.select_set(True)
        context.view_layer.objects.active = lat

        md = ob.modifiers.new("Lattice", "LATTICE")
        md.object = lat

        if self.lat_type == "2D":

            lat.location = self.BBox.loc
            lat.scale = (1.0, dim_xy * 1.5, self.BBox.dim.z)

            lat_data.interpolation_type_w = "KEY_LINEAR"

            lat_data.points_u = 1
            lat_data.points_v = 7
            lat_data.points_w = 2

            pt_co_ids = (
                (0.42, (9, 11)),
                (0.16, (8, 12)),
                (-0.49, (7, 13)),
            )

            pivot = 0.5

        else:

            lat.location = (*self.BBox.loc.xy, self.BBox.max.z)
            lat.scale[1] = dim_xy * 1.5

            lat_data.points_u = 1
            lat_data.points_v = 7
            lat_data.points_w = 1

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
                    v_gr = ob.vertex_groups.new(name="Lattice profile")

                if is_editmesh:
                    v_ids = [v.index for v in ob.data.vertices if v.select]
                else:
                    v_ids = [v.index for v in ob.data.vertices if v.co.z > 0.1]

                v_gr.add(v_ids, 1.0, "ADD")
                md.vertex_group = v_gr.name

        # Transform lattice points
        # ---------------------------

        for co, index in pt_co_ids:
            for i in index:
                lat_data.points[i].co_deform.z = (co - pivot) * self.scale + pivot

        # Add modifier to selected objects
        # ---------------------------

        for ob in obs:
            md = ob.modifiers.new("Lattice", "LATTICE")
            md.object = lat

        return {"FINISHED"}

    def invoke(self, context, event):
        from ..lib import asset

        ob = context.object

        if not ob:
            return {"CANCELLED"}

        self.BBox = asset.GetBoundBox((ob,))

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)


def upd_size(self, context):
    self.size = context.object.dimensions[int(self.axis)]


class OBJECT_OT_resize(Operator):
    bl_label = "Resize"
    bl_description = "Scale selected objects to given size"
    bl_idname = "object.jewelcraft_resize"
    bl_options = {"REGISTER", "UNDO"}

    axis: EnumProperty(
        name="Axis",
        items=(
            ("0", "X", ""),
            ("1", "Y", ""),
            ("2", "Z", ""),
        ),
        update=upd_size,
    )
    size: FloatProperty(name="Size", min=0.0, step=10, unit="LENGTH")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        col = layout.column()
        col.row().prop(self, "axis", expand=True)

        if self.dim_orig[int(self.axis)]:
            col.prop(self, "size")
        else:
            row = col.row()
            row.alignment = "RIGHT"
            row.alert = True
            row.label(text="Zero dimensions", icon="ERROR")

        layout.separator()

    def execute(self, context):
        size_orig = self.dim_orig[int(self.axis)]

        if not size_orig:
            return {"FINISHED"}

        scale = self.size / size_orig
        bpy.ops.transform.resize(value=(scale, scale, scale), center_override=self.pivot)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.object:
            return {"CANCELLED"}

        dim = context.object.dimensions

        self.dim_orig = dim.to_tuple()
        self.size = dim[int(self.axis)]
        self.pivot = context.object.matrix_world.translation.to_tuple()

        wm = context.window_manager
        return wm.invoke_props_dialog(self)
