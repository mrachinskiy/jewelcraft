# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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

from ..lib import asset, dynamic_list


class OBJECT_OT_jewelcraft_select_gems_by_trait(Operator):
    bl_label = "JewelCraft Select Gems By Trait"
    bl_description = "Select gems by trait"
    bl_idname = "object.jewelcraft_select_gems_by_trait"
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

        split = layout.split()
        split.prop(self, "filter_size")
        split.prop(self, "size", text="")

        split = layout.split()
        split.prop(self, "filter_stone")
        split.prop(self, "stone", text="")

        split = layout.split()
        split.prop(self, "filter_cut", text="Cut", text_ctxt="JewelCraft")
        split.template_icon_view(self, "cut", show_labels=True)

        layout.prop(self, "use_extend")
        layout.prop(self, "use_select_children")

    def execute(self, context):
        visible = context.visible_objects
        size = round(self.size, 2)
        selected = []
        app = selected.append

        expr = (
            "for ob in visible:"
            "\n    if 'gem' in ob {size} {stone} {cut}:"
            "\n        ob.select_set(True)"
            "\n        app(ob)"
            "\n    {else_deselect}"
        )

        expr = expr.format(
            size="and round(ob.dimensions[1], 2) == size" if self.filter_size  else "",
            stone="and ob['gem']['stone'] == self.stone"  if self.filter_stone else "",
            cut="and ob['gem']['cut'] == self.cut"        if self.filter_cut   else "",
            else_deselect="" if self.use_extend else "else: ob.select_set(False)",
        )

        exec(expr)

        if selected:

            if not context.object.select_get():
                context.view_layer.objects.active = selected[0]

            if self.use_select_children:
                visible = set(visible)

                for ob in selected:
                    if ob.children:
                        for child in ob.children:
                            if child in visible:
                                child.select_set(True)

        return {"FINISHED"}

    def invoke(self, context, event):
        ob = context.object

        if ob and "gem" in ob:
            self.size = ob.dimensions[1]
            self.stone = ob["gem"]["stone"]
            self.cut = ob["gem"]["cut"]

        if self.filter_similar:
            self.filter_size = True
            self.filter_stone = True
            self.filter_cut = True

        return self.execute(context)


class OBJECT_OT_jewelcraft_select_overlapping(Operator):
    bl_label = "JewelCraft Select Overlapping"
    bl_description = "Select gems that are less than 0.1 mm distance from each other or overlapping"
    bl_idname = "object.jewelcraft_select_overlapping"
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
        obs = []
        ob_data = []

        context.scene.update()

        for dup in context.depsgraph.object_instances:

            if dup.is_instance:
                ob = dup.instance_object.original
            else:
                ob = dup.object.original

            ob.select_set(False)

            if "gem" in ob:
                loc = dup.matrix_world.to_translation()
                rad = max(ob.dimensions[:2]) / 2

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

        overlaps = asset.gem_overlap(ob_data, threshold=self.threshold)

        if overlaps:
            for i in overlaps:
                ob = obs[i]
                if ob:
                    ob.select_set(True)

            self.report({"WARNING"}, _("{} overlaps found").format(len(overlaps)))

        else:
            self.report({"INFO"}, _("{} overlaps found").format(0))

        return {"FINISHED"}
