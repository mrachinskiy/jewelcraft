# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from math import pi, tau

import bpy
from bpy.app.translations import pgettext_iface as _
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import Object, Operator
from mathutils import Matrix

from ..lib import unit


class OBJECT_OT_mirror(Operator):
    bl_label = "Mirror"
    bl_description = "Mirror selected objects around one or more axes, keeping object data linked"
    bl_idname = "object.jewelcraft_mirror"
    bl_options = {"REGISTER", "UNDO"}

    mirror_type: EnumProperty(
        name="Mirror Type",
        items=(
            ("INSTANCE", "Instance", ""),
            ("OBJECT", "Object", ""),
        ),
    )
    x: BoolProperty(name="X", options={"SKIP_SAVE"})
    y: BoolProperty(name="Y", options={"SKIP_SAVE"})
    z: BoolProperty(name="Z", options={"SKIP_SAVE"})
    use_coll_move: BoolProperty(name="Move to Collection", default=True, options={"SKIP_SAVE"})
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})
    pivot: EnumProperty(
        name="Pivot Point",
        items=(
            ("SCENE", "Scene", ""),
            ("OBJECT", "Object", ""),
        ),
    )
    keep_z: BoolProperty(
        name="Keep Z Direction",
        description="Makes transforms on Z axis consistent with original object (does not affect gems)",
        default=True,
    )
    use_cursor: BoolProperty(name="Use 3D Cursor")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.row().prop(self, "mirror_type", expand=True)

        layout.separator()

        if self.mirror_type == "INSTANCE":
            row = layout.row(heading="Move to Collection")
            row.prop(self, "use_coll_move", text="")
            sub = row.row()
            sub.enabled = self.use_coll_move
            sub.alert = self.use_coll_move and not self.collection_name
            sub.prop(self, "collection_name", text="")
        else:
            col = layout.column(heading="Orientation", align=True)
            col.prop(self, "keep_z")

        layout.separator()

        col = layout.column(heading="Mirror Axis", align=True)
        col.prop(self, "x")
        col.prop(self, "y")
        col.prop(self, "z")

        layout.separator()

        if self.mirror_type == "INSTANCE":
            layout.row().prop(self, "pivot", expand=True)
        else:
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

        if self.mirror_type == "INSTANCE":
            obs = context.selected_objects
            coll_name = self.collection_name if self.use_coll_move else None

            md, coll_obs = asset.gn_setup_coll("Mirror Instance", obs, coll_name)
            md["Input_2"] = coll_obs
            md["Input_3"] = self.x
            md["Input_4"] = self.y
            md["Input_5"] = self.z

            if self.pivot == "OBJECT":
                pivot = asset.pivot_add(coll_obs.name)
                md["Input_6"] = pivot
        else:
            context.view_layer.update()

            obs = []
            for ob in context.selected_objects:
                ob.select_set(False)
                obs.append((ob, False))

            for axis in axes:
                obs = self.object_mirror(obs, axis)

            for ob, flipped in obs:
                if flipped and ob.type == "MESH":
                    asset.apply_scale(ob)
                    ob.data.flip_normals()

        return {"FINISHED"}

    def invoke(self, context, event):
        obs = context.selected_objects

        if not obs:
            return {"CANCELLED"}

        for ob in obs:
            if "gem" in ob:
                break

        self.collection_name = ob.name

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)

    def object_mirror(self, obs: tuple[Object, bool], i: int) -> tuple[Object, bool]:
        context = bpy.context
        space_data = context.space_data
        use_local_view = bool(space_data.local_view)
        cursor_offset = context.scene.cursor.location * 2
        flip_z = Matrix.Rotation(pi, 4, "X")
        flip_z_inv = flip_z.inverted()
        rotate_types = {"CAMERA", "LAMP", "SPEAKER", "FONT"}
        duplimap = {}
        children = {}
        obs_mirrored = []

        for ob_orig, flipped in obs:
            is_gem = "gem" in ob_orig
            use_rot = is_gem or ob_orig.type in rotate_types

            # Duplicate
            ob = ob_orig.copy()
            obs_mirrored.append((ob, False if use_rot else not flipped))

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
            ob.matrix_world = ob_orig.matrix_world

            # Orientation
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

                if self.keep_z:
                    ob.matrix_world @= flip_z
                    ob.data.transform(flip_z_inv)

            # Translation
            ob.matrix_world[i][3] *= -1

            if self.use_cursor:
                ob.matrix_world[i][3] += cursor_offset[i]

        context.view_layer.objects.active = ob

        # Handle relations
        # -------------------------

        for child, parent in children.items():
            parent = duplimap.get(parent)
            if parent:
                child.parent = parent
                child.matrix_parent_inverse = parent.matrix_world.inverted()

        return obs + obs_mirrored


class OBJECT_OT_radial_instance(Operator):
    bl_label = "Radial Instance"
    bl_description = "Create collection instances of selected objects in radial order"
    bl_idname = "object.jewelcraft_radial_instance"
    bl_options = {"REGISTER", "UNDO"}

    use_coll_move: BoolProperty(name="Move to Collection", default=True, options={"SKIP_SAVE"})
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})
    count: IntProperty(name="Count", default=1, min=1, options={"SKIP_SAVE"})
    angle: FloatProperty(name="Angle", default=tau, step=10, unit="ROTATION", options={"SKIP_SAVE"})
    axis: EnumProperty(
        name="Axis",
        items=(
            ("0", "X", ""),
            ("1", "Y", ""),
            ("2", "Z", ""),
        ),
        default="2",
    )
    pivot: EnumProperty(
        name="Pivot Point",
        items=(
            ("SCENE", "Scene", ""),
            ("OBJECT", "Object", ""),
        ),
    )
    use_include_original: BoolProperty(name="Include Original", default=True)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        row = layout.row(heading="Move to Collection")
        row.prop(self, "use_coll_move", text="")
        sub = row.row()
        sub.enabled = self.use_coll_move
        sub.alert = self.use_coll_move and not self.collection_name
        sub.prop(self, "collection_name", text="")

        layout.separator()

        layout.prop(self, "count")
        layout.prop(self, "use_include_original")

        layout.separator()

        layout.prop(self, "angle")
        layout.row().prop(self, "axis", expand=True)

        layout.separator()

        layout.row().prop(self, "pivot", expand=True)

        layout.separator()

    def execute(self, context):
        if self.count == 1 or (self.use_coll_move and not self.collection_name):
            return {"FINISHED"}

        from ..lib import asset

        obs = context.selected_objects
        coll_name = self.collection_name if self.use_coll_move else None

        md, coll_obs = asset.gn_setup_coll("Radial Instance", obs, coll_name)
        md["Input_2"] = coll_obs
        md["Input_3"] = self.count
        md["Input_4"] = self.use_include_original
        md["Input_5"] = self.angle
        md["Socket_0"] = int(self.axis)

        if self.pivot == "OBJECT":
            pivot = asset.pivot_add(coll_obs.name)
            md["Input_9"] = pivot

        return {"FINISHED"}

    def invoke(self, context, event):
        obs = context.selected_objects

        if not obs:
            return {"CANCELLED"}

        for ob in obs:
            if "gem" in ob:
                break

        self.collection_name = ob.name

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_instance_face(Operator):
    bl_label = "Instance Face"
    bl_description = "Create instance face for selected objects"
    bl_idname = "object.jewelcraft_instance_face"
    bl_options = {"REGISTER", "UNDO"}

    use_coll_move: BoolProperty(name="Move to Collection", default=True, options={"SKIP_SAVE"})
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})
    pivot: EnumProperty(
        name="Pivot Point",
        items=(
            ("SCENE", "Scene", ""),
            ("OBJECT", "Object", ""),
        ),
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        row = layout.row(heading="Move to Collection")
        row.prop(self, "use_coll_move", text="")
        sub = row.row()
        sub.enabled = self.use_coll_move
        sub.alert = self.use_coll_move and not self.collection_name
        sub.prop(self, "collection_name", text="")

        layout.separator()

        layout.row().prop(self, "pivot", expand=True)

        layout.separator()

    def execute(self, context):
        from ..lib import asset

        obs = context.selected_objects
        coll_name = self.collection_name if self.use_coll_move else None

        for ob in obs:
            if "gem" in ob:
                break

        md, coll_obs = asset.gn_setup_coll("Instance Face", obs, coll_name)
        md["Input_2"] = coll_obs

        if self.pivot == "OBJECT":
            pivot = asset.pivot_add(coll_obs.name)
            pivot.empty_display_size = max(ob.dimensions.xy) * 0.75
            pivot.location = ob.location
            md["Input_3"] = pivot

        # Setup instance face object
        # -------------------------------

        r = min(ob.dimensions.xy) * 0.15
        verts = [
            (-r, -r, 0.0),
            ( r, -r, 0.0),
            ( r,  r, 0.0),
            (-r,  r, 0.0),
        ]
        faces = [(0, 1, 2, 3)]

        df = md.id_data
        df.data.from_pydata(verts, [], faces)
        df.location = ob.location
        df.location.x += ob.dimensions.x * 1.5

        return {"FINISHED"}

    def invoke(self, context, event):
        obs = context.selected_objects

        if not obs:
            return {"CANCELLED"}

        for ob in obs:
            if "gem" in ob:
                break

        self.collection_name = ob.name
        if ob.location.length_squared != 0.0:
            self.pivot = "OBJECT"

        wm = context.window_manager
        wm.invoke_props_popup(self, event)
        return self.execute(context)


def _ratio(a: float, b: float) -> float:
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
        direction, axis = self.direction.split("_")

        if axis == "X":
            lat.scale.xy = self.BBox.dimensions.zy
            lat.location.zy = self.BBox.location.zy
            if direction == "NEG":
                lat.location.x = self.BBox.min.x
                lat.rotation_euler.y = pi / 2
            else:
                lat.location.x = self.BBox.max.x
                lat.rotation_euler.y = -pi / 2
        elif axis == "Y":
            lat.scale.xy = self.BBox.dimensions.xz
            lat.location.xz = self.BBox.location.xz
            if direction == "NEG":
                lat.location.y = self.BBox.min.y
                lat.rotation_euler.x = -pi / 2
            else:
                lat.location.y = self.BBox.max.y
                lat.rotation_euler.x = pi / 2
        else:
            lat.scale.xy = self.BBox.dimensions.xy
            lat.location.xy = self.BBox.location.xy
            if direction == "NEG":
                lat.location.z = self.BBox.min.z
            else:
                lat.location.z = self.BBox.max.z
                lat.rotation_euler.x = -pi

        ratio = _ratio(*lat.scale.xy)
        lat_data.points_w = 1

        if ratio >= 1.0:
            lat_data.points_u = round(10 * ratio)
            lat_data.points_v = 10
        elif ratio < 1.0:
            lat_data.points_u = 10
            lat_data.points_v = round(10 / ratio)
        else:
            lat_data.points_u = 10 if lat.scale.x > 0.0 else 1
            lat_data.points_v = 10 if lat.scale.y > 0.0 else 1

        return {"FINISHED"}

    def invoke(self, context, event):
        from ..lib import asset

        obs = context.selected_objects

        if len(obs) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        obs.remove(context.object)
        self.BBox = asset.BoundBox(obs)

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
            dim_xy = self.BBox.dimensions.y or 1.0
        else:
            rot_z = pi / 2
            dim_xy = self.BBox.dimensions.x or 1.0

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

            lat.location = self.BBox.location
            lat.scale = (1.0, dim_xy * 1.5, self.BBox.dimensions.z)

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

            lat.location.xy = self.BBox.location.xy
            lat.location.z = self.BBox.max.z
            lat.scale.y = dim_xy * 1.5

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

        if not context.object:
            return {"CANCELLED"}

        self.BBox = asset.BoundBox((context.object,))

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


class CURVE_OT_length_display(Operator):
    bl_label = "Curve Length"
    bl_description = "Display curve length"
    bl_idname = "curve.jewelcraft_length_display"

    def execute(self, context):
        from ..lib import mesh, ui_lib

        ob = context.object

        if not ob or ob.type != "CURVE":
            self.report({"ERROR"}, "Active object must be a curve")
            return {"CANCELLED"}

        length = unit.Scale().from_scene(mesh.est_curve_length(ob))
        report = f"{length:.2f} {_('mm')}"

        ui_lib.popup_list(self, _("Curve Length"), (report,))

        return {"FINISHED"}


class OBJECT_OT_stretch_along_curve(Operator):
    bl_label = "Stretch Along Curve"
    bl_description = (
        "Stretch deformed objects along curve on X axis, "
        "also works in Edit Mode with selected vertices"
    )
    bl_idname = "object.jewelcraft_stretch_along_curve"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import bmesh
        from ..lib import asset, mesh

        if context.mode == "EDIT_MESH":

            for ob in context.objects_in_mode:
                me = ob.data
                curve = asset.mod_curve_off(ob)

                if not curve:
                    continue

                length = mesh.est_curve_length(curve)
                length_halved = length / 2 / ob.matrix_world.to_scale()[0]

                bm = bmesh.from_edit_mesh(me)
                for v in bm.verts:
                    if v.select:
                        if v.co.x > 0.0:
                            v.co.x = length_halved
                        else:
                            v.co.x = -length_halved
                bm.normal_update()
                bmesh.update_edit_mesh(me, destructive=False)

        else:

            for ob in context.selected_objects:
                if ob.type != "MESH":
                    continue

                curve = asset.mod_curve_off(ob)
                BBox = asset.BoundBox((ob,))

                if not curve:
                    continue

                length = mesh.est_curve_length(curve)
                ob.scale.x = length / BBox.dimensions.x * ob.scale.x

        return {"FINISHED"}


class OBJECT_OT_move_over_under(Operator):
    bl_label = "Move Over/Under"
    bl_description = "Move deformed object over or under the curve"
    bl_idname = "object.jewelcraft_move_over_under"
    bl_options = {"REGISTER", "UNDO"}

    position: EnumProperty(
        name="Position",
        items=(
            ("OVER", "Over", ""),
            ("UNDER", "Under", ""),
        ),
        options={"SKIP_SAVE"},
    )
    individual: BoolProperty(name="Individual", description="Move each object individually")

    def execute(self, context):
        import bmesh
        from ..lib import asset

        context.view_layer.update()

        if self.individual:

            for ob in context.selected_objects:
                if ob.type != "MESH":
                    continue

                curve = asset.mod_curve_off(ob)
                BBox = asset.BoundBox((ob,))

                if self.position == "UNDER":
                    z_object = BBox.max.z
                else:
                    z_object = BBox.min.z

                if curve:
                    z_pivot = curve.location.z
                else:
                    z_pivot = 0.0

                z_offset = z_pivot - z_object

                if context.mode == "OBJECT":
                    ob.location.z += z_offset
                else:
                    bm = bmesh.from_edit_mesh(ob.data)
                    for v in bm.verts:
                        if v.select:
                            v.co.z += z_offset
                    bm.normal_update()
                    bmesh.update_edit_mesh(ob.data, destructive=False)

        else:

            if not (ob := context.edit_object or context.object):
                return {"CANCELLED"}

            curve = asset.mod_curve_off(ob)
            BBox = asset.BoundBox((ob,))

            if self.position == "UNDER":
                z_object = BBox.max.z
            else:
                z_object = BBox.min.z

            if curve:
                z_pivot = curve.matrix_world.translation.z
            else:
                z_pivot = 0.0

            bpy.ops.transform.translate(value=(0.0, 0.0, z_pivot - z_object))

        return {"FINISHED"}
