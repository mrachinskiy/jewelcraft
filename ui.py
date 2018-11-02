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
from bpy.types import Panel, Menu, UIList

from . import var, addon_updater_ops
from .lib import asset


# Utils
# ---------------------------


class Setup:
    bl_category = "JewelCraft"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def __init__(self):
        self.prefs = bpy.context.user_preferences.addons[__package__].preferences
        self.scene_props = bpy.context.scene.jewelcraft
        self.wm_props = bpy.context.window_manager.jewelcraft
        self.pcoll = var.preview_collections["icons"]


# Lists
# ---------------------------


class VIEW3D_UL_jewelcraft_weighting_set(UIList, Setup):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")

        row = row.row(align=True)
        row.active = item.enabled
        row.prop(item, "name", text="", emboss=False)

        if self.prefs.weighting_list_show_composition:
            sub = row.row(align=True)
            sub.scale_x = 1.5
            sub.prop(item, "composition", text="", emboss=False)

        if self.prefs.weighting_list_show_density:
            sub = row.row(align=True)
            sub.scale_x = 0.5
            sub.prop(item, "density", text="", emboss=False)


# Menus
# ---------------------------


class VIEW3D_MT_jewelcraft_select_gem_by(Menu):
    bl_label = "Select Gems By..."
    bl_description = "Select gems by trait"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Size", text_ctxt="Dative").filter_size = True
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Stone", text_ctxt="Dative").filter_stone = True
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Cut", text_ctxt="Dative").filter_cut = True
        layout.separator()
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Similar").filter_similar = True
        layout.operator("object.jewelcraft_select_doubles", text="Doubles")
        layout.separator()
        layout.operator("object.jewelcraft_select_gems_by_trait", text="All")


class VIEW3D_MT_jewelcraft_folder(Menu):
    bl_label = ""

    def draw(self, context):
        library_folder = asset.user_asset_library_folder_object()
        layout = self.layout
        layout.operator("wm.jewelcraft_asset_folder_create", icon="ZOOMIN")
        layout.operator("wm.jewelcraft_asset_folder_rename", text="Rename", icon="LINE_DATA")
        layout.separator()
        layout.operator("wm.path_open", text="Open Library Folder", icon="FILE_FOLDER").filepath = library_folder
        layout.separator()
        layout.operator("wm.jewelcraft_asset_ui_refresh", icon="FILE_REFRESH")


class VIEW3D_MT_jewelcraft_asset(Menu):
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.jewelcraft_asset_rename", text="Rename", icon="LINE_DATA")
        layout.operator("wm.jewelcraft_asset_replace", icon="GROUP")
        layout.operator("wm.jewelcraft_asset_preview_replace", text="Replace Preview", icon="IMAGE_DATA")


class VIEW3D_MT_jewelcraft_weighting_set(Menu):
    bl_label = ""

    def draw(self, context):
        library_folder = asset.user_asset_library_folder_weighting()
        layout = self.layout
        layout.operator("wm.jewelcraft_weighting_set_add", icon="ZOOMIN")
        layout.operator("wm.jewelcraft_weighting_set_del", text="Remove", icon="ZOOMOUT")
        layout.operator("wm.jewelcraft_weighting_set_rename", text="Rename", icon="LINE_DATA")
        layout.operator("wm.jewelcraft_weighting_set_replace", text="Replace", icon="GHOST")
        layout.separator()
        layout.operator("wm.path_open", text="Open Library Folder", icon="FILE_FOLDER").filepath = library_folder
        layout.separator()
        layout.operator("wm.jewelcraft_weighting_set_refresh", icon="FILE_REFRESH")


class VIEW3D_MT_jewelcraft_weighting_list(Menu, Setup):
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.jewelcraft_ul_item_clear", icon="X")
        layout.separator()
        layout.prop(self.prefs, "weighting_list_show_composition")
        layout.prop(self.prefs, "weighting_list_show_density")


class VIEW3D_MT_jewelcraft_product_report(Menu, Setup):
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        layout.prop(self.prefs, "product_report_display")
        layout.prop(self.prefs, "product_report_save")
        layout.prop(self.prefs, "product_report_use_layers")
        layout.separator()
        layout.label("Report Language:")
        layout.prop(self.prefs, "product_report_lang", text="")


# Panels
# ---------------------------


class VIEW3D_PT_jewelcraft_update(Panel, Setup):
    bl_label = "Update"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return addon_updater_ops.updater.update_ready

    def draw(self, context):
        addon_updater_ops.update_notice_box_ui(self, context)


class VIEW3D_PT_jewelcraft_gems(Panel, Setup):
    bl_label = "Gems"

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"}

    def draw(self, context):
        addon_updater_ops.check_for_update_background()

        layout = self.layout

        layout.template_icon_view(self.wm_props, "gem_cut", show_labels=True)

        row = layout.row(align=True)
        row.prop(self.wm_props, "gem_stone", text="")
        row.operator("view3d.jewelcraft_search_stone", text="", icon="VIEWZOOM")

        row = layout.row(align=True)
        row.operator("object.jewelcraft_gem_add", text="Add Gem", icon_value=self.pcoll["gem_add"].icon_id)
        row.operator("object.jewelcraft_gem_edit", text="", icon_value=self.pcoll["gem_edit"].icon_id)

        layout.menu("VIEW3D_MT_jewelcraft_select_gem_by")


class VIEW3D_PT_jewelcraft_widgets(Panel, Setup):
    bl_label = "Widgets"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"}

    def draw_header(self, context):
        layout = self.layout
        layout.prop(self.wm_props, "widget_toggle", text="")

    def draw(self, context):
        layout = self.layout
        layout.active = self.wm_props.widget_toggle

        col = layout.column(align=True)
        col.prop(self.prefs, "widget_selection_only")
        col.prop(self.prefs, "widget_use_overrides")
        sub = col.column()
        sub.active = self.prefs.widget_use_overrides
        sub.prop(self.prefs, "widget_overrides_only")
        col.prop(self.prefs, "widget_x_ray")

        col = layout.column(align=True)
        col.prop(self.prefs, "widget_color", text="")
        col.prop(self.prefs, "widget_linewidth")
        col.prop(self.prefs, "widget_distance")

        row = layout.row(align=True)
        row.operator("object.jewelcraft_widgets_overrides_set")
        row.operator("object.jewelcraft_widgets_overrides_del")


class VIEW3D_PT_jewelcraft_assets(Panel, Setup):
    bl_label = "Assets"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"}

    def draw(self, context):
        layout = self.layout

        if not self.wm_props.asset_folder:
            layout.operator("wm.jewelcraft_asset_folder_create", icon="ZOOMIN")
            layout.operator("wm.jewelcraft_asset_ui_refresh", icon="FILE_REFRESH")
            return

        row = layout.row(align=True)
        row.prop(self.wm_props, "asset_folder", text="")
        row.menu("VIEW3D_MT_jewelcraft_folder", icon="SCRIPTWIN")

        row = layout.row()

        col = row.column()
        col.enabled = bool(self.wm_props.asset_list)
        col.template_icon_view(self.wm_props, "asset_list", show_labels=True)

        if self.prefs.display_asset_name:
            col.label(self.wm_props.asset_list)

        col = row.column(align=True)
        col.operator("wm.jewelcraft_asset_add_to_library", text="", icon="ZOOMIN")
        col.operator("wm.jewelcraft_asset_remove_from_library", text="", icon="ZOOMOUT")
        col.operator("view3d.jewelcraft_search_asset", text="", icon="VIEWZOOM")
        col.menu("VIEW3D_MT_jewelcraft_asset", icon="SCRIPTWIN")

        layout.operator("wm.jewelcraft_asset_import", text="Import Asset")


class VIEW3D_PT_jewelcraft_jeweling(Panel, Setup):
    bl_label = "Jeweling"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.jewelcraft_prongs_add", text="Prongs", icon_value=self.pcoll["prongs"].icon_id)
        col.operator("object.jewelcraft_cutter_add", text="Cutter", icon_value=self.pcoll["cutter"].icon_id)

        row = layout.row(align=True)
        row.operator("object.jewelcraft_curve_scatter", text="Curve Scatter", icon_value=self.pcoll["scatter"].icon_id)
        row.operator("object.jewelcraft_curve_redistribute", text="", icon_value=self.pcoll["redistribute"].icon_id)


class VIEW3D_PT_jewelcraft_object(Panel, Setup):
    bl_label = "Object"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.jewelcraft_mirror", text="Mirror", icon_value=self.pcoll["mirror"].icon_id)
        col.operator("object.jewelcraft_make_dupliface", text="Make Dupli-face", icon_value=self.pcoll["dupliface"].icon_id)

        layout.operator("object.jewelcraft_resize", text="Resize", icon_value=self.pcoll["resize"].icon_id)

        col = layout.column(align=True)
        col.operator("object.jewelcraft_lattice_project", text="Lattice Project", icon_value=self.pcoll["lattice_project"].icon_id,)
        col.operator("object.jewelcraft_lattice_profile", text="Lattice Profile", icon_value=self.pcoll["lattice_profile"].icon_id,)


class VIEW3D_PT_jewelcraft_curve(Panel, Setup):
    bl_label = "Curve"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        layout.operator("curve.jewelcraft_size_curve_add", text="Size Curve", icon_value=self.pcoll["size_curve"].icon_id)

        row = layout.row()
        row.operator("object.jewelcraft_stretch_along_curve", text="Stretch", icon_value=self.pcoll["stretch"].icon_id)
        sub = row.row(align=True)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.pcoll["over"].icon_id)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.pcoll["under"].icon_id).under = True

        layout.operator("curve.jewelcraft_length_display", text="Curve Length", icon_value=self.pcoll["curve_length"].icon_id)


class VIEW3D_PT_jewelcraft_curve_editmesh(Panel, Setup):
    bl_label = "Curve"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.jewelcraft_stretch_along_curve", text="Stretch", icon_value=self.pcoll["stretch"].icon_id)
        sub = row.row(align=True)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.pcoll["over"].icon_id)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.pcoll["under"].icon_id).under = True


class VIEW3D_PT_jewelcraft_weighting(Panel, Setup):
    bl_label = "Weighting"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        material_list = self.prefs.weighting_materials

        row = layout.row(align=True)
        row.prop(self.wm_props, "weighting_set", text="")
        row.menu("VIEW3D_MT_jewelcraft_weighting_set", icon="SCRIPTWIN")

        row = layout.row(align=True)
        row.operator("wm.jewelcraft_weighting_set_load")
        row.operator("wm.jewelcraft_weighting_set_load_append")

        layout.separator()

        row = layout.row()

        col = row.column()
        col.template_list("VIEW3D_UL_jewelcraft_weighting_set", "", material_list, "coll", material_list, "index", rows=5)

        col = row.column(align=True)
        col.operator("wm.jewelcraft_ul_item_add", text="", icon="ZOOMIN")
        col.operator("wm.jewelcraft_ul_item_del", text="", icon="ZOOMOUT")
        col.menu("VIEW3D_MT_jewelcraft_weighting_list", icon="SCRIPTWIN")
        col.separator()
        col.operator("wm.jewelcraft_ul_item_move", text="", icon="TRIA_UP").move_up = True
        col.operator("wm.jewelcraft_ul_item_move", text="", icon="TRIA_DOWN")

        layout.operator("object.jewelcraft_weight_display", text="Calculate")


class VIEW3D_PT_jewelcraft_product_report(Panel, Setup):
    bl_label = "Product Report"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        col = row.column(align=True)
        col.alignment = "RIGHT"
        col.scale_x = 0.9
        col.label("Size")
        col.label("Shank")
        col.label("Dimensions", text_ctxt="JewelCraft")
        col.label("Weight")
        col = row.column(align=True)
        col.prop(self.scene_props, "product_report_ob_size", text="")
        col.prop(self.scene_props, "product_report_ob_shank", text="")
        col.prop(self.scene_props, "product_report_ob_dim", text="")
        col.prop(self.scene_props, "product_report_ob_weight", text="")

        layout.separator()

        row = layout.row(align=True)
        row.operator("wm.jewelcraft_product_report", text="Product Report")
        row.menu("VIEW3D_MT_jewelcraft_product_report", icon="SCRIPTWIN")
