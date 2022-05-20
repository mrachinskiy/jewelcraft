# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from bpy.app.translations import pgettext_tip as _

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
        eq_size = (lambda ob: round(ob.dimensions.y, 2) == size) if self.filter_size else (lambda x: True)
        eq_stone = (lambda ob: ob["gem"]["stone"] == self.stone) if self.filter_stone else (lambda x: True)
        eq_cut = (lambda ob: ob["gem"]["cut"] == self.cut) if self.filter_cut else (lambda x: True)
        selected = None

        if not self.use_extend:
            for ob in context.selected_objects:
                ob.select_set(False)

        for ob in context.visible_objects:
            if "gem" in ob and eq_size(ob) and eq_stone(ob) and eq_cut(ob):
                ob.select_set(True)

                if ob.select_get():
                    selected = ob

                if self.use_select_children and ob.children:
                    for child in ob.children:
                        child.select_set(True)

        ob = context.object
        if ob is None or not (ob.select_get() and "gem" in ob):
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
        app_obs = obs.append
        app_data = ob_data.append
        depsgraph = context.evaluated_depsgraph_get()

        for dup in depsgraph.object_instances:

            if dup.is_instance:
                ob = dup.instance_object.original
                sel = dup.parent.original
                visible = dup.parent.original.visible_get()  # T74368
            else:
                ob = dup.object.original
                sel = ob
                visible = ob.visible_get()

            ob.select_set(False)

            if "gem" not in ob or not visible:
                continue

            app_obs(sel)
            app_data(asset.gem_transform(dup))

        overlaps = asset.gem_overlap(ob_data, self.threshold)

        if overlaps:
            for i in overlaps:
                obs[i].select_set(True)
            self.report({"WARNING"}, _("{} overlaps found").format(len(overlaps)))
        else:
            self.report({"INFO"}, _("{} overlaps found").format(0))

        return {"FINISHED"}
