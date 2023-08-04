# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from pathlib import Path

import bpy
from bpy.types import PropertyGroup, AddonPreferences, Object, Collection
from bpy.props import (
    EnumProperty,
    BoolProperty,
    FloatProperty,
    StringProperty,
    PointerProperty,
    IntProperty,
    FloatVectorProperty,
    CollectionProperty,
)

from . import ui, var, mod_update
from .lib import data, dynamic_list, pathutils


# Update callbacks
# ------------------------------------------


_folder_cache = {}


def upd_folder_cache(self, context):
    wm_props = context.window_manager.jewelcraft
    _folder_cache[wm_props.asset_libs.index] = wm_props.asset_folder


def upd_folder_list(self, context):
    dynamic_list.asset_folders_refresh()

    # Recover previous folder
    wm_props = context.window_manager.jewelcraft
    folder = _folder_cache.get(wm_props.asset_libs.index)

    if folder is not None:
        try:
            wm_props.asset_folder = folder
            return
        except TypeError:
            _folder_cache.clear()

    wm_props.property_unset("asset_folder")


def upd_folder_list_serialize(self, context):
    upd_folder_list(self, context)
    data.asset_libs_serialize()


def upd_lib_name(self, context):
    self["name"] = Path(self.path).name or self.name
    upd_folder_list_serialize(self, context)


def upd_asset_popover_width(self, context):
    ui.VIEW3D_PT_jewelcraft_assets.bl_ui_units_x = self.asset_popover_width
    bpy.utils.unregister_class(ui.VIEW3D_PT_jewelcraft_assets)
    bpy.utils.register_class(ui.VIEW3D_PT_jewelcraft_assets)


def upd_spacing_overlay(self, context):
    from .lib.view3d_lib import spacing_overlay
    spacing_overlay.handler_toggle(self, context)


def upd_material_list_rename(self, context):
    if not self.name:
        self["name"] = self.name_orig
        return

    if self.name == self.name_orig:
        return

    path = pathutils.get_weighting_list_filepath(self.name_orig)
    path_new = pathutils.get_weighting_list_filepath(self.name)

    if not path.exists():
        dynamic_list.weighting_lib_refresh()
        return

    path.rename(path_new)
    self.name_orig = self.name


# Custom properties
# ------------------------------------------


class ListProperty:
    index: IntProperty()

    def add(self):
        item = self.coll.add()
        self.index = self.length() - 1
        return item

    def remove(self):
        if self.coll:
            self.coll.remove(self.index)
            index_last = max(0, self.length() - 1)

            if self.index > index_last:
                self.index = index_last

    def clear(self):
        self.coll.clear()

    def move(self, move_up: bool):
        if self.length() < 2:
            return

        if move_up:
            index_new = self.index - 1
        else:
            index_new = self.index + 1

        if 0 <= index_new < self.length():
            self.coll.move(self.index, index_new)
            self.index = index_new

    def values(self):
        return self.coll.values()

    def active_item(self):
        return self.coll[self.index]

    def length(self):
        return len(self.coll)


# Collection properties


class MaterialCollection(PropertyGroup):
    enabled: BoolProperty(description="Enable material for weighting display", default=True)
    name: StringProperty(default="Untitled")
    composition: StringProperty(default="Unknown")
    density: FloatProperty(description="Density g/cm³", default=0.01, min=0.01, step=1, precision=2)


class MaterialListCollection(PropertyGroup):
    name: StringProperty(name="Click to rename", update=upd_material_list_rename)
    name_orig: StringProperty()
    default: BoolProperty()
    builtin: BoolProperty()

    @property
    def load_id(self):
        if self.builtin:
            return "BUILTIN/" + self.name
        return self.name


class MeasurementCollection(PropertyGroup):
    name: StringProperty(name="Name", default="Untitled")
    collection: PointerProperty(name="Collection", type=Collection)
    object: PointerProperty(name="Object", type=Object)
    type: EnumProperty(
        items=(
            ("RING_SIZE", "", ""),
            ("WEIGHT", "", ""),
            ("DIMENSIONS", "", ""),
            ("METADATA", "", ""),
        ),
    )
    datablock_type: EnumProperty(
        items=(
            ("OBJECT", "", ""),
            ("COLLECTION", "", ""),
        ),
    )
    ring_size: EnumProperty(
        name="Format",
        items=(
            ("DIA", "Diameter", ""),
            ("CIR", "Circumference", ""),
            ("US", "USA", ""),
            ("UK", "Britain", ""),
            ("CH", "Swiss", ""),
            ("JP", "Japan", ""),
        ),
    )
    axis: EnumProperty(
        name="Axis",
        items=(
            ("0", "X", ""),
            ("1", "Y", ""),
            ("2", "Z", ""),
        ),
    )
    x: BoolProperty(name="X")
    y: BoolProperty(name="Y")
    z: BoolProperty(name="Z")
    material_name: StringProperty()
    material_density: FloatProperty()
    value: StringProperty()


class Metadata(PropertyGroup):
    name: StringProperty(default="...", update=data.report_metadata_serialize)
    value: StringProperty(default="...", update=data.report_metadata_serialize)


class AssetLibCollection(PropertyGroup):
    name: StringProperty(default="Untitled", update=upd_folder_list_serialize)
    path: StringProperty(default="/", subtype="DIR_PATH", update=upd_lib_name)


class SizeCollection(PropertyGroup):
    size: FloatProperty(name="Size", default=1.0, min=0.0001, step=10, unit="LENGTH")
    qty: IntProperty(name="Qty", default=1, min=1)


# List properties


class MaterialList(ListProperty, PropertyGroup):
    coll: CollectionProperty(type=MaterialCollection)


class MeasurementList(ListProperty, PropertyGroup):
    coll: CollectionProperty(type=MeasurementCollection)


class MetadataList(ListProperty, PropertyGroup):
    coll: CollectionProperty(type=Metadata)


class AssetLibList(ListProperty, PropertyGroup):
    index: IntProperty(update=upd_folder_list)
    coll: CollectionProperty(type=AssetLibCollection)


class SizeList(ListProperty, PropertyGroup):
    coll: CollectionProperty(type=SizeCollection)

    def add(self):
        item = self.coll.add()

        if self.length() > 1:
            item.size = self.coll[self.index].size

            index_curr = self.length() - 1
            index_new = self.index + 1

            if index_curr != index_new:
                self.coll.move(index_curr, index_new)

            self.index = index_new
        else:
            self.index = self.length() - 1

        return item


# Common properties


class ReportLangEnum:
    report_lang: EnumProperty(
        name="Report Language",
        items=(
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
            ("ar_EG", "Arabic (ﺔﻴﺑﺮﻌﻟﺍ)", ""),
            ("en_US", "English (English)", ""),
            ("es", "Spanish (Español)", ""),
            ("fr_FR", "French (Français)", ""),
            ("it_IT", "Italian (Italiano)", ""),
            ("ru_RU", "Russian (Русский)", ""),
            ("zh_CN", "Simplified Chinese (简体中文)", ""),
            ("zh_TW", "Traditional Chinese (繁體中文)", ""),
        ),
    )


# Preferences
# ------------------------------------------


class Preferences(ReportLangEnum, mod_update.Preferences, AddonPreferences):
    bl_idname = __package__

    # Asset
    # ------------------------

    asset_preview_resolution: IntProperty(
        name="Preview Resolution",
        description="Asset preview image size when creating new assets",
        default=256,
        subtype="PIXEL",
    )
    asset_popover_width: IntProperty(
        name="Popover Width",
        description="Assets popover width",
        default=20,
        min=0,
        update=upd_asset_popover_width,
    )
    asset_ui_preview_scale: FloatProperty(
        name="Preview Scale",
        description="Asset preview scale in sidebar",
        default=3.0,
        min=1.0,
        step=1,
    )
    asset_show_name: BoolProperty(
        name="Show Asset Name",
        description="Show asset name in sidebar",
    )

    # Weighting
    # ------------------------

    weighting_hide_builtin_lists: BoolProperty(
        name="Hide Built-in Material Lists",
        description="Hide built-in material lists from library",
        update=dynamic_list.weighting_lib_refresh,
    )
    weighting_lib_path: StringProperty(
        name="Library Folder",
        description="Custom library folder path",
        default=str(var.WEIGHTING_LIB_USER_DIR),
        subtype="DIR_PATH",
        update=dynamic_list.weighting_lib_refresh,
    )
    weighting_default_list: StringProperty(default="BUILTIN/Precious")

    # Design Report
    # ------------------------

    report_use_preview: BoolProperty(
        name="Preview",
        description="Include viewport preview image in report",
        default=True,
    )
    report_preview_resolution: IntProperty(
        name="Preview Resolution",
        default=512,
        subtype="PIXEL",
    )
    report_use_metadata: BoolProperty(
        name="Metadata",
        description="Include metadata in report",
        default=True,
    )
    gem_map_fontsize_table: IntProperty(
        name="Gem Table",
        default=19,
        min=1,
    )
    gem_map_fontsize_gem_size: IntProperty(
        name="Gem Size",
        default=18,
        min=1,
    )

    # Overlays
    # ------------------------

    overlay_color: FloatVectorProperty(
        name="Color",
        default=(0.9, 0.9, 0.9, 1.0),
        size=4,
        min=0.0,
        soft_max=1.0,
        subtype="COLOR",
    )
    overlay_linewidth: FloatProperty(
        name="Line Width",
        default=1.2,
        min=1.0,
        soft_max=5.0,
        subtype="PIXEL",
    )
    overlay_fontsize_distance: IntProperty(
        name="Font Size",
        default=16,
        min=1,
    )

    # Themes
    # ------------------------

    color_prongs: FloatVectorProperty(
        name="Prongs",
        default=(0.8, 0.8, 0.8, 1.0),
        size=4,
        min=0.0,
        soft_max=1.0,
        subtype="COLOR",
    )
    color_cutter: FloatVectorProperty(
        name="Cutter",
        default=(0.8, 0.8, 0.8, 1.0),
        size=4,
        min=0.0,
        soft_max=1.0,
        subtype="COLOR",
    )

    def draw(self, context):
        ui.prefs_ui(self, context)


# Window manager properties
# ------------------------------------------


class WmProperties(PropertyGroup):
    prefs_active_tab: EnumProperty(
        items=(
            ("ASSET_MANAGER", "Asset Manager", ""),
            ("DESIGN_REPORT", "Design Report", ""),
            ("WEIGHTING", "Weighting", ""),
            ("THEMES", "Themes", ""),
            ("UPDATES", "Updates", ""),
        ),
    )
    show_spacing: BoolProperty(
        name="Spacing Overlay",
        description="Show distance to nearby gems",
        update=upd_spacing_overlay,
    )
    asset_folder: EnumProperty(
        name="Category",
        description="Asset category",
        items=dynamic_list.asset_folders,
        update=upd_folder_cache,
    )
    asset_filter: StringProperty(
        name="Filter",
        description="Filter by name",
    )
    weighting_lists: CollectionProperty(type=MaterialListCollection)
    asset_menu_ui_lock: BoolProperty()
    asset_show_favs: BoolProperty(name="Favorites")
    asset_libs: PointerProperty(type=AssetLibList)
    sizes: PointerProperty(type=SizeList)
    report_metadata: PointerProperty(type=MetadataList)


# Scene properties
# ------------------------------------------


class SceneProperties(PropertyGroup):
    weighting_materials: PointerProperty(type=MaterialList)
    weighting_show_composition: BoolProperty(
        name="Show Composition",
        description="Display material composition in the list",
    )
    weighting_show_density: BoolProperty(
        name="Show Density",
        description="Display material density in the list",
    )
    measurements: PointerProperty(type=MeasurementList)
    overlay_show_all: BoolProperty(
        name="Show All",
        description="Show spacing guide for all visible gems",
    )
    overlay_show_in_front: BoolProperty(
        name="In Front",
        description="Draw overlay in front of objects",
    )
    overlay_use_overrides: BoolProperty(
        name="Overrides",
        description="Use object defined overlay settings",
        default=True,
    )
    overlay_spacing: FloatProperty(
        name="Spacing",
        default=0.2,
        min=0.0,
        step=1,
        precision=2,
        unit="LENGTH",
    )
