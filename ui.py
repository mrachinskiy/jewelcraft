# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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

from . import var, mod_update
from .lib import asset, unit, dynamic_list


# Utils
# ---------------------------


class Setup:
    bl_category = "JewelCraft"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def __init__(self):
        self.prefs = bpy.context.preferences.addons[__package__].preferences
        self.wm_props = bpy.context.window_manager.jewelcraft
        self.pcoll = var.preview_collections["icons"]
        self.theme = self.prefs.theme_icon

    def icon_get(self, name):
        return self.pcoll[self.theme + name].icon_id


# Lists
# ---------------------------


class VIEW3D_UL_jewelcraft_weighting_set(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.jewelcraft
        mainrow = layout.row(align=True)

        row = mainrow.row(align=True)
        row.scale_x = 0.8
        row.prop(item, "enabled", text="")

        row = mainrow.row(align=True)
        row.active = item.enabled
        row.prop(item, "name", text="", emboss=False)

        if props.weighting_show_composition:
            sub = mainrow.row(align=True)
            sub.scale_x = 1.5
            sub.prop(item, "composition", text="", emboss=False)

        if props.weighting_show_density:
            sub = mainrow.row(align=True)
            sub.scale_x = 0.7
            sub.prop(item, "density", text="", emboss=False)


class VIEW3D_UL_jewelcraft_measurements(UIList):
    icons = {
        "DIMENSIONS": "SHADING_BBOX",
        "WEIGHT": "FILE_3D",
        "RING_SIZE": "MESH_CIRCLE",
    }

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.active = item.object is not None
        layout.prop(item, "name", text="", emboss=False, icon=self.icons.get(item.type, "BLANK1"))


class VIEW3D_UL_jewelcraft_asset_libs(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.split(factor=0.25, align=True)
        row.prop(item, "name", text="", emboss=False)
        row.prop(item, "path", text="", emboss=False)


class VIEW3D_UL_jewelcraft_asset_libs_select(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.label(text=item.name, translate=False)
        row.operator("wm.path_open", text="", icon="FILE_FOLDER", emboss=False).filepath = item.path


# Menus
# ---------------------------


def draw_jewelcraft_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_jewelcraft")


class VIEW3D_MT_jewelcraft(Setup, Menu):
    bl_label = "JewelCraft"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.jewelcraft_gem_add", icon_value=self.icon_get("GEM_ADD"))
        layout.operator("object.jewelcraft_gem_edit", icon_value=self.icon_get("GEM_EDIT"))
        layout.operator("object.jewelcraft_gem_recover", icon_value=self.icon_get("GEM_RECOVER"))
        layout.menu("VIEW3D_MT_jewelcraft_select_gem_by")
        layout.operator("wm.call_panel", text="Spacing Overlay", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_spacing_overlay"
        layout.separator()
        layout.operator("wm.call_panel", text="Assets", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_assets"
        layout.separator()
        layout.operator("object.jewelcraft_prongs_add", icon_value=self.icon_get("PRONGS"))
        layout.operator("object.jewelcraft_cutter_add", icon_value=self.icon_get("CUTTER"))
        layout.operator("object.jewelcraft_curve_distribute", icon_value=self.icon_get("DISTRIBUTE"))
        layout.operator("object.jewelcraft_curve_redistribute", icon_value=self.icon_get("REDISTRIBUTE"))
        layout.separator()
        layout.operator("object.jewelcraft_mirror", icon_value=self.icon_get("MIRROR"))
        layout.operator("object.jewelcraft_radial_instance", icon_value=self.icon_get("RADIAL"))
        layout.operator("object.jewelcraft_make_instance_face", icon_value=self.icon_get("INSTANCE_FACE"))
        layout.operator("object.jewelcraft_resize", icon_value=self.icon_get("RESIZE"))
        layout.operator("object.jewelcraft_lattice_project", icon_value=self.icon_get("LATTICE_PROJECT"))
        layout.operator("object.jewelcraft_lattice_profile", icon_value=self.icon_get("LATTICE_PROFILE"))
        layout.separator()
        layout.operator("curve.jewelcraft_size_curve_add", icon_value=self.icon_get("SIZE_CURVE"))
        layout.operator("object.jewelcraft_stretch_along_curve", icon_value=self.icon_get("STRETCH"))
        layout.operator("object.jewelcraft_move_over_under", text="Move Over", icon_value=self.icon_get("OVER"))
        layout.operator("object.jewelcraft_move_over_under", text="Move Under", icon_value=self.icon_get("UNDER")).under = True
        layout.operator("curve.jewelcraft_length_display", icon_value=self.icon_get("CURVE_LENGTH"))
        layout.separator()
        layout.operator("wm.call_panel", text="Weighting", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_weighting"
        layout.separator()
        layout.operator("wm.jewelcraft_design_report", text="Design Report")
        layout.operator("view3d.jewelcraft_gem_map")
        layout.operator("wm.call_panel", text="Measurement", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_measurement"


class VIEW3D_MT_jewelcraft_select_gem_by(Menu):
    bl_label = "Select Gems By..."
    bl_description = "Select gems by trait"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Size", text_ctxt="Dative").filter_size = True
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Stone", text_ctxt="Dative").filter_stone = True
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Cut", text_ctxt="Dative").filter_cut = True
        layout.separator()
        layout.operator("object.jewelcraft_select_gems_by_trait", text="Similar", text_ctxt="Dative").filter_similar = True
        layout.operator("object.jewelcraft_select_overlapping", text="Overlapping")
        layout.separator()
        layout.operator("object.jewelcraft_select_gems_by_trait", text="All")


class VIEW3D_MT_jewelcraft_asset_folder(Menu):
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.jewelcraft_asset_folder_create", icon="ADD")
        layout.operator("wm.jewelcraft_asset_folder_rename", text="Rename")


class VIEW3D_MT_jewelcraft_weighting_set(Menu):
    bl_label = ""

    def draw(self, context):
        library_folder = asset.get_weighting_lib_path()
        layout = self.layout
        layout.operator("wm.jewelcraft_weighting_set_add", icon="ADD")
        layout.operator("wm.jewelcraft_weighting_set_del", text="Remove", text_ctxt="*", icon="REMOVE")
        layout.operator("wm.jewelcraft_weighting_set_rename", text="Rename")
        layout.operator("wm.jewelcraft_weighting_set_replace")
        layout.operator("wm.jewelcraft_weighting_set_autoload_mark", icon="DOT")
        layout.separator()
        layout.operator("wm.path_open", text="Open Library Folder", icon="FILE_FOLDER").filepath = library_folder
        layout.separator()
        layout.operator("wm.jewelcraft_weighting_set_refresh", icon="FILE_REFRESH")


class VIEW3D_MT_jewelcraft_weighting_mats(Menu):
    bl_label = ""

    def draw(self, context):
        props = context.scene.jewelcraft
        layout = self.layout
        layout.operator("scene.jewelcraft_ul_clear", icon="X").prop = "weighting_materials"
        layout.separator()
        layout.prop(props, "weighting_show_composition")
        layout.prop(props, "weighting_show_density")


# Popovers
# ---------------------------


class VIEW3D_PT_jewelcraft_asset_libs(Panel):
    bl_label = "Libraries"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 8

    def draw(self, context):
        wm_props = context.window_manager.jewelcraft

        layout = self.layout

        row = layout.row()
        row.label(text="Libraries")

        sub = row.row()
        sub.alignment = "RIGHT"
        sub.operator("wm.jewelcraft_asset_ui_refresh", text="", icon="FILE_REFRESH", emboss=False)

        layout.template_list(
            "VIEW3D_UL_jewelcraft_asset_libs_select",
            "",
            wm_props.asset_libs,
            "coll",
            wm_props.asset_libs,
            "index",
            rows=wm_props.asset_libs.length() + 1,
        )


# Panels
# ---------------------------


class VIEW3D_PT_jewelcraft_update(Setup, Panel):
    bl_label = "Update"

    @classmethod
    def poll(cls, context):
        return mod_update.state.update_available

    def draw(self, context):
        mod_update.sidebar_ui(self, context)


class VIEW3D_PT_jewelcraft_warning(Setup, Panel):
    bl_label = "Warning"

    @classmethod
    def poll(cls, context):
        return unit.check(context) is not False

    def draw(self, context):
        layout = self.layout

        warning = unit.check(context)

        if warning is unit.WARN_SCALE:
            layout.label(text="Scene scale is not optimal", icon="ERROR")
        elif warning is unit.WARN_SYSTEM:
            layout.label(text="Unsupported unit system", icon="ERROR")

        col = layout.row()
        col.alignment = "CENTER"
        col.scale_y = 1.5
        col.operator("scene.jewelcraft_scene_units_set")


class VIEW3D_PT_jewelcraft_gems(Setup, Panel):
    bl_label = "Gems"

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"}

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("object.jewelcraft_gem_add", icon_value=self.icon_get("GEM_ADD"))
        row.operator("object.jewelcraft_gem_edit", text="", icon_value=self.icon_get("GEM_EDIT"))
        row.operator("object.jewelcraft_gem_recover", text="", icon_value=self.icon_get("GEM_RECOVER"))

        layout.menu("VIEW3D_MT_jewelcraft_select_gem_by")


class VIEW3D_PT_jewelcraft_spacing_overlay(Setup, Panel):
    bl_label = "Spacing Overlay"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "VIEW3D_PT_jewelcraft_gems"

    def draw_header(self, context):
        self.layout.prop(self.wm_props, "show_spacing", text="")

    def draw(self, context):
        props = context.scene.jewelcraft

        layout = self.layout

        if self.is_popover:
            row = layout.row(align=True)
            row.prop(self.wm_props, "show_spacing", text="")
            row.label(text="Spacing Overlay")

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.active = self.wm_props.show_spacing
        col.prop(props, "overlay_show_all")
        col.prop(props, "overlay_show_in_front")
        col.prop(props, "overlay_use_overrides")
        col.prop(props, "overlay_spacing", text="Spacing", text_ctxt="JewelCraft")

        col.separator()

        row = col.row(align=True)
        row.operator("object.jewelcraft_overlay_override_add")
        row.operator("object.jewelcraft_overlay_override_del")


class VIEW3D_PT_jewelcraft_assets(Setup, Panel):
    bl_label = "Assets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_ui_units_x = 20

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"}

    def draw(self, context):
        layout = self.layout

        if self.is_popover:
            layout.label(text="Assets")
            layout.separator()

        if not self.wm_props.asset_libs.values():
            layout.operator("wm.jewelcraft_goto_prefs", text="Set Library Folder", icon="ASSET_MANAGER").active_tab = "ASSET_MANAGER"
            return

        show_favs = self.wm_props.asset_show_favs

        row = layout.row(align=True)
        row.prop(self.wm_props, "asset_show_favs", text="", icon="SOLO_ON")
        row.separator()
        subrow = row.row(align=True)
        subrow.enabled = not show_favs
        sub = subrow.row(align=True)
        sub.scale_x = 1.28
        sub.popover(panel="VIEW3D_PT_jewelcraft_asset_libs", text="", icon="ASSET_MANAGER")

        if not self.wm_props.asset_folder:
            subrow.operator("wm.jewelcraft_asset_folder_create", icon="ADD")
            return

        subrow.prop(self.wm_props, "asset_folder", text="")
        subrow.menu("VIEW3D_MT_jewelcraft_asset_folder", icon="THREE_DOTS")

        flow = layout.grid_flow()
        sub = flow.row()
        sub.enabled = not show_favs
        sub.operator("wm.jewelcraft_asset_add", icon="ADD")
        flow.row().prop(self.wm_props, "asset_filter", text="", icon="VIEWZOOM")

        flow = layout.grid_flow(row_major=True, even_columns=True, even_rows=True, align=True)

        filter_name = self.wm_props.asset_filter.lower()
        show_name = self.prefs.asset_show_name

        if show_favs:
            assets = dynamic_list.favorites()
        else:
            assets = dynamic_list.assets(asset.get_asset_lib_path(), self.wm_props.asset_folder)

        if not assets:
            flow.box().label(text="Category is empty")
            return

        for asset_path, asset_name, asset_icon, is_fav in assets:

            if filter_name and filter_name not in asset_name.lower():
                continue

            box = flow.box().column(align=True)
            box.template_icon(icon_value=asset_icon, scale=self.prefs.asset_ui_preview_scale)
            if show_name:
                row = box.row()
                row.scale_x = 0.8
                row.label(text=asset_name, translate=False)

            split = box.split(align=True)
            split.scale_y = 0.9
            split.scale_x = 0.8
            split.operator("wm.jewelcraft_asset_import", text="", icon="IMPORT", emboss=False).filepath = asset_path
            split.operator("wm.jewelcraft_asset_menu", text="", icon="THREE_DOTS", emboss=False).filepath = asset_path
            if is_fav:
                split.operator("wm.jewelcraft_asset_favorite_del", text="", icon="SOLO_ON", emboss=False).filepath = asset_path
            else:
                split.operator("wm.jewelcraft_asset_favorite_add", text="", icon="SOLO_OFF", emboss=False).filepath = asset_path


class VIEW3D_PT_jewelcraft_jeweling(Setup, Panel):
    bl_label = "Jeweling"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.jewelcraft_prongs_add", text="Prongs", icon_value=self.icon_get("PRONGS"))
        col.operator("object.jewelcraft_cutter_add", text="Cutter", text_ctxt="JewelCraft", icon_value=self.icon_get("CUTTER"))

        row = layout.row(align=True)
        row.operator("object.jewelcraft_curve_distribute", icon_value=self.icon_get("DISTRIBUTE"))
        row.operator("object.jewelcraft_curve_redistribute", text="", icon_value=self.icon_get("REDISTRIBUTE"))


class VIEW3D_PT_jewelcraft_object(Setup, Panel):
    bl_label = "Object"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.jewelcraft_mirror", icon_value=self.icon_get("MIRROR"))
        row.operator("object.jewelcraft_radial_instance", text="Radial", text_ctxt="*", icon_value=self.icon_get("RADIAL"))
        col.operator("object.jewelcraft_make_instance_face", icon_value=self.icon_get("INSTANCE_FACE"))

        layout.operator("object.jewelcraft_resize", icon_value=self.icon_get("RESIZE"))

        col = layout.column(align=True)
        col.operator("object.jewelcraft_lattice_project", icon_value=self.icon_get("LATTICE_PROJECT"))
        col.operator("object.jewelcraft_lattice_profile", icon_value=self.icon_get("LATTICE_PROFILE"))


class VIEW3D_PT_jewelcraft_object_editmesh(Setup, Panel):
    bl_label = "Object"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.jewelcraft_lattice_profile", icon_value=self.icon_get("LATTICE_PROFILE"))


class VIEW3D_PT_jewelcraft_curve(Setup, Panel):
    bl_label = "Curve"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        layout.operator("curve.jewelcraft_size_curve_add", text="Size Curve", icon_value=self.icon_get("SIZE_CURVE"))

        row = layout.row()
        row.operator("object.jewelcraft_stretch_along_curve", text="Stretch", icon_value=self.icon_get("STRETCH"))
        sub = row.row(align=True)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.icon_get("OVER"))
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.icon_get("UNDER")).under = True

        layout.operator("curve.jewelcraft_length_display", icon_value=self.icon_get("CURVE_LENGTH"))


class VIEW3D_PT_jewelcraft_curve_editmesh(Setup, Panel):
    bl_label = "Curve"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.jewelcraft_stretch_along_curve", text="Stretch", icon_value=self.icon_get("STRETCH"))
        sub = row.row(align=True)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.icon_get("OVER"))
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=self.icon_get("UNDER")).under = True


class VIEW3D_PT_jewelcraft_weighting(Setup, Panel):
    bl_label = "Weighting"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        material_list = context.scene.jewelcraft.weighting_materials

        layout = self.layout

        if self.is_popover:
            layout.label(text="Weighting")
            layout.separator()

        row = layout.row(align=True)
        row.prop(self.wm_props, "weighting_set", text="")
        row.menu("VIEW3D_MT_jewelcraft_weighting_set", icon="THREE_DOTS")

        row = layout.row(align=True)
        row.operator("wm.jewelcraft_weighting_set_load")
        row.operator("wm.jewelcraft_weighting_set_load_append")

        layout.separator()

        row = layout.row()

        col = row.column()
        col.template_list(
            "VIEW3D_UL_jewelcraft_weighting_set",
            "",
            material_list,
            "coll",
            material_list,
            "index",
            rows=5,
        )

        col = row.column(align=True)
        col.operator("wm.jewelcraft_ul_materials_add", text="", icon="ADD")
        col.operator("scene.jewelcraft_ul_del", text="", icon="REMOVE").prop = "weighting_materials"
        col.separator()
        col.menu("VIEW3D_MT_jewelcraft_weighting_mats", icon="DOWNARROW_HLT")
        col.separator()
        op = col.operator("scene.jewelcraft_ul_move", text="", icon="TRIA_UP")
        op.prop = "weighting_materials"
        op.move_up = True
        col.operator("scene.jewelcraft_ul_move", text="", icon="TRIA_DOWN").prop = "weighting_materials"

        layout.operator("object.jewelcraft_weight_display", text="Calculate")


class VIEW3D_PT_jewelcraft_design_report(Setup, Panel):
    bl_label = "Design Report"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.jewelcraft_design_report", text="Design Report")
        layout.operator("view3d.jewelcraft_gem_map")


class VIEW3D_PT_jewelcraft_measurement(Setup, Panel):
    bl_label = "Measurement"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "VIEW3D_PT_jewelcraft_design_report"

    def draw(self, context):
        measures_list = context.scene.jewelcraft.measurements

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if self.is_popover:
            layout.label(text="Measurement")
            layout.separator()

        row = layout.row()

        col = row.column()
        col.template_list(
            "VIEW3D_UL_jewelcraft_measurements",
            "",
            measures_list,
            "coll",
            measures_list,
            "index",
            rows=3,
        )

        col = row.column(align=True)
        col.operator("wm.jewelcraft_ul_measurements_add", text="", icon="ADD")
        col.operator("scene.jewelcraft_ul_del", text="", icon="REMOVE").prop = "measurements"
        col.separator()
        op = col.operator("scene.jewelcraft_ul_move", text="", icon="TRIA_UP")
        op.prop = "measurements"
        op.move_up = True
        col.operator("scene.jewelcraft_ul_move", text="", icon="TRIA_DOWN").prop = "measurements"

        if measures_list.coll:
            item = measures_list.coll[measures_list.index]

            layout.prop(item, "object")

            if item.type == "DIMENSIONS":
                col = layout.column(heading="Dimensions", align=True)
                col.prop(item, "x")
                col.prop(item, "y")
                col.prop(item, "z")
            elif item.type == "WEIGHT":
                box = layout.box()
                row = box.row(align=True)
                row.label(text=item.material_name, translate=False)
                row.operator("wm.jewelcraft_ul_measurements_material_select", text="", icon="DOWNARROW_HLT", emboss=False)
            elif item.type == "RING_SIZE":
                layout.prop(item, "ring_size")
                layout.prop(item, "axis", expand=True)


# Preferences
# ---------------------------


def prefs_ui(self, context):
    wm_props = context.window_manager.jewelcraft
    active_tab = wm_props.prefs_active_tab

    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    split = layout.split(factor=0.25)
    col = split.column()
    col.use_property_split = False
    col.scale_y = 1.3
    col.prop(wm_props, "prefs_active_tab", expand=True)

    box = split.box()

    if active_tab == "ASSET_MANAGER":
        box.label(text="Libraries")
        col = box.column()
        row = col.row()

        col = row.column()
        col.template_list(
            "VIEW3D_UL_jewelcraft_asset_libs",
            "",
            wm_props.asset_libs,
            "coll",
            wm_props.asset_libs,
            "index",
            rows=4,
        )

        col = row.column(align=True)
        col.operator("wm.jewelcraft_ul_add", text="", icon="ADD").prop = "asset_libs"
        col.operator("wm.jewelcraft_ul_del", text="", icon="REMOVE").prop = "asset_libs"
        col.separator()
        op = col.operator("wm.jewelcraft_ul_move", text="", icon="TRIA_UP")
        op.prop = "asset_libs"
        op.move_up = True
        col.operator("wm.jewelcraft_ul_move", text="", icon="TRIA_DOWN").prop = "asset_libs"

        box.label(text="Assets")
        col = box.column()
        col.prop(self, "asset_preview_resolution")

        box.label(text="Interface")
        col = box.column()
        col.prop(self, "asset_popover_width")
        col.prop(self, "asset_ui_preview_scale")
        col.prop(self, "asset_show_name")

    elif active_tab == "WEIGHTING":
        col = box.column()
        col.prop(self, "weighting_hide_default_sets")
        col.prop(self, "weighting_set_lib_path")

    elif active_tab == "DESIGN_REPORT":
        col = box.column()
        col.prop(self, "design_report_lang")

        box.label(text="Gem Map")
        col = box.column(align=True)
        col.prop(self, "gem_map_width", text="Resolution X")
        col.prop(self, "gem_map_height", text="Y")

        box.label(text="Warnings")
        col = box.column()
        col.prop(self, "warn_hidden_gems")
        col.prop(self, "warn_gem_overlap")

    elif active_tab == "THEMES":
        box.label(text="Interface")
        col = box.column()
        col.prop(self, "theme_icon")

        box.label(text="Spacing Overlay")
        col = box.column()
        col.prop(self, "overlay_color")
        col.prop(self, "overlay_linewidth")
        col.prop(self, "view_font_size_distance")

        box.label(text="Viewport Options")
        col = box.column()
        col.prop(self, "view_font_size_option")

        box.label(text="Gem Map Font Size")
        col = box.column()
        col.prop(self, "view_font_size_report")
        col.prop(self, "view_font_size_gem_size")

        box.label(text="Materials")
        col = box.column()
        col.prop(self, "color_prongs")
        col.prop(self, "color_cutter")

    elif active_tab == "UPDATES":
        mod_update.prefs_ui(self, box)
