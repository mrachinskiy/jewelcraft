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


import bpy
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Operator

from .. import var
from ..lib import asset, dynamic_list


class OBJECT_OT_gem_add(Operator):
    bl_label = "JewelCraft Make Gem"
    bl_description = "Add gemstone to the scene"
    bl_idname = "object.jewelcraft_gem_add"
    bl_options = {"REGISTER", "UNDO"}

    cut: EnumProperty(name="Cut", items=dynamic_list.cuts)
    stone: EnumProperty(name="Stone", items=dynamic_list.stones)
    size: FloatProperty(
        name="Size",
        default=1.0,
        min=0.0001,
        step=5,
        precision=2,
        unit="LENGTH",
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "size")
        layout.prop(self, "stone")
        split = layout.split(factor=0.49)
        split.row()
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        scene = context.scene
        view_layer = context.view_layer
        space_data = context.space_data
        stone_name = asset.get_name(self.stone)
        cut_name = asset.get_name(self.cut)
        color = var.STONE_COLOR.get(self.stone) or self.color

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
        self.color = asset.color_rnd()

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class OBJECT_OT_gem_edit(Operator):
    bl_label = "JewelCraft Edit Gem"
    bl_description = "Edit selected gems"
    bl_idname = "object.jewelcraft_gem_edit"
    bl_options = {"REGISTER", "UNDO"}

    cut: EnumProperty(name="Cut", items=dynamic_list.cuts, options={"SKIP_SAVE"})
    stone: EnumProperty(name="Stone", items=dynamic_list.stones, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "stone")
        split = layout.split(factor=0.49)
        split.row()
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        obs = context.selected_objects

        if self.cut != self.cut_orig:

            cut_name = asset.get_name(self.cut)
            imported = asset.asset_import(var.GEM_ASSET_FILEPATH, me_name=cut_name)
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
                    asset.add_material(ob, name=stone_name, color=color, is_gem=True)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects or not context.object:
            self.report({"ERROR"}, "At least one gem object must be selected")
            return {"CANCELLED"}

        ob = context.object

        if "gem" in ob:
            self.cut = ob["gem"]["cut"]
            self.stone = ob["gem"]["stone"]

        self.stone_orig = self.stone
        self.cut_orig = self.cut
        self.color = asset.color_rnd()

        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


class OBJECT_OT_gem_id_add(Operator):
    bl_label = "JewelCraft Add Gem ID"
    bl_description = "Add gem identifiers to selected objects"
    bl_idname = "object.jewelcraft_gem_id_add"
    bl_options = {"REGISTER", "UNDO"}

    cut: EnumProperty(name="Cut", items=dynamic_list.cuts)
    stone: EnumProperty(name="Stone", items=dynamic_list.stones)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "stone")
        split = layout.split(factor=0.49)
        split.row()
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.type == "MESH":
                ob["gem"] = {"cut": self.cut, "stone": self.stone}

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class OBJECT_OT_gem_id_convert_deprecated(Operator):
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
                        if link.data is ob.data:
                            link["gem"] = ob["gem"]

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
