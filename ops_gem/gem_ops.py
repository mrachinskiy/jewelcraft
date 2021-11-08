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


import bpy
from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from bpy.app.translations import pgettext_iface as _
from mathutils import Matrix

from .. import var
from ..lib import dynamic_list, unit


def upd_set_weight(self, context):
    if self.stone == "DIAMOND" and self.cut == "ROUND":
        self["weight"] = unit.convert_mm_ct(unit.Scale().from_scene(self.size))


def upd_weight(self, context):
    self["size"] = unit.Scale().to_scene(unit.convert_ct_mm(self.weight))


class OBJECT_OT_gem_add(Operator):
    bl_label = "Add Gem"
    bl_description = "Add gemstone to the scene"
    bl_idname = "object.jewelcraft_gem_add"
    bl_options = {"REGISTER", "UNDO"}

    cut: EnumProperty(name="Cut", items=dynamic_list.cuts, update=upd_set_weight)
    stone: EnumProperty(name="Stone", items=dynamic_list.stones, update=upd_set_weight)
    size: FloatProperty(
        name="Size",
        default=1.0,
        min=0.0001,
        step=5,
        precision=2,
        unit="LENGTH",
        update=upd_set_weight,
    )
    weight: FloatProperty(
        name="Carats",
        description="Round diamonds only",
        default=0.004,
        min=0.0001,
        step=0.1,
        precision=3,
        update=upd_weight,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "size")
        col = layout.column()
        col.enabled = self.stone == "DIAMOND" and self.cut == "ROUND"
        col.prop(self, "weight")
        layout.prop(self, "stone")
        split = layout.split(factor=0.4)
        row = split.row()
        row.alignment = "RIGHT"
        row.label(text="Cut", text_ctxt="Jewelry")
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        from ..lib import asset, gemlib

        scene = context.scene
        view_layer = context.view_layer
        space_data = context.space_data
        cut_name = gemlib.CUTS[self.cut].name
        stone_name = gemlib.STONES[self.stone].name
        color = gemlib.STONES[self.stone].color or self.color

        for ob in context.selected_objects:
            ob.select_set(False)

        imported = asset.asset_import(var.GEM_ASSET_FILEPATH, ob_name=cut_name)
        ob = imported.objects[0]
        context.collection.objects.link(ob)

        if space_data.local_view:
            ob.local_view_set(space_data, True)

        ob.scale *= self.size
        ob.location = scene.cursor.location
        ob.select_set(True)
        ob["gem"] = {"cut": self.cut, "stone": self.stone}

        asset.add_material(ob, name=stone_name, color=color, is_gem=True)

        if context.mode == "EDIT_MESH":
            asset.ob_copy_to_faces(ob)
            bpy.ops.object.mode_set(mode="OBJECT")

        view_layer.objects.active = ob

        return {"FINISHED"}

    def invoke(self, context, event):
        from ..lib import asset

        self.color = asset.color_rnd()

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class OBJECT_OT_gem_edit(Operator):
    bl_label = "Edit Gem"
    bl_description = "Edit selected gems"
    bl_idname = "object.jewelcraft_gem_edit"
    bl_options = {"REGISTER", "UNDO"}

    cut: EnumProperty(name="Cut", items=dynamic_list.cuts, options={"SKIP_SAVE"})
    stone: EnumProperty(name="Stone", items=dynamic_list.stones, options={"SKIP_SAVE"})
    use_id_only: BoolProperty(
        name="Only ID",
        description="Only edit gem identifiers, not affecting object data and materials",
        options={"SKIP_SAVE"},
    )
    use_force: BoolProperty(
        name="Force Edit",
        description="Force edit selected mesh objects, can be used to make gems from non-gem objects",
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "stone")
        split = layout.split(factor=0.4)
        row = split.row()
        row.alignment = "RIGHT"
        row.label(text="Cut", text_ctxt="Jewelry")
        split.template_icon_view(self, "cut", show_labels=True)

        layout.separator()

        layout.prop(self, "use_id_only")
        layout.prop(self, "use_force")

    def execute(self, context):
        from ..lib import asset, gemlib

        obs = context.selected_objects
        cut_name = gemlib.CUTS[self.cut].name
        stone_name = gemlib.STONES[self.stone].name
        color = gemlib.STONES[self.stone].color or self.color

        imported = asset.asset_import(var.GEM_ASSET_FILEPATH, me_name=cut_name)
        me = imported.meshes[0]

        for ob in obs:

            if ob.type != "MESH":
                continue

            if self.use_force or "gem" in ob:

                if self.use_force:
                    ob["gem"] = {}

                if self.use_force or ob["gem"]["cut"] != self.cut:

                    ob["gem"]["cut"] = self.cut

                    if not self.use_id_only:
                        size_orig = ob.dimensions.y
                        mats_orig = ob.data.materials

                        ob.data = me.copy()
                        ob.name = cut_name

                        ob.scale = (size_orig, size_orig, size_orig)
                        asset.apply_scale(ob)

                        for mat in mats_orig:
                            ob.data.materials.append(mat)

                if self.use_force or ob["gem"]["stone"] != self.stone:

                    ob["gem"]["stone"] = self.stone

                    if not self.use_id_only:

                        if ob.data.users > 1:
                            ob.data = ob.data.copy()

                        asset.add_material(ob, name=stone_name, color=color, is_gem=True)

        bpy.data.meshes.remove(me)

        return {"FINISHED"}

    def invoke(self, context, event):
        from ..lib import asset

        if not context.selected_objects:
            self.report({"ERROR"}, "At least one gem object must be selected")
            return {"CANCELLED"}

        ob = context.object

        if ob is not None and "gem" in ob:
            self.cut = ob["gem"]["cut"]
            self.stone = ob["gem"]["stone"]

        self.color = asset.color_rnd()

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_gem_recover(Operator):
    bl_label = "Recover Gem"
    bl_description = (
        "Separate loose, center origin and fix orientation (can recover gems from STL file)."
        "\nNOTE: gem ID can be added with Edit Gem tool"
    )
    bl_idname = "object.jewelcraft_gem_recover"
    bl_options = {"REGISTER", "UNDO"}

    axis_size: FloatProperty(default=1.0, options={"HIDDEN"})
    axis_width: FloatProperty(default=7.0, options={"HIDDEN"})
    axis_in_front: BoolProperty(default=True, options={"HIDDEN"})
    y_align: BoolProperty(options={"HIDDEN"})
    snap_to_edge: BoolProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def modal(self, context, event):
        if event.type in {"ESC", "RET", "SPACE", "NUMPAD_ENTER"}:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, "WINDOW")
            bpy.types.SpaceView3D.draw_handler_remove(self.handler_text, "WINDOW")
            context.workspace.status_text_set(None)
            context.region.tag_redraw()

            if event.type == "ESC":
                return {"CANCELLED"}

            return self.execute(context)

        elif event.type in {"LEFT_ARROW", "RIGHT_ARROW"} and event.value == "PRESS":

            if event.ctrl:
                if event.type == "LEFT_ARROW":
                    if self.y_var > 1:
                        self.y_var -= 1
                        self.modal_pass(context)
                else:
                    self.y_var += 1
                    self.modal_pass(context)

            else:
                if event.type == "LEFT_ARROW":
                    if self.rot_var > 1:
                        self.rot_var -= 1
                        self.modal_pass(context)
                else:
                    self.rot_var += 1
                    self.modal_pass(context)

        elif event.type in {"DOWN_ARROW", "UP_ARROW"} and event.value == "PRESS":
            if event.type == "DOWN_ARROW":
                if self.xy_loc > 0:
                    self.xy_loc -= 1
                    self.modal_pass(context)
            else:
                if self.xy_loc < 2:
                    self.xy_loc += 1
                    self.modal_pass(context)

        elif event.type == "Y" and event.value == "PRESS":
            self.y_align = not self.y_align
            self.modal_pass(context)

        elif event.type == "E" and event.value == "PRESS":
            self.snap_to_edge = not self.snap_to_edge
            self.modal_pass(context)

        elif event.type == "X" and event.value == "PRESS":
            self.axis_in_front = not self.axis_in_front
            context.region.tag_redraw()

        elif event.type in {"LEFT_BRACKET", "RIGHT_BRACKET"} and event.value == "PRESS":
            if event.type == "LEFT_BRACKET":
                if self.axis_width > 0.5:
                    self.axis_width -= 0.1
            else:
                self.axis_width += 0.1

            context.region.tag_redraw()

        elif event.type in {"MINUS", "EQUAL"} and event.value == "PRESS":
            if event.type == "MINUS":
                if self.axis_size > 0.1:
                    self.axis_size -= 0.1
            else:
                self.axis_size += 0.1

            context.region.tag_redraw()

        elif (
            event.type in {
                "MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE",
                "NUMPAD_1", "NUMPAD_2", "NUMPAD_3", "NUMPAD_4", "NUMPAD_5",
                "NUMPAD_6", "NUMPAD_7", "NUMPAD_8", "NUMPAD_9",
                "NUMPAD_MINUS", "NUMPAD_PLUS",
            }
        ):
            return {"PASS_THROUGH"}

        return {"RUNNING_MODAL"}

    def execute(self, context):
        import collections
        import operator
        import itertools

        rotvar = self.rot_var - 1
        yvar = self.y_var - 1
        app = self.mats.append

        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")

        for ob in context.selected_objects:
            normal_groups = collections.defaultdict(float)

            for poly in ob.data.polygons:
                normal_groups[poly.normal.copy().freeze()] += poly.area

            normals = sorted(normal_groups.items(), key=operator.itemgetter(1), reverse=True)

            try:
                normal = normals[rotvar][0]
            except IndexError:
                normal = normals[0][0]

            mat = normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
            ob.matrix_world @= mat
            ob.data.transform(mat.inverted())

            # Adjust origin
            # ------------------------------

            verts = sorted(ob.data.vertices, key=operator.attrgetter("co.xy.length"), reverse=True)[:8]

            # Z height

            co_z_low = min(verts, key=operator.attrgetter("co.z")).co.z

            if co_z_low != 0.0:
                mat = Matrix.Translation((0.0, 0.0, co_z_low))
                ob.matrix_world @= mat
                ob.data.transform(mat.inverted())

            # Y align

            if self.y_align:

                if self.snap_to_edge:
                    cos = [
                        (
                            (v1.co.xy + v2.co.xy) / 2,
                            (v1.co.xy - v2.co.xy).length,
                        )
                        for v1, v2 in itertools.combinations(verts, 2)
                    ]
                    cos.sort(key=operator.itemgetter(1))

                    try:
                        vec = cos[yvar][0]
                    except IndexError:
                        vec = cos[0][0]

                else:
                    try:
                        vec = verts[yvar].co.xy
                    except IndexError:
                        vec = verts[0].co.xy

                vec.negate()
                vec.resize_3d()

                mat = vec.to_track_quat("Y", "Z").to_matrix().to_4x4()
                ob.matrix_world @= mat
                ob.data.transform(mat.inverted())

            # XY center

            if self.xy_loc != 0:

                if self.xy_loc == 1:
                    context.view_layer.update()

                    xy_min = min((x[0], x[1]) for x in ob.bound_box)
                    xy_max = max((x[0], x[1]) for x in ob.bound_box)

                    x_loc = (xy_min[0] + xy_max[0]) / 2
                    y_loc = (xy_min[1] + xy_max[1]) / 2

                    co_xy = (x_loc, y_loc)

                elif self.xy_loc == 2:
                    co_xy = min(ob.data.vertices, key=operator.attrgetter("co.z")).co.xy

                if co_xy[0] != 0.0 or co_xy[1] != 0.0:
                    mat = Matrix.Translation((*co_xy, 0.0))
                    ob.matrix_world @= mat
                    ob.data.transform(mat.inverted())

            # Display axis

            app(ob.matrix_world.copy())

        return {"FINISHED"}

    def modal_pass(self, context):
        self.mats.clear()
        bpy.ops.object.duplicate()

        self.execute(context)

        # Cleanup

        for ob in context.selected_objects:
            bpy.data.meshes.remove(ob.data)

        # Restore selection

        for ob_name in self.ob_names:
            bpy.data.objects[ob_name].select_set(True)

        context.view_layer.objects.active = bpy.data.objects[ob_name]

    def invoke(self, context, event):
        from ..lib import view3d_lib

        self.ob_names = []
        unique_meshes = set()

        for ob in context.selected_objects:
            if ob.type != "MESH" or ob.data in unique_meshes:
                ob.select_set(False)
                continue
            self.ob_names.append(ob.name)
            unique_meshes.add(ob.data)

        if not self.ob_names:
            self.report({"ERROR"}, "At least one mesh object must be selected")
            return {"CANCELLED"}

        self.mats = []
        self.rot_var = 1
        self.y_var = 1
        self.xy_loc = 0
        self.xy_loc_enum = (_("Median"), _("Bounds"), _("Culet"))

        self.modal_pass(context)

        # Onscreen

        self.padding_x, self.padding_y = view3d_lib.padding_init(context)

        view3d_lib.options_init(
            self,
            (
                (_("In Front"), "(X)", "axis_in_front", view3d_lib.TYPE_BOOL),
                (_("Size"), "(-/=)", "axis_size", view3d_lib.TYPE_NUM),
                (_("Width"), "([/])", "axis_width", view3d_lib.TYPE_NUM),
                ("", "", None, None),
                (_("Orientation"), "(←/→)", "rot_var", view3d_lib.TYPE_NUM),
                (_("Center"), "(↓/↑)", "xy_loc", view3d_lib.TYPE_ENUM),
                ("", "", None, None),
                (_("Align Y"), "(Y)", "y_align", view3d_lib.TYPE_BOOL),
                ("", "", "y_align", view3d_lib.TYPE_DEP_ON),
                (_("Snap to Edges"), "(E)", "snap_to_edge", view3d_lib.TYPE_BOOL),
                (_("Direction"), "(Ctrl ←/→)", "y_var", view3d_lib.TYPE_NUM),
            ),
        )

        # Draw handlers

        self.handler = bpy.types.SpaceView3D.draw_handler_add(
            view3d_lib.draw_axis,
            (self, context),
            "WINDOW",
            "POST_VIEW",
        )
        self.handler_text = bpy.types.SpaceView3D.draw_handler_add(
            view3d_lib.options_display,
            (self, context, self.padding_x, self.padding_y),
            "WINDOW",
            "POST_PIXEL",
        )

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set("ESC: Cancel, ↵/␣: Confirm")

        return {"RUNNING_MODAL"}
