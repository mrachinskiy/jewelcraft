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


from bpy.types import PropertyGroup, AddonPreferences, Object
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

from . import dynamic_lists, addon_updater_ops
from .lib import widgets


# Custom properties
# ------------------------------------------


class JewelCraftMaterialsCollection(PropertyGroup):
    enabled: BoolProperty(description="Enable material for weighting and product report", default=True)
    name: StringProperty(default="Untitled")
    composition: StringProperty(default="Unknown")
    density: FloatProperty(description="Density g/cm³", default=0.01, min=0.01, step=1, precision=2)


class JewelCraftMaterialsList(PropertyGroup):
    index: IntProperty()
    coll: CollectionProperty(type=JewelCraftMaterialsCollection)

    def add(self):
        item = self.coll.add()
        self.index = len(self.coll) - 1
        return item

    def remove(self):
        if self.coll:
            self.coll.remove(self.index)
            index_last = max(0, len(self.coll) - 1)

            if self.index > index_last:
                self.index = index_last

    def clear(self):
        self.coll.clear()

    def move(self, move_up):

        if len(self.coll) < 2:
            return

        if move_up:
            index_new = self.index - 1
        else:
            index_new = self.index + 1

        if 0 <= index_new < len(self.coll):
            self.coll.move(self.index, index_new)
            self.index = index_new

    def values(self):
        return self.coll.values()


# Add-on preferences
# ------------------------------------------


def property_split(data, layout, label, prop, ratio=0.0):
    split = layout.split(align=True, factor=ratio)
    split.alignment = "RIGHT"
    split.label(text=label)
    split.prop(data, prop, text="")


def update_asset_refresh(self, context):
    dynamic_lists.asset_folder_list_refresh()
    dynamic_lists.asset_list_refresh(hard=True)


class JewelCraftPreferences(AddonPreferences):
    bl_idname = __package__

    active_section: EnumProperty(
        items=(
            ("ASSET_MANAGER",  "Asset Manager",  ""),
            ("WEIGHTING",      "Weighting",      ""),
            ("PRODUCT_REPORT", "Product Report", ""),
            ("THEMES",         "Themes",         ""),
            ("UPDATER",        "Update",         ""),
        ),
    )
    update_auto_check: BoolProperty(
        name="Automatically check for updates",
        description="Automatically check for updates with specified interval",
        default=True,
    )
    update_interval: EnumProperty(
        name="Interval",
        description="Interval",
        items=(
            ("1", "Once a day", ""),
            ("7", "Once a week", ""),
            ("30", "Once a month", ""),
        ),
        default="7",
    )
    asset_name_from_obj: BoolProperty(
        name="Asset name from active object",
        description="Use active object name when creating new asset",
    )
    use_custom_asset_dir: BoolProperty(
        name="Use custom library folder",
        description="Set custom asset library folder, if disabled the default library folder will be used",
        update=update_asset_refresh,
    )
    custom_asset_dir: StringProperty(
        name="Library Folder Path",
        description="Custom library folder path",
        subtype="DIR_PATH",
        update=update_asset_refresh,
    )
    display_asset_name: BoolProperty(
        name="Display asset name",
        description="Display asset name in Tool Shelf",
    )
    weighting_hide_default_sets: BoolProperty(
        name="Hide default sets",
        description="Hide default JewelCraft sets from weighting sets menu",
        update=dynamic_lists.weighting_set_refresh,
    )
    weighting_set_use_custom_dir: BoolProperty(
        name="Use custom library folder",
        description="Set custom asset library folder, if disabled the default library folder will be used",
        update=dynamic_lists.weighting_set_refresh,
    )
    weighting_set_custom_dir: StringProperty(
        name="Library Folder Path",
        description="Custom library folder path",
        subtype="DIR_PATH",
        update=dynamic_lists.weighting_set_refresh,
    )
    weighting_materials: PointerProperty(type=JewelCraftMaterialsList)
    weighting_list_show_composition: BoolProperty(
        name="Show composition",
        description="Display material composition in the list",
    )
    weighting_list_show_density: BoolProperty(
        name="Show density",
        description="Display material density in the list",
    )
    product_report_lang: EnumProperty(
        name="Report Language",
        description="Product report language",
        items=(
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
            ("en_US", "English (English)", ""),
            ("ru_RU", "Russian (Русский)", ""),
        ),
    )
    product_report_display: BoolProperty(
        name="Display in a new window",
        description="Display product report in new window",
        default=True,
    )
    product_report_save: BoolProperty(
        name="Save to file",
        description="Save product report to file in project folder",
        default=True,
    )
    product_report_use_hidden_gems: BoolProperty(
        name="Hidden gems",
        description="Show warning if there are hidden gem objects in the scene",
        default=True,
    )
    widget_selection_only: BoolProperty(
        name="Selection only",
        description="Draw widgets only for selected objects",
    )
    widget_use_overrides: BoolProperty(
        name="Use overrides",
        description="Use object defined widget overrides",
        default=True,
    )
    widget_overrides_only: BoolProperty(
        name="Overrides only",
        description="Display only object defined widget overrides",
    )
    widget_show_in_front: BoolProperty(
        name="In Front",
        description="Draw widgets in front of objects",
    )
    widget_color: FloatVectorProperty(
        name="Color",
        default=(0.9, 0.9, 0.9, 1.0),
        size=4,
        min=0.0,
        soft_max=1.0,
        subtype="COLOR",
    )
    widget_linewidth: IntProperty(
        name="Line Width",
        default=2,
        min=1,
        soft_max=5,
        subtype="PIXEL",
    )
    widget_distance: FloatProperty(
        name="Distance",
        default=0.2,
        min=0.0,
        step=1,
        precision=2,
        unit="LENGTH",
    )
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
    theme_icon: EnumProperty(
        name="Icons",
        items=(
            ("LIGHT", "Light", ""),
            ("DARK", "Dark", ""),
        ),
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        split = layout.split(factor=0.25)
        col = split.column()
        col.use_property_split = False
        col.scale_y = 1.3
        col.prop(self, "active_section", expand=True)

        box = split.box()

        if self.active_section == "ASSET_MANAGER":
            col = box.column()
            col.prop(self, "asset_name_from_obj")
            col.prop(self, "display_asset_name")
            col.prop(self, "use_custom_asset_dir")
            sub = col.row()
            sub.active = self.use_custom_asset_dir
            sub.prop(self, "custom_asset_dir")

        elif self.active_section == "WEIGHTING":
            col = box.column()
            col.prop(self, "weighting_hide_default_sets")
            col.prop(self, "weighting_set_use_custom_dir")
            sub = col.row()
            sub.active = self.weighting_set_use_custom_dir
            sub.prop(self, "weighting_set_custom_dir")

            box.label(text="Materials list")

            row = box.row()
            row.template_list(
                "VIEW3D_UL_jewelcraft_weighting_set",
                "",
                self.weighting_materials,
                "coll",
                self.weighting_materials,
                "index",
            )

            col = row.column(align=True)
            col.operator("wm.jewelcraft_ul_item_add", text="", icon="ADD")
            col.operator("wm.jewelcraft_ul_item_del", text="", icon="REMOVE")
            col.separator()
            col.operator("wm.jewelcraft_ul_item_move", text="", icon="TRIA_UP").move_up = True
            col.operator("wm.jewelcraft_ul_item_move", text="", icon="TRIA_DOWN")

            col = box.column()
            col.prop(self, "weighting_list_show_composition")
            col.prop(self, "weighting_list_show_density")

        elif self.active_section == "PRODUCT_REPORT":
            col = box.column()
            col.prop(self, "product_report_display")
            col.prop(self, "product_report_save")
            col.prop(self, "product_report_lang")

            box.label(text="Warnings")
            box.prop(self, "product_report_use_hidden_gems")

        elif self.active_section == "THEMES":
            box.label(text="Interface")
            col = box.column()
            col.prop(self, "theme_icon")

            box.label(text="Widgets")
            col = box.column()
            col.prop(self, "widget_selection_only")
            col.prop(self, "widget_use_overrides")
            sub = col.column()
            sub.active = self.widget_use_overrides
            sub.prop(self, "widget_overrides_only")
            col.prop(self, "widget_show_in_front")
            col.prop(self, "widget_color")
            col.prop(self, "widget_linewidth")
            col.prop(self, "widget_distance")

            box.label(text="Materials")
            col = box.column()
            col.prop(self, "color_prongs")
            col.prop(self, "color_cutter")

        elif self.active_section == "UPDATER":
            box.use_property_split = False
            addon_updater_ops.update_settings_ui(self, context, element=box)


# Window manager properties
# ------------------------------------------


def update_asset_list(self, context):
    dynamic_lists.asset_list_refresh()
    item_id = dynamic_lists.assets(self, context)[0][0]

    if item_id:
        self.asset_list = item_id


class JewelCraftPropertiesWm(PropertyGroup):
    gem_cut: EnumProperty(items=dynamic_lists.cuts)
    gem_stone: EnumProperty(name="Stone", description="Stone", items=dynamic_lists.stones)
    widget_toggle: BoolProperty(description="Enable widgets drawing", update=widgets.handler_toggle)
    asset_folder: EnumProperty(
        name="Category",
        description="Asset category",
        items=dynamic_lists.asset_folders,
        update=update_asset_list,
    )
    asset_list: EnumProperty(items=dynamic_lists.assets)
    weighting_set: EnumProperty(
        name="Weighting Set",
        description="Set of materials for weighting",
        items=dynamic_lists.weighting_set,
    )


# Scene properties
# ------------------------------------------


class JewelCraftPropertiesScene(PropertyGroup):
    product_report_ob_size: PointerProperty(
        type=Object,
        name="Size",
        description="Object for ring inner diameter reference",
    )
    product_report_ob_shank: PointerProperty(
        type=Object,
        name="Shank",
        description="Object for shank width and height reference",
    )
    product_report_ob_dim: PointerProperty(
        type=Object,
        name="Dimensions",
        description="Object for dimensions reference",
    )
    product_report_ob_weight: PointerProperty(
        type=Object,
        name="Weight",
        description="Object for weight reference",
    )
