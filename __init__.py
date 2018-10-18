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


bl_info = {
    "name": "JewelCraft",
    "author": "Mikhail Rachinskiy",
    "version": (2, 2, 0),
    "blender": (2, 79, 0),
    "location": "3D View > Tool Shelf",
    "description": "Jewelry design toolkit.",
    "wiki_url": "https://github.com/mrachinskiy/jewelcraft#readme",
    "tracker_url": "https://github.com/mrachinskiy/jewelcraft/issues",
    "category": "Object",
}


if "bpy" in locals():
    import importlib

    for entry in os.scandir(var.ADDON_DIR):

        if entry.is_file() and entry.name.endswith(".py") and not entry.name.startswith("__"):
            module = os.path.splitext(entry.name)[0]
            importlib.reload(eval(module))

        elif entry.is_dir() and not entry.name.startswith((".", "__")) and not entry.name.endswith("updater"):

            for subentry in os.scandir(entry.path):

                if subentry.name.endswith(".py"):
                    module = "{}.{}".format(entry.name, os.path.splitext(subentry.name)[0])
                    importlib.reload(eval(module))
else:
    import os

    import bpy
    import bpy.utils.previews
    from bpy.props import PointerProperty

    from . import var, ui, translations, preferences, dynamic_lists, addon_updater_ops
    from .lib import widgets
    from .op_cutter import cutter_op
    from .op_prongs import prongs_op
    from .op_scatter import scatter_op
    from .op_product_report import product_report_op
    from .ops_asset import asset_ops, folder_ops
    from .ops_curve import curve_ops
    from .ops_gem import gem_ops, gem_select_ops
    from .ops_object import object_ops
    from .ops_utils import search_ops, widgets_ops
    from .ops_weighting import weighting_list_ops, weighting_set_ops, weighting_op


classes = (
    preferences.JewelCraftMaterialsCollection,
    preferences.JewelCraftMaterialsList,
    preferences.JewelCraftPreferences,
    preferences.JewelCraftPropertiesWm,
    preferences.JewelCraftPropertiesScene,
    ui.VIEW3D_UL_jewelcraft_weighting_set,
    ui.VIEW3D_MT_jewelcraft_select_gem_by,
    ui.VIEW3D_MT_jewelcraft_folder,
    ui.VIEW3D_MT_jewelcraft_asset,
    ui.VIEW3D_MT_jewelcraft_weighting_set,
    ui.VIEW3D_MT_jewelcraft_weighting_list,
    ui.VIEW3D_MT_jewelcraft_product_report,
    ui.VIEW3D_PT_jewelcraft_update,
    ui.VIEW3D_PT_jewelcraft_gems,
    ui.VIEW3D_PT_jewelcraft_widgets,
    ui.VIEW3D_PT_jewelcraft_assets,
    ui.VIEW3D_PT_jewelcraft_jeweling,
    ui.VIEW3D_PT_jewelcraft_object,
    ui.VIEW3D_PT_jewelcraft_curve,
    ui.VIEW3D_PT_jewelcraft_curve_editmesh,
    ui.VIEW3D_PT_jewelcraft_weighting,
    ui.VIEW3D_PT_jewelcraft_product_report,
    prongs_op.OBJECT_OT_jewelcraft_prongs_add,
    cutter_op.OBJECT_OT_jewelcraft_cutter_add,
    scatter_op.OBJECT_OT_jewelcraft_curve_scatter,
    scatter_op.OBJECT_OT_jewelcraft_curve_redistribute,
    product_report_op.WM_OT_jewelcraft_product_report,
    gem_ops.OBJECT_OT_jewelcraft_gem_add,
    gem_ops.OBJECT_OT_jewelcraft_gem_edit,
    gem_ops.OBJECT_OT_jewelcraft_gem_id_add,
    gem_ops.OBJECT_OT_jewelcraft_gem_id_convert_deprecated,
    gem_select_ops.OBJECT_OT_jewelcraft_select_gems_by_trait,
    gem_select_ops.OBJECT_OT_jewelcraft_select_doubles,
    folder_ops.WM_OT_jewelcraft_asset_folder_create,
    folder_ops.WM_OT_jewelcraft_asset_folder_rename,
    folder_ops.WM_OT_jewelcraft_asset_ui_refresh,
    asset_ops.WM_OT_jewelcraft_asset_add_to_library,
    asset_ops.WM_OT_jewelcraft_asset_remove_from_library,
    asset_ops.WM_OT_jewelcraft_asset_rename,
    asset_ops.WM_OT_jewelcraft_asset_replace,
    asset_ops.WM_OT_jewelcraft_asset_preview_replace,
    asset_ops.WM_OT_jewelcraft_asset_import,
    curve_ops.CURVE_OT_jewelcraft_size_curve_add,
    curve_ops.CURVE_OT_jewelcraft_length_display,
    curve_ops.OBJECT_OT_jewelcraft_stretch_along_curve,
    curve_ops.OBJECT_OT_jewelcraft_move_over_under,
    object_ops.OBJECT_OT_jewelcraft_mirror,
    object_ops.OBJECT_OT_jewelcraft_make_dupliface,
    object_ops.OBJECT_OT_jewelcraft_lattice_project,
    object_ops.OBJECT_OT_jewelcraft_lattice_profile,
    object_ops.OBJECT_OT_jewelcraft_resize,
    search_ops.VIEW3D_OT_jewelcraft_search_stone,
    search_ops.VIEW3D_OT_jewelcraft_search_asset,
    widgets_ops.OBJECT_OT_jewelcraft_widgets_overrides_set,
    widgets_ops.OBJECT_OT_jewelcraft_widgets_overrides_del,
    weighting_list_ops.WM_OT_jewelcraft_ul_item_add,
    weighting_list_ops.WM_OT_jewelcraft_ul_item_del,
    weighting_list_ops.WM_OT_jewelcraft_ul_item_clear,
    weighting_list_ops.WM_OT_jewelcraft_ul_item_move,
    weighting_op.OBJECT_OT_jewelcraft_weight_display,
    weighting_set_ops.WM_OT_jewelcraft_weighting_set_add,
    weighting_set_ops.WM_OT_jewelcraft_weighting_set_replace,
    weighting_set_ops.WM_OT_jewelcraft_weighting_set_del,
    weighting_set_ops.WM_OT_jewelcraft_weighting_set_load,
    weighting_set_ops.WM_OT_jewelcraft_weighting_set_load_append,
    weighting_set_ops.WM_OT_jewelcraft_weighting_set_rename,
    weighting_set_ops.WM_OT_jewelcraft_weighting_set_refresh,
)


def register():
    addon_updater_ops.register(bl_info)

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.jewelcraft = PointerProperty(type=preferences.JewelCraftPropertiesWm)
    bpy.types.Scene.jewelcraft = PointerProperty(type=preferences.JewelCraftPropertiesScene)

    bpy.app.translations.register(__name__, translations.DICTIONARY)

    # Previews
    # ---------------------------

    pcoll = bpy.utils.previews.new()

    for entry in os.scandir(var.ICONS_DIR):

        if entry.name.endswith(".png"):
            name = os.path.splitext(entry.name)[0]
            pcoll.load(name, entry.path, "IMAGE")

    var.preview_collections["icons"] = pcoll


def unregister():
    addon_updater_ops.unregister()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.jewelcraft
    del bpy.types.Scene.jewelcraft

    bpy.app.translations.unregister(__name__)

    # Previews
    # ---------------------------

    for pcoll in var.preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    var.preview_collections.clear()
    dynamic_lists._cache.clear()

    # Widgets
    # ---------------------------

    widgets.handler_del()


if __name__ == "__main__":
    register()
