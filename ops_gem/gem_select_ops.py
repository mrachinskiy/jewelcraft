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


from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from bpy.app.translations import pgettext_tip as _
from mathutils import Matrix

from ..lib import dynamic_list


class OBJECT_OT_gem_select_by_trait(Operator):
    bl_label = "Select Gems by Trait"
    bl_description = "Select gems by trait"
    bl_idname = "object.jewelcraft_gem_select_by_trait"
    bl_options = {"REGISTER", "UNDO"}

    filter_size: BoolProperty(name="Size", options={"SKIP_SAVE"})
    filter_stone: BoolProperty(name="Stone", options={"SKIP_SAVE"})
    filter_cut: BoolProperty(name="Cut", options={"SKIP_SAVE"})
    filter_similar: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    size: FloatProperty(
        name="Size",
        default=1.0,
        min=0.0,
        step=10,
        precision=2,
        unit="LENGTH",
    )
    stone: EnumProperty(name="Stone", items=dynamic_list.stones)
    cut: EnumProperty(name="Cut", items=dynamic_list.cuts)

    use_extend: BoolProperty(name="Extend", description="Extend selection")
    use_select_children: BoolProperty(name="Select Children")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(heading="Size")
        row.prop(self, "filter_size", text="")
        row.prop(self, "size", text="")

        row = layout.row(heading="Stone")
        row.prop(self, "filter_stone", text="")
        row.prop(self, "stone", text="")

        row = layout.row(heading="Cut", heading_ctxt="Jewelry")
        row.prop(self, "filter_cut", text="")
        row.template_icon_view(self, "cut", show_labels=True)

        layout.separator()

        layout.prop(self, "use_extend")
        layout.prop(self, "use_select_children")

    def execute(self, context):
        size = round(self.size, 2)
        check_size = check_stone = check_cut = lambda x: True

        if self.filter_size:
            check_size = lambda ob: round(ob.dimensions.y, 2) == size
        if self.filter_stone:
            check_stone = lambda ob: ob["gem"]["stone"] == self.stone
        if self.filter_cut:
            check_cut = lambda ob: ob["gem"]["cut"] == self.cut

        selected = None

        for ob in context.visible_objects:
            if "gem" in ob and check_size(ob) and check_stone(ob) and check_cut(ob):
                selected = ob
                ob.select_set(True)
                if self.use_select_children and ob.children:
                    for child in ob.children:
                        child.select_set(True)
            elif not self.use_extend:
                ob.select_set(False)

        if context.object is None or not context.object.select_get():
            context.view_layer.objects.active = selected

        return {"FINISHED"}

    def invoke(self, context, event):
        ob = context.object

        if ob and "gem" in ob:
            self.size = ob.dimensions.y
            self.stone = ob["gem"]["stone"]
            self.cut = ob["gem"]["cut"]

        if self.filter_similar:
            self.filter_size = True
            self.filter_stone = True
            self.filter_cut = True

        return self.execute(context)


class OBJECT_OT_gem_select_overlapping(Operator):
    bl_label = "Select Overlapping"
    bl_description = "Select gems that are less than 0.1 mm distance from each other or overlapping"
    bl_idname = "object.jewelcraft_gem_select_overlapping"
    bl_options = {"REGISTER", "UNDO"}

    threshold: FloatProperty(
        name="Threshold",
        default=0.1,
        soft_min=0.0,
        step=1,
        precision=2,
        unit="LENGTH",
    )

    def execute(self, context):
        from ..lib import asset

        obs = []
        ob_data = []
        depsgraph = context.evaluated_depsgraph_get()

        for dup in depsgraph.object_instances:

            if dup.is_instance:
                ob = dup.instance_object.original
            else:
                ob = dup.object.original

            ob.select_set(False)

            if "gem" in ob:
                loc = dup.matrix_world.to_translation()
                rad = max(ob.dimensions.xy) / 2

                if dup.is_instance:
                    mat = dup.matrix_world.copy()

                    if ob.parent and ob.parent.is_instancer:
                        sel = ob.parent
                    else:
                        sel = None
                else:
                    mat_loc = Matrix.Translation(loc)
                    mat_rot = dup.matrix_world.to_quaternion().to_matrix().to_4x4()
                    mat = mat_loc @ mat_rot

                    sel = ob

                loc.freeze()
                mat.freeze()

                obs.append(sel)
                ob_data.append((loc, rad, mat))

        overlaps = asset.gem_overlap(ob_data, self.threshold)

        if overlaps:
            for i in overlaps:
                ob = obs[i]
                if ob:
                    ob.select_set(True)

            self.report({"WARNING"}, _("{} overlaps found").format(len(overlaps)))

        else:
            self.report({"INFO"}, _("{} overlaps found").format(0))

        return {"FINISHED"}
