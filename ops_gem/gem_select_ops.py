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


import collections

from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from bpy.app.translations import pgettext_tip as _

from ..lib import dynamic_list


class OBJECT_OT_jewelcraft_select_gems_by_trait(Operator):
    bl_label = "JewelCraft Select Gems By Trait"
    bl_description = "Select gems by trait"
    bl_idname = "object.jewelcraft_select_gems_by_trait"
    bl_options = {"REGISTER", "UNDO"}

    filter_size: BoolProperty(name="Size", options={"SKIP_SAVE"})
    filter_stone: BoolProperty(name="Stone", options={"SKIP_SAVE"})
    filter_cut: BoolProperty(name="Cut", options={"SKIP_SAVE"})
    filter_similar: BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    size: FloatProperty(name="Size", default=1.0, min=0.0, step=10, precision=2, unit="LENGTH")
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


class OBJECT_OT_jewelcraft_select_doubles(Operator):
    bl_label = "JewelCraft Select Doubles"
    bl_description = "Select duplicated gems (located in the same spot)"
    bl_idname = "object.jewelcraft_select_doubles"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        doubles = collections.defaultdict(list)

        for dup in context.depsgraph.object_instances:

            if dup.is_instance:
                ob = dup.instance_object.original
            else:
                ob = dup.object.original

            ob.select_set(False)

            if "gem" in ob:

                if dup.is_instance:

                    if ob.parent and ob.parent.is_instancer:
                        value = ob.parent
                    else:
                        value = None

                else:
                    value = ob

                loc = dup.matrix_world.translation.to_tuple()
                doubles[loc].append(value)

        doubles = {k: v for k, v in doubles.items() if len(v) > 1}

        if doubles:
            d = 0

            for obs in doubles.values():
                for ob in obs[1:]:
                    if ob:
                        ob.select_set(True)
                    d += 1

            self.report({"WARNING"}, _("{} duplicates found").format(d))

        else:
            self.report({"INFO"}, _("{} duplicates found").format(0))

        return {"FINISHED"}
