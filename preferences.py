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
    enabled = BoolProperty(description="Enable material for weighting and product report", default=True)
    name = StringProperty(default="Untitled")
    composition = StringProperty(default="Unknown")
    density = FloatProperty(description="Density g/cm³", default=0.01, min=0.01, step=1, precision=2)


class JewelCraftMaterialsList(PropertyGroup):
    index = IntProperty()
    coll = CollectionProperty(type=JewelCraftMaterialsCollection)

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
    split = layout.split(align=True, percentage=ratio)
    split.alignment = "RIGHT"
    split.label(label)
    split.prop(data, prop, text="")


def update_asset_refresh(self, context):
    dynamic_lists.asset_folder_list_refresh()
    dynamic_lists.asset_list_refresh(hard=True)


class JewelCraftPreferences(AddonPreferences):
    bl_idname = __package__

    active_section = EnumProperty(
        items=(
            ("ASSET_MANAGER",  "Asset Manager",  ""),
            ("WEIGHTING",      "Weighting",      ""),
            ("PRODUCT_REPORT", "Product Report", ""),
            ("THEMES",         "Themes",         ""),
            ("UPDATER",        "Update",         ""),
        ),
        options={"SKIP_SAVE"},
    )

    asset_name_from_obj = BoolProperty(name="Asset name from active object", description="Use active object name when creating new asset")
    use_custom_asset_dir = BoolProperty(name="Use custom library folder", description="Set custom asset library folder, if disabled the default library folder will be used", update=update_asset_refresh)
    custom_asset_dir = StringProperty(name="Library Folder Path", description="Custom library folder path", subtype="DIR_PATH", update=update_asset_refresh)
    display_asset_name = BoolProperty(name="Display asset name", description="Display asset name in Tool Shelf")

    weighting_hide_default_sets = BoolProperty(name="Hide default sets", description="Hide default JewelCraft sets from weighting sets menu", update=dynamic_lists.weighting_set_refresh)
    weighting_set_use_custom_dir = BoolProperty(name="Use custom library folder", description="Set custom asset library folder, if disabled the default library folder will be used", update=dynamic_lists.weighting_set_refresh)
    weighting_set_custom_dir = StringProperty(name="Library Folder Path", description="Custom library folder path", subtype="DIR_PATH", update=dynamic_lists.weighting_set_refresh)
    weighting_materials = PointerProperty(type=JewelCraftMaterialsList)
    weighting_list_show_composition = BoolProperty(name="Show composition", description="Display material composition in the list")
    weighting_list_show_density = BoolProperty(name="Show density", description="Display material density in the list")

    product_report_lang = EnumProperty(
        name="Report Language",
        description="Product report language",
        items=(
            ("ru_RU", "Russian (Русский)", ""),
            ("en_US", "English (English)", ""),
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
        ),
        default="AUTO",
    )
    product_report_display = BoolProperty(name="Display in a new window", description="Display product report in new window", default=True)
    product_report_save = BoolProperty(name="Save to file", description="Save product report to file in project folder", default=True)

    widget_selection_only = BoolProperty(name="Selection only", description="Draw widgets only for selected objects")
    widget_use_overrides = BoolProperty(name="Use overrides", description="Use object defined widget overrides", default=True)
    widget_overrides_only = BoolProperty(name="Overrides only", description="Display only object defined widget overrides")
    widget_x_ray = BoolProperty(name="X-Ray", description="Draw widgets in front of objects")
    widget_color = FloatVectorProperty(name="Widget Color", default=(1.0, 1.0, 1.0, 1.0), size=4, min=0.0, soft_max=1.0, subtype="COLOR")
    widget_linewidth = IntProperty(name="Line Width", default=2, min=1, soft_max=5, subtype="PIXEL")
    widget_distance = FloatProperty(name="Distance", default=0.2, min=0.0, step=1, precision=2, unit="LENGTH")

    color_prongs = FloatVectorProperty(name="Prongs", default=(0.8, 0.8, 0.8), min=0.0, soft_max=1.0, subtype="COLOR")
    color_cutter = FloatVectorProperty(name="Cutter", default=(0.8, 0.8, 0.8), min=0.0, soft_max=1.0, subtype="COLOR")

    update_auto_check = BoolProperty(name="Automatically check for updates", description="Automatically check for updates with specified interval", default=True)
    update_interval = EnumProperty(
        name="Interval",
        description="Interval",
        items=(
            ("1", "Once a day", ""),
            ("7", "Once a week", ""),
            ("30", "Once a month", ""),
        ),
        default="7",
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.row().prop(self, "active_section", expand=True)

        col.separator()

        if self.active_section == "ASSET_MANAGER":
            col = layout.column()
            property_split(self, col, "Asset name from active object", "asset_name_from_obj", ratio=1 / 3)
            property_split(self, col, "Display asset name", "display_asset_name", ratio=1 / 3)
            property_split(self, col, "Use custom library folder", "use_custom_asset_dir", ratio=1 / 3)
            sub = col.row()
            sub.active = self.use_custom_asset_dir
            property_split(self, sub, "Library Folder Path", "custom_asset_dir", ratio=1 / 3)

        elif self.active_section == "WEIGHTING":
            col = layout.column()
            property_split(self, col, "Hide default sets", "weighting_hide_default_sets", ratio=1 / 3)
            property_split(self, col, "Use custom library folder", "weighting_set_use_custom_dir", ratio=1 / 3)
            sub = col.row()
            sub.active = self.weighting_set_use_custom_dir
            property_split(self, sub, "Library Folder Path", "weighting_set_custom_dir", ratio=1 / 3)

            layout.separator()

            col = layout.column()
            property_split(self, col, "Show composition", "weighting_list_show_composition", ratio=1 / 3)
            property_split(self, col, "Show density", "weighting_list_show_density", ratio=1 / 3)

            split = col.split(percentage=1 / 3)
            row = split.row()
            row.alignment = "RIGHT"
            row.label("Materials list")

            row = split.row()
            col = row.column()
            col.template_list("VIEW3D_UL_jewelcraft_weighting_set", "", self.weighting_materials, "coll", self.weighting_materials, "index")
            col = row.column(align=True)
            col.operator("wm.jewelcraft_ul_item_add", text="", icon="ZOOMIN")
            col.operator("wm.jewelcraft_ul_item_del", text="", icon="ZOOMOUT")
            col.separator()
            col.operator("wm.jewelcraft_ul_item_move", text="", icon="TRIA_UP").move_up = True
            col.operator("wm.jewelcraft_ul_item_move", text="", icon="TRIA_DOWN")

        elif self.active_section == "PRODUCT_REPORT":
            col = layout.column()
            property_split(self, col, "Display in a new window", "product_report_display", ratio=1 / 3)
            property_split(self, col, "Save to file", "product_report_save", ratio=1 / 3)
            property_split(self, col, "Report Language", "product_report_lang", ratio=1 / 3)

        elif self.active_section == "THEMES":
            layout.label("Widgets")
            split = layout.split(percentage=0.5)
            col = split.column()
            property_split(self, col, "Selection only", "widget_selection_only")
            property_split(self, col, "Use overrides", "widget_use_overrides")
            sub = col.column()
            sub.active = self.widget_use_overrides
            property_split(self, sub, "Overrides only", "widget_overrides_only")
            property_split(self, col, "X-Ray", "widget_x_ray")
            property_split(self, col, "Widget Color", "widget_color")
            property_split(self, col, "Line Width", "widget_linewidth")
            property_split(self, col, "Distance", "widget_distance")

            layout.separator()

            layout.label("Materials")
            split = layout.split(percentage=0.5)
            col = split.column()
            property_split(self, col, "Prongs", "color_prongs")
            property_split(self, col, "Cutter", "color_cutter")

        elif self.active_section == "UPDATER":
            addon_updater_ops.update_settings_ui(self, context)


# Window manager properties
# ------------------------------------------


def update_asset_list(self, context):
    dynamic_lists.asset_list_refresh()
    item_id = dynamic_lists.assets(self, context)[0][0]

    if item_id:
        self.asset_list = item_id


class JewelCraftPropertiesWm(PropertyGroup):
    gem_cut = EnumProperty(items=dynamic_lists.cuts)
    gem_stone = EnumProperty(name="Stone", description="Stone", items=dynamic_lists.stones)

    widget_toggle = BoolProperty(description="Enable widgets drawing", update=widgets.handler_toggle)

    asset_folder = EnumProperty(name="Category", description="Asset category", items=dynamic_lists.asset_folders, update=update_asset_list)
    asset_list = EnumProperty(items=dynamic_lists.assets)

    weighting_set = EnumProperty(name="Weighting Set", description="Set of materials for weighting", items=dynamic_lists.weighting_set)


# Scene properties
# ------------------------------------------


class JewelCraftPropertiesScene(PropertyGroup):
    product_report_ob_size = PointerProperty(type=Object, name="Size", description="Object for ring inner diameter reference")
    product_report_ob_shank = PointerProperty(type=Object, name="Shank", description="Object for shank width and height reference")
    product_report_ob_dim = PointerProperty(type=Object, name="Dimensions", description="Object for dimensions reference")
    product_report_ob_weight = PointerProperty(type=Object, name="Weight", description="Object for weight reference")
