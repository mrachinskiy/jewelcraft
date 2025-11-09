# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Callable
from pathlib import Path

import bpy
from bpy.app.translations import pgettext_iface as _
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty,
                       FloatProperty, FloatVectorProperty, IntProperty,
                       PointerProperty, StringProperty)
from bpy.types import AddonPreferences, Collection, Object, PropertyGroup

from . import ui, var
from .lib import dynamic_list


# Update callbacks
# ------------------------------------------


_upd_lock = False


def _serialize_colors_interval():
    global _upd_lock

    bpy.context.window_manager.jewelcraft.gem_colors.serialize()
    _upd_lock = False


def upd_serialize_colors(self, context):
    global _upd_lock

    if self.builtin:
        return

    if not _upd_lock:
        bpy.app.timers.register(_serialize_colors_interval, first_interval=2)
        _upd_lock = True


def upd_color_name(self, context=None):
    wm_props = context.window_manager.jewelcraft
    color = wm_props.gem_colors.active_item()
    wm_props["gem_color"] = color.color
    wm_props["gem_color_name"] = _(color.name)


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
    bpy.context.window_manager.jewelcraft.asset_libs.serialize()


def upd_lib_name(self, context):
    self["name"] = Path(self.path).name or self.name
    upd_folder_list_serialize(self, context)


def upd_asset_popover_width(self, context):
    ui.VIEW3D_PT_jewelcraft_assets.bl_ui_units_x = self.asset_popover_width
    bpy.utils.unregister_class(ui.VIEW3D_PT_jewelcraft_assets)
    bpy.utils.register_class(ui.VIEW3D_PT_jewelcraft_assets)


def upd_spacing_overlay(self, context):
    from .lib import overlays
    overlays.spacing.handler_toggle(self, context)


def upd_gem_map_overlay(self, context):
    from .lib import overlays
    overlays.gem_map.handler_toggle(self, context)


def upd_material_list_rename(self, context):
    if not self.name:
        self["name"] = self.name_orig
        return

    if self.name == self.name_orig:
        return

    weighting_list_path = context.scene.jewelcraft.weighting_materials.serialize_path
    path = weighting_list_path(self.name_orig)
    path_new = weighting_list_path(self.name)

    if not path.exists():
        dynamic_list.weighting_lib_refresh()
        return

    path.rename(path_new)
    self.name_orig = self.name


# Collection properties
# ------------------------------------------


class GemColor(PropertyGroup):
    name: StringProperty(name="Click to rename", default="Colorless", update=upd_serialize_colors)
    color: FloatVectorProperty(
        name="Color",
        default=(1.0, 1.0, 1.0),
        size=3,
        min=0.0,
        max=1.0,
        subtype="COLOR",
        update=upd_serialize_colors,
    )
    builtin: BoolProperty()

    def asdict(self) -> dict[str, str]:
        from .lib import colorlib

        return {
            "name": self.name,
            "color": colorlib.rbg_to_hex(self.color),
        }


class WeightingMaterial(PropertyGroup):
    enabled: BoolProperty(description="Enable material for weighting display", default=True)
    name: StringProperty(default="Untitled")
    composition: StringProperty(default="Unknown")
    density: FloatProperty(description="Density g/cm³", default=0.01, min=0.01, step=1, precision=2)

    def asdict(self) -> dict[str, str | float]:
        return {
            "name": self.name,
            "composition": self.composition,
            "density": round(self.density, 2),
        }


class WeightingListItem(PropertyGroup):
    name: StringProperty(name="Click to rename", update=upd_material_list_rename)
    name_orig: StringProperty()
    default: BoolProperty()
    builtin: BoolProperty()

    @property
    def load_id(self):
        if self.builtin:
            return "BUILTIN/" + self.name
        return self.name


class Measurement(PropertyGroup):
    name: StringProperty(name="Name", default="Untitled")
    collection: PointerProperty(name="Collection", type=Collection)
    object: PointerProperty(name="Object", type=Object)
    type: EnumProperty(
        items=(
            ("RING_SIZE", "", ""),
            ("WEIGHT", "", ""),
            ("DIMENSIONS", "", ""),
            ("METADATA", "", ""),
            ("VOLUME", "", ""),
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
            ("DIAMETER", "Diameter", ""),
            ("CIRCUMFERENCE", "Circumference", ""),
            ("US", "USA", ""),
            ("UK", "Britain", ""),
            ("CH", "Swiss", ""),
            ("JP", "Japan", ""),
            ("HK", "Hong Kong", ""),
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

    def asdict(self):
        d = {
            "type": self.type,
            "name": self.name,
        }

        if self.type != "METADATA":
            d["datablock_type"] = self.datablock_type

        if self.type == "METADATA":
            d["value"] = self.value
        elif self.type == "WEIGHT":
            d["value"] = round(self.material_density, 2)
        elif self.type == "DIMENSIONS":
            d["value"] = self.x, self.y, self.z
        elif self.type == "RING_SIZE":
            d["value"] = self.ring_size, "XYZ"[int(self.axis)]

        return d

    def fromdict(self, item):
        d = {
            "type": "METADATA",
            "name": "Untitled",
            "datablock_type": "OBJECT",
            "value": "",
        }
        d |= item

        self.type = d["type"]
        self.name = d["name"]

        if self.type != "METADATA":
            self.datablock_type = d["datablock_type"]

        if self.type == "METADATA":
            self.value = d["value"]
        elif self.type == "WEIGHT":
            self.material_name = d["name"]
            self.material_density = d["value"]
        elif self.type == "DIMENSIONS":
            self.x, self.y, self.z = d["value"]
        elif self.type == "RING_SIZE":
            try:
                fmt, axis = d["value"]
                self.ring_size = fmt
                self.axis = {"X": "0", "Y": "1", "Z": "2"}.get(axis, "0")
            except TypeError:
                pass


class AssetLib(PropertyGroup):
    name: StringProperty(default="Untitled", update=upd_folder_list_serialize)
    path: StringProperty(default="/", subtype="DIR_PATH", update=upd_lib_name)

    def asdict(self) -> dict[str, str]:
        return dict(self)


class SizeItem(PropertyGroup):
    size: FloatProperty(name="Size", default=1.0, min=0.0001, step=10, unit="LENGTH")
    qty: IntProperty(name="Qty", default=1, min=1)


# List properties
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

    def serialize(self, filepath: Path | None = None) -> None:
        import json

        data = [item.asdict() for item in self.values() if not getattr(item, "builtin", False)]

        if not filepath:
            filepath = self.serialize_path()

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _deserialize(self, filepath: Path, fmt: Callable = lambda k, v: v, is_builtin=False) -> None:
        import json

        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

            for data_item in data:
                item = self.add()
                for k, v in data_item.items():
                    item[k] = fmt(k, v)
                if is_builtin:
                    item["builtin"] = True

            self["index"] = 0

    def serialize_path(self) -> Path:
        ...


class GemColorsList(ListProperty, PropertyGroup):
    index: IntProperty(update=upd_color_name)
    coll: CollectionProperty(type=GemColor)

    def set_active_by_name(self, name: str) -> tuple[int, int, int]:
        for i, item in enumerate(self.coll):
            if item.name == name:
                self["index"] = i
                return item.color

    def deserialize(self) -> None:
        if self.coll:
            return

        def _hex_to_rgb(k, v):
            from .lib import colorlib
            if k == "color":
                return colorlib.hex_to_rgb(v)
            return v

        self.clear()
        self._deserialize(var.GEM_ASSET_DIR / "colors.json", fmt=_hex_to_rgb, is_builtin=True)

        if (filepath := self.serialize_path()).exists():
            self._deserialize(filepath, fmt=_hex_to_rgb)

    def serialize_path(self) -> Path:
        prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
        return Path(prefs.config_dir) / "gem_colors.json"


class WeightingMaterialsList(ListProperty, PropertyGroup):
    coll: CollectionProperty(type=WeightingMaterial)

    def deserialize(self, name: str) -> None:

        def _translate_item_name(k, v):
            if k == "name":
                return _(v)
            return v

        if name.startswith("BUILTIN/"):
            filepath = var.WEIGHTING_LISTS_DIR / (name[len("BUILTIN/"):] + ".json")
            self._deserialize(filepath, fmt=_translate_item_name)
        else:
            filepath = bpy.context.scene.jewelcraft.weighting_materials.serialize_path(name)
            self._deserialize(filepath)

    def serialize_path(self, name: str = "") -> Path:
        prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
        path = Path(prefs.config_dir) / "weighting_library"
        if name:
            return path / f"{name}.json"
        return path


class MeasurementsList(ListProperty, PropertyGroup):
    coll: CollectionProperty(type=Measurement)

    def deserialize(self, is_on_load=False, load_factory=False) -> None:
        import json

        if is_on_load and self.coll:
            return

        if load_factory or not (filepath := self.serialize_path()).exists():
            filepath = var.ENTRIES_FILEPATH

        with open(filepath, "r", encoding="utf-8") as file:
            self.clear()
            data = json.load(file)

            for data_item in data:
                item = self.add()
                item.fromdict(data_item)

            self["index"] = 0

    def serialize_path(self) -> Path:
        prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
        return Path(prefs.config_dir) / "report_entries.json"


class AssetLibsList(ListProperty, PropertyGroup):
    index: IntProperty(update=upd_folder_list)
    coll: CollectionProperty(type=AssetLib)

    def path(self) -> Path:
        return Path(self.active_item().path)

    def deserialize(self, is_on_load=False) -> None:
        filepath = self.serialize_path()

        if is_on_load and self.coll:
            return

        if filepath.exists():
            self.clear()
            self._deserialize(filepath)

    def serialize_path(self) -> Path:
        prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
        return Path(prefs.config_dir) / "asset_libraries.json"


class SizeList(ListProperty, PropertyGroup):
    coll: CollectionProperty(type=SizeItem)

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

    def serialize(self) -> None:
        return


# Common properties
# ------------------------------------------


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


class Preferences(ReportLangEnum, AddonPreferences):
    bl_idname = __package__

    # Config
    # ------------------------

    config_dir: StringProperty(
        name="Configuration",
        description="Configuration folder for certain add-on preferences, like asset favorites, gem colors and similar",
        default=bpy.utils.extension_path_user(var.ADDON_ID),
        subtype="DIR_PATH",
    )

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

    weighting_default_list: StringProperty(default="BUILTIN/Precious")

    # Design Report
    # ------------------------

    file_format: EnumProperty(
        name="Format",
        items=(
            ("HTML", "HTML", ""),
            ("JSON", "JSON", ""),
        ),
    )
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

    def asset_favs_filepath(self) -> Path:
        return Path(self.config_dir) / "asset_favorites.json"


# Window manager properties
# ------------------------------------------


class WmProperties(PropertyGroup):
    prefs_show_general: BoolProperty(name="General")
    prefs_show_gems: BoolProperty(name="Gem Colors")
    prefs_show_asset_manager: BoolProperty(name="Asset Manager")
    prefs_show_design_report: BoolProperty(name="Design Report")
    prefs_show_themes: BoolProperty(name="Themes")
    gem_colors: PointerProperty(type=GemColorsList)
    gem_color: FloatVectorProperty(
        name="Color",
        default=(1.0, 1.0, 1.0),
        size=3,
        min=0.0,
        max=1.0,
        subtype="COLOR",
    )
    gem_color_name: StringProperty(name="Color Name")
    show_spacing: BoolProperty(
        name="Spacing Overlay",
        description="Show distance to nearby gems",
        update=upd_spacing_overlay,
    )
    show_gem_map: BoolProperty(
        name="Gem Map",
        description="Show color-coded gem map",
        update=upd_gem_map_overlay,
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
    weighting_lists: CollectionProperty(type=WeightingListItem)
    asset_menu_ui_lock: BoolProperty()
    asset_show_favs: BoolProperty(name="Favorites")
    asset_libs: PointerProperty(type=AssetLibsList)
    sizes: PointerProperty(type=SizeList)


# Scene properties
# ------------------------------------------


class SceneProperties(PropertyGroup):
    weighting_materials: PointerProperty(type=WeightingMaterialsList)
    weighting_show_composition: BoolProperty(
        name="Show Composition",
        description="Show material composition",
    )
    weighting_show_density: BoolProperty(
        name="Show Density",
        description="Show material density",
    )
    measurements: PointerProperty(type=MeasurementsList)
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
    overlay_gem_map_show_all: BoolProperty(
        name="Show All",
        description="Show for all visible gems",
    )
    overlay_gem_map_show_in_front: BoolProperty(
        name="In Front",
        description="Draw overlay in front of objects",
    )
    overlay_gem_map_use_material_color: BoolProperty(
        name="Material Color",
        description="Use gem material color for gem map",
    )
    overlay_gem_map_opacity: FloatProperty(
        name="Opacity",
        default=0.8,
        min=0.0,
        max=1.0,
        precision=2,
        subtype="FACTOR",
    )
