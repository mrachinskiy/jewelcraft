# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from bpy.types import Panel, Menu, UIList

from . import mod_update
from .lib import dynamic_list, pathutils, unit
from .lib.previewlib import icon, icon_menu


# Lists
# ---------------------------


class VIEW3D_UL_jewelcraft_material_list(UIList):

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
        "METADATA": "DOT",
    }

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        is_meta = item.type == "METADATA"
        layout.alert = not is_meta and item.collection is None and item.object is None
        layout.prop(item, "name", text="", emboss=False, icon=self.icons.get(item.type, "BLANK1"))
        if is_meta:
            layout.prop(item, "value", text="", emboss=False)


class VIEW3D_UL_jewelcraft_metadata(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.split(factor=0.25, align=True)
        row.prop(item, "name", text="", emboss=False)
        row.prop(item, "value", text="", emboss=False)


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


class VIEW3D_UL_jewelcraft_sizes(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.alignment = "RIGHT"
        sub.active = False
        sub.label(text="Qty")
        row.prop(item, "qty", text="", emboss=False)

        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.alignment = "RIGHT"
        sub.active = False
        sub.label(text="Size")
        row.prop(item, "size", text="", emboss=False)


# Menus
# ---------------------------


def draw_jewelcraft_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_jewelcraft")


class VIEW3D_MT_jewelcraft(Menu):
    bl_label = "JewelCraft"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("object.jewelcraft_gem_add", icon_value=icon_menu("GEM_ADD"))
        layout.operator("object.jewelcraft_gem_edit", icon_value=icon_menu("GEM_EDIT"))
        layout.operator("object.jewelcraft_gem_recover", icon_value=icon_menu("GEM_RECOVER"))
        layout.menu("VIEW3D_MT_jewelcraft_select_gem_by")
        layout.operator("wm.call_panel", text="Spacing Overlay", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_spacing_overlay"
        layout.operator("wm.call_panel", text="Gem Map Overlay", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_gem_map_overlay"
        layout.separator()
        layout.operator("wm.call_panel", text="Assets", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_assets"
        layout.separator()
        layout.operator("object.jewelcraft_prongs_add", icon_value=icon_menu("PRONGS"))
        layout.operator("object.jewelcraft_cutter_add", icon_value=icon_menu("CUTTER"))
        layout.operator("object.jewelcraft_microprong_cutter_add", icon_value=icon_menu("MICROPRONG_CUTTER"))
        layout.operator("object.jewelcraft_curve_distribute", icon_value=icon_menu("DISTRIBUTE"))
        layout.operator("object.jewelcraft_curve_redistribute", icon_value=icon_menu("REDISTRIBUTE"))
        layout.separator()
        layout.operator("object.jewelcraft_mirror", icon_value=icon_menu("MIRROR"))
        layout.operator("object.jewelcraft_radial_instance", icon_value=icon_menu("RADIAL"))
        layout.operator("object.jewelcraft_make_instance_face", icon_value=icon_menu("INSTANCE_FACE"))
        layout.operator("object.jewelcraft_resize", icon_value=icon_menu("RESIZE"))
        layout.operator("object.jewelcraft_lattice_project", icon_value=icon_menu("LATTICE_PROJECT"))
        layout.operator("object.jewelcraft_lattice_profile", icon_value=icon_menu("LATTICE_PROFILE"))
        layout.separator()
        layout.operator("curve.jewelcraft_size_curve_add", icon_value=icon_menu("SIZE_CURVE"))
        layout.operator("object.jewelcraft_stretch_along_curve", icon_value=icon_menu("STRETCH"))
        layout.operator("object.jewelcraft_move_over_under", text="Move Over", icon_value=icon_menu("OVER"))
        layout.operator("object.jewelcraft_move_over_under", text="Move Under", icon_value=icon_menu("UNDER")).under = True
        layout.operator("curve.jewelcraft_length_display", icon_value=icon_menu("CURVE_LENGTH"))
        layout.separator()
        layout.operator("wm.call_panel", text="Weighting", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_weighting"
        layout.separator()
        layout.operator("wm.jewelcraft_design_report", text="Design Report")
        layout.operator("view3d.jewelcraft_gem_map")
        layout.operator("wm.call_panel", text="Measurement", text_ctxt="*", icon="WINDOW").name = "VIEW3D_PT_jewelcraft_measurement"


class VIEW3D_MT_jewelcraft_select_gem_by(Menu):
    bl_label = "Select by Trait"
    bl_description = "Select gems by trait"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("object.jewelcraft_gem_select_by_trait", text="Size", text_ctxt="*").filter_size = True
        layout.operator("object.jewelcraft_gem_select_by_trait", text="Stone", text_ctxt="*").filter_stone = True
        layout.operator("object.jewelcraft_gem_select_by_trait", text="Cut", text_ctxt="Jewelry").filter_cut = True
        layout.separator()
        layout.operator("object.jewelcraft_gem_select_by_trait", text="Similar").filter_similar = True
        layout.operator("object.jewelcraft_gem_select_overlapping", text="Overlapping")
        layout.separator()
        layout.operator("object.jewelcraft_gem_select_by_trait", text="All")


class VIEW3D_MT_jewelcraft_asset_folder(Menu):
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.jewelcraft_asset_folder_create", icon="ADD")
        layout.operator("wm.jewelcraft_asset_folder_rename", text="Rename")


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


class VIEW3D_PT_jewelcraft_weighting_lib(Panel):
    bl_label = "Library"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 15

    def draw(self, context):
        lib = context.window_manager.jewelcraft.weighting_lists
        lib_path = str(pathutils.get_weighting_lib_path())

        if not lib:
            dynamic_list.weighting_lib()

        layout = self.layout

        row = layout.row()
        row.label(text="Library")

        sub = row.row(align=True)
        sub.emboss = "NONE"
        sub.alignment = "RIGHT"
        sub.scale_x = 1.1
        sub.operator("wm.jewelcraft_weighting_ui_refresh", text="", icon="FILE_REFRESH")
        sub.operator("wm.path_open", text="", icon="FILE_FOLDER").filepath = lib_path

        layout.separator()

        for item in lib:
            row = layout.row(align=True)
            row.emboss = "NONE"
            row.operator("wm.jewelcraft_weighting_list_set_default", text="", icon="RADIOBUT_ON" if item.default else "RADIOBUT_OFF").load_id = item.load_id
            row.separator()
            row.label(text=item.name, text_ctxt="Jewelry", translate=item.builtin)

            sub = row.row(align=True)
            sub.scale_x = 1.1
            sub.operator("wm.jewelcraft_weighting_list_import", text="", icon="IMPORT").load_id = item.load_id

            sub2 = sub.row(align=True)
            sub2.enabled = not item.builtin
            sub2.operator("wm.jewelcraft_weighting_list_save_as", text="", icon="FILE_TICK").list_name = item.name
            sub2.operator("wm.jewelcraft_weighting_list_del", text="", icon="TRASH").list_name = item.name

        row = layout.row()
        row.emboss = "NONE"
        row.alignment = "RIGHT"
        row.scale_x = 1.1
        row.operator("wm.jewelcraft_weighting_list_save", text="", icon="ADD")


# Panels
# ---------------------------


class SidebarSetup:
    bl_category = "JewelCraft"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


class VIEW3D_PT_jewelcraft_update(mod_update.Sidebar, SidebarSetup, Panel):
    bl_label = "Update"


class VIEW3D_PT_jewelcraft_warning(SidebarSetup, Panel):
    bl_label = "Warning"

    @classmethod
    def poll(cls, context):
        return unit.check() is not unit.WARN_NONE

    def draw_header(self, context):
        self.layout.alert = True
        self.layout.label(icon="ERROR")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alignment = "CENTER"

        warning = unit.check()

        if warning is unit.WARN_SCALE:
            row.label(text="Scene scale is not optimal")
        elif warning is unit.WARN_SYSTEM:
            row.label(text="Unsupported unit system")

        row = layout.row()
        row.alignment = "CENTER"
        row.scale_y = 1.5
        row.operator("scene.jewelcraft_scene_units_set")


class VIEW3D_PT_jewelcraft_gems(SidebarSetup, Panel):
    bl_label = "Gems"

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"}

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("object.jewelcraft_gem_add", icon_value=icon("GEM_ADD"))
        row.operator("object.jewelcraft_gem_edit", text="", icon_value=icon("GEM_EDIT"))
        row.operator("object.jewelcraft_gem_recover", text="", icon_value=icon("GEM_RECOVER"))

        layout.menu("VIEW3D_MT_jewelcraft_select_gem_by")


class VIEW3D_PT_jewelcraft_spacing_overlay(SidebarSetup, Panel):
    bl_label = "Spacing Overlay"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "VIEW3D_PT_jewelcraft_gems"

    def draw_header(self, context):
        wm_props = context.window_manager.jewelcraft
        self.layout.prop(wm_props, "show_spacing", text="")

    def draw(self, context):
        props = context.scene.jewelcraft
        wm_props = context.window_manager.jewelcraft

        layout = self.layout

        if self.is_popover:
            row = layout.row(align=True)
            row.prop(wm_props, "show_spacing", text="")
            row.label(text="Spacing Overlay")

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.active = wm_props.show_spacing
        col.prop(props, "overlay_show_all")
        col.prop(props, "overlay_show_in_front")
        col.prop(props, "overlay_use_overrides")
        col.prop(props, "overlay_spacing", text="Spacing", text_ctxt="Jewelry")

        col.separator()

        row = col.row(align=True)
        row.operator("object.jewelcraft_overlay_override_add")
        row.operator("object.jewelcraft_overlay_override_del")


class VIEW3D_PT_jewelcraft_gem_map_overlay(SidebarSetup, Panel):
    bl_label = "Gem Map Overlay"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "VIEW3D_PT_jewelcraft_gems"

    def draw_header(self, context):
        wm_props = context.window_manager.jewelcraft
        self.layout.prop(wm_props, "show_gem_map", text="")

    def draw(self, context):
        props = context.scene.jewelcraft
        wm_props = context.window_manager.jewelcraft

        layout = self.layout

        if self.is_popover:
            row = layout.row(align=True)
            row.prop(wm_props, "show_gem_map", text="")
            row.label(text="Gem Map Overlay")

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.active = wm_props.show_gem_map
        col.prop(props, "overlay_gem_map_show_all")
        col.prop(props, "overlay_gem_map_show_in_front")
        col.prop(props, "overlay_gem_map_opacity")


class VIEW3D_PT_jewelcraft_assets(SidebarSetup, Panel):
    bl_label = "Assets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_ui_units_x = 20

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "EDIT_MESH"}

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        wm_props = context.window_manager.jewelcraft

        layout = self.layout

        if self.is_popover:
            layout.label(text="Assets")
            layout.separator()

        if not wm_props.asset_libs.values():
            layout.operator("wm.jewelcraft_goto_prefs", text="Set Library Folder", icon="ASSET_MANAGER").active_tab = "ASSET_MANAGER"
            return

        show_favs = wm_props.asset_show_favs

        row = layout.row(align=True)
        row.prop(wm_props, "asset_show_favs", text="", icon="SOLO_ON")
        row.separator()
        subrow = row.row(align=True)
        subrow.enabled = not show_favs
        sub = subrow.row(align=True)
        sub.scale_x = 1.28
        sub.popover(panel="VIEW3D_PT_jewelcraft_asset_libs", text="", icon="ASSET_MANAGER")

        if not wm_props.asset_folder:
            subrow.operator("wm.jewelcraft_asset_folder_create", icon="ADD")
            return

        subrow.prop(wm_props, "asset_folder", text="")
        subrow.menu("VIEW3D_MT_jewelcraft_asset_folder", icon="THREE_DOTS")

        flow = layout.grid_flow()
        sub = flow.row()
        sub.enabled = not show_favs
        sub.operator("wm.jewelcraft_asset_add", icon="ADD")
        flow.row().prop(wm_props, "asset_filter", text="", icon="VIEWZOOM")

        flow = layout.grid_flow(row_major=True, even_columns=True, even_rows=True, align=True)

        filter_name = wm_props.asset_filter.lower()
        show_name = prefs.asset_show_name

        if show_favs:
            assets = dynamic_list.favorites()
        else:
            assets = dynamic_list.assets(pathutils.get_asset_lib_path(), wm_props.asset_folder)

        if not assets:
            flow.box().label(text="Category is empty")
            return

        for asset_path, asset_name, asset_icon, is_fav in assets:

            if filter_name and filter_name not in asset_name.lower():
                continue

            box = flow.box().column(align=True)
            box.template_icon(icon_value=asset_icon, scale=prefs.asset_ui_preview_scale)
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


class VIEW3D_PT_jewelcraft_jeweling(SidebarSetup, Panel):
    bl_label = "Jeweling"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.jewelcraft_prongs_add", text="Prongs", icon_value=icon("PRONGS"))
        col.operator("object.jewelcraft_cutter_add", text="Cutter", text_ctxt="Jewelry", icon_value=icon("CUTTER"))
        col.operator("object.jewelcraft_microprong_cutter_add", text="Microprong Cutter", icon_value=icon("MICROPRONG_CUTTER"))

        row = layout.row(align=True)
        row.operator("object.jewelcraft_curve_distribute", icon_value=icon("DISTRIBUTE"))
        row.operator("object.jewelcraft_curve_redistribute", text="", icon_value=icon("REDISTRIBUTE"))


class VIEW3D_PT_jewelcraft_object(SidebarSetup, Panel):
    bl_label = "Object"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.jewelcraft_mirror", icon_value=icon("MIRROR"))
        row.operator("object.jewelcraft_radial_instance", text="Radial", text_ctxt="*", icon_value=icon("RADIAL"))
        col.operator("object.jewelcraft_make_instance_face", icon_value=icon("INSTANCE_FACE"))

        layout.operator("object.jewelcraft_resize", icon_value=icon("RESIZE"))

        col = layout.column(align=True)
        col.operator("object.jewelcraft_lattice_project", icon_value=icon("LATTICE_PROJECT"))
        col.operator("object.jewelcraft_lattice_profile", icon_value=icon("LATTICE_PROFILE"))


class VIEW3D_PT_jewelcraft_object_editmesh(SidebarSetup, Panel):
    bl_label = "Object"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.jewelcraft_lattice_profile", icon_value=icon("LATTICE_PROFILE"))


class VIEW3D_PT_jewelcraft_curve(SidebarSetup, Panel):
    bl_label = "Curve"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        layout.operator("curve.jewelcraft_size_curve_add", text="Size Curve", icon_value=icon("SIZE_CURVE"))

        row = layout.row()
        row.operator("object.jewelcraft_stretch_along_curve", text="Stretch", icon_value=icon("STRETCH"))
        sub = row.row(align=True)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=icon("OVER"))
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=icon("UNDER")).under = True

        layout.operator("curve.jewelcraft_length_display", icon_value=icon("CURVE_LENGTH"))


class VIEW3D_PT_jewelcraft_curve_editmesh(SidebarSetup, Panel):
    bl_label = "Curve"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.jewelcraft_stretch_along_curve", text="Stretch", icon_value=icon("STRETCH"))
        sub = row.row(align=True)
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=icon("OVER"))
        sub.operator("object.jewelcraft_move_over_under", text="", icon_value=icon("UNDER")).under = True


class VIEW3D_PT_jewelcraft_weighting(SidebarSetup, Panel):
    bl_label = "Weighting"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        material_list = context.scene.jewelcraft.weighting_materials

        layout = self.layout

        if self.is_popover:
            layout.label(text="Weighting")
            layout.separator()

        layout.popover(panel="VIEW3D_PT_jewelcraft_weighting_lib", icon="ASSET_MANAGER")

        row = layout.row()

        col = row.column()
        col.template_list(
            "VIEW3D_UL_jewelcraft_material_list",
            "",
            material_list,
            "coll",
            material_list,
            "index",
            rows=5,
        )

        col = row.column(align=True)
        col.operator("wm.jewelcraft_ul_material_add", text="", icon="ADD")
        col.operator("scene.jewelcraft_ul_del", text="", icon="REMOVE").prop = "weighting_materials"
        col.separator()
        col.menu("VIEW3D_MT_jewelcraft_weighting_mats", icon="DOWNARROW_HLT")
        col.separator()
        op = col.operator("scene.jewelcraft_ul_move", text="", icon="TRIA_UP")
        op.prop = "weighting_materials"
        op.move_up = True
        col.operator("scene.jewelcraft_ul_move", text="", icon="TRIA_DOWN").prop = "weighting_materials"

        layout.operator("object.jewelcraft_weight_display", text="Calculate")


class VIEW3D_PT_jewelcraft_design_report(SidebarSetup, Panel):
    bl_label = "Design Report"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.jewelcraft_design_report", text="Design Report")
        layout.operator("view3d.jewelcraft_gem_map")


class VIEW3D_PT_jewelcraft_measurement(SidebarSetup, Panel):
    bl_label = "Additional Entries"
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

            if item.type == "METADATA":
                return

            col = layout.column()

            if item.datablock_type == "OBJECT":
                col.alert = item.object is None
                col.prop(item, "object")
            else:
                col.alert = item.collection is None
                col.prop(item, "collection")

            if item.type == "WEIGHT":
                box = layout.box()
                row = box.row()
                row.label(text=item.material_name, translate=False)
                row.operator("wm.jewelcraft_ul_measurements_material_select", text="", icon="DOWNARROW_HLT", emboss=False)
            elif item.type == "DIMENSIONS":
                col = layout.column(heading="Dimensions", align=True)
                col.prop(item, "x")
                col.prop(item, "y")
                col.prop(item, "z")
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

    elif active_tab == "DESIGN_REPORT":
        box.prop(self, "report_lang")

        box.label(text="Design Report")
        row = box.row(heading="Preview")
        row.prop(self, "report_use_preview", text="")
        sub = row.row()
        sub.enabled = self.report_use_preview
        sub.prop(self, "report_preview_resolution", text="")

        row = box.row()
        row.use_property_split = False
        row.prop(self, "report_use_metadata", text="Metadata")

        col = box.column()
        col.active = self.report_use_metadata
        row = col.row()

        col = row.column()
        col.template_list(
            "VIEW3D_UL_jewelcraft_metadata",
            "",
            wm_props.report_metadata,
            "coll",
            wm_props.report_metadata,
            "index",
            rows=4,
        )

        col = row.column(align=True)
        col.operator("wm.jewelcraft_ul_add", text="", icon="ADD").prop = "report_metadata"
        col.operator("wm.jewelcraft_ul_del", text="", icon="REMOVE").prop = "report_metadata"
        col.separator()
        op = col.operator("wm.jewelcraft_ul_move", text="", icon="TRIA_UP")
        op.prop = "report_metadata"
        op.move_up = True
        col.operator("wm.jewelcraft_ul_move", text="", icon="TRIA_DOWN").prop = "report_metadata"

        box.label(text="Gem Map Font Size")
        col = box.column()
        col.prop(self, "gem_map_fontsize_table")
        col.prop(self, "gem_map_fontsize_gem_size")

    elif active_tab == "WEIGHTING":
        col = box.column()
        col.prop(self, "weighting_hide_builtin_lists")
        col.prop(self, "weighting_lib_path")

    elif active_tab == "THEMES":
        box.label(text="Spacing Overlay")
        col = box.column()
        col.prop(self, "overlay_color")
        col.prop(self, "overlay_linewidth")
        col.prop(self, "overlay_fontsize_distance")

        box.label(text="Materials")
        col = box.column()
        col.prop(self, "color_prongs")
        col.prop(self, "color_cutter")

    elif active_tab == "UPDATES":
        mod_update.prefs_ui(self, box)
