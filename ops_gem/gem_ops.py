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


import bpy
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Operator

from .. import var, dynamic_lists
from ..lib import asset


class OBJECT_OT_jewelcraft_gem_add(Operator):
    bl_label = "JewelCraft Make Gem"
    bl_description = "Add gemstone to the scene"
    bl_idname = "object.jewelcraft_gem_add"
    bl_options = {"REGISTER", "UNDO"}

    cut = EnumProperty(name="Cut", items=dynamic_lists.cuts)
    stone = EnumProperty(name="Stone", items=dynamic_lists.stones)
    size = FloatProperty(name="Size", description="Gem size", default=1.0, min=0.0001, step=10, precision=2, unit="LENGTH")

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.label("Size")
        split.prop(self, "size", text="")

        split = layout.split()
        split.label("Stone")
        split.prop(self, "stone", text="")

        split = layout.split()
        split.label("Cut", text_ctxt="JewelCraft")
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        scene = context.scene
        stone_name = asset.get_name(self.stone)
        cut_name = asset.get_name(self.cut)
        color = var.STONE_COLOR.get(self.stone) or self.color

        for ob in scene.objects:
            ob.select = False

        imported = asset.asset_import(filepath=var.GEM_ASSET_FILEPATH, ob_name=cut_name)
        ob = imported.objects[0]
        scene.objects.link(ob)

        ob.layers = self.view_layers
        ob.scale = ob.scale * self.size
        ob.location = scene.cursor_location
        ob.select = True
        ob["gem"] = {"cut": self.cut, "stone": self.stone}

        asset.add_material(ob, mat_name=stone_name, color=color, is_gem=True)

        if context.mode == "EDIT_MESH":
            asset.ob_copy_to_pos(ob)
            bpy.ops.object.mode_set(mode="OBJECT")

        scene.objects.active = ob

        return {"FINISHED"}

    def invoke(self, context, event):
        props = context.window_manager.jewelcraft
        self.stone = props.gem_stone
        self.cut = props.gem_cut
        self.color = asset.color_rnd()
        self.view_layers = [False for x in range(20)]
        self.view_layers[context.scene.active_layer] = True

        return self.execute(context)


class OBJECT_OT_jewelcraft_gem_edit(Operator):
    bl_label = "JewelCraft Edit Gem"
    bl_description = "Edit selected gems"
    bl_idname = "object.jewelcraft_gem_edit"
    bl_options = {"REGISTER", "UNDO"}

    cut = EnumProperty(name="Cut", items=dynamic_lists.cuts, options={"SKIP_SAVE"})
    stone = EnumProperty(name="Stone", items=dynamic_lists.stones, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.label("Stone")
        split.prop(self, "stone", text="")

        split = layout.split()
        split.label("Cut", text_ctxt="JewelCraft")
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        obs = context.selected_objects

        if self.cut != self.cut_orig:

            cut_name = asset.get_name(self.cut)
            imported = asset.asset_import(filepath=var.GEM_ASSET_FILEPATH, me_name=cut_name)
            me = imported.meshes[0]

            for ob in obs:
                if "gem" in ob:

                    size_orig = ob.dimensions[1]
                    mats_orig = ob.data.materials

                    ob.data = me.copy()
                    ob["gem"]["cut"] = self.cut
                    ob.name = cut_name

                    ob.scale = (size_orig, size_orig, size_orig)
                    asset.apply_scale(ob)

                    for mat in mats_orig:
                        ob.data.materials.append(mat)

            bpy.data.meshes.remove(me)

        if self.stone != self.stone_orig:

            stone_name = asset.get_name(self.stone)
            color = var.STONE_COLOR.get(self.stone) or self.color

            for ob in obs:
                if "gem" in ob:

                    if ob.data.users > 1:
                        ob.data = ob.data.copy()

                    ob["gem"]["stone"] = self.stone
                    asset.add_material(ob, mat_name=stone_name, color=color, is_gem=True)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects or not context.active_object:
            self.report({"ERROR"}, "At least one gem object must be selected")
            return {"CANCELLED"}

        ob = context.active_object

        if "gem" in ob:
            self.cut = ob["gem"]["cut"]
            self.stone = ob["gem"]["stone"]

        self.stone_orig = self.stone
        self.cut_orig = self.cut
        self.color = asset.color_rnd()

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_jewelcraft_gem_id_add(Operator):
    bl_label = "JewelCraft Add Gem ID"
    bl_description = "Add gem identifiers to selected objects"
    bl_idname = "object.jewelcraft_gem_id_add"
    bl_options = {"REGISTER", "UNDO"}

    cut = EnumProperty(name="Cut", items=dynamic_lists.cuts)
    stone = EnumProperty(name="Stone", items=dynamic_lists.stones)

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.label("Stone")
        split.prop(self, "stone", text="")

        split = layout.split()
        split.label("Cut", text_ctxt="JewelCraft")
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.type == "MESH":
                ob["gem"] = {"cut": self.cut, "stone": self.stone}

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class OBJECT_OT_jewelcraft_gem_id_convert_deprecated(Operator):
    bl_label = "JewelCraft Convert Deprecated Gem IDs"
    bl_description = "Convert deprecated gem identifiers to compatible for all objects in the scene"
    bl_idname = "object.jewelcraft_gem_id_convert_deprecated"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obs = context.scene.objects

        for ob in obs:
            if ob.type == "MESH" and "gem" in ob.data:

                if "gem" not in ob:
                    ob["gem"] = {}

                    for k, v in ob.data["gem"].items():
                        if k.lower() == "cut":
                            ob["gem"]["cut"] = v
                        elif k.lower() == "type":
                            ob["gem"]["stone"] = v

                del ob.data["gem"]

                if ob.data.users > 1:
                    for link in obs:
                        if link.data == ob.data:
                            link["gem"] = ob["gem"]

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
