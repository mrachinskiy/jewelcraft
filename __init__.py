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


bl_info = {
    "name": "JewelCraft",
    "author": "Mikhail Rachinskiy",
    "version": (2, 3, 5),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar",
    "description": "Jewelry design toolkit.",
    "wiki_url": "https://github.com/mrachinskiy/jewelcraft#readme",
    "tracker_url": "https://github.com/mrachinskiy/jewelcraft/issues",
    "category": "Object",
}


if "bpy" in locals():

    def walk(path, parent_dir=None):
        import importlib

        for entry in os.scandir(path):

            if entry.is_file() and entry.name.endswith(".py"):
                filename, _ = os.path.splitext(entry.name)
                is_init = filename == "__init__"

                if parent_dir:
                    module = parent_dir if is_init else f"{parent_dir}.{filename}"
                else:
                    if is_init:
                        continue
                    module = filename

                importlib.reload(eval(module))

            elif entry.is_dir() and not entry.name.startswith((".", "__")):
                dirname = f"{parent_dir}.{entry.name}" if parent_dir else entry.name
                walk(entry.path, parent_dir=dirname)

    walk(var.ADDON_DIR)
else:
    import os

    import bpy
    import bpy.utils.previews
    from bpy.props import PointerProperty

    from . import (
        var,
        ui,
        preferences,
        localization,
        mod_update,
        op_cutter,
        op_gem_map,
        op_product_report,
        op_prongs,
        op_scatter,
        ops_asset,
        ops_gem,
        ops_measurement,
        ops_object,
        ops_utils,
        ops_weighting,
    )
    from .lib import on_load


var.UPDATE_CURRENT_VERSION = bl_info["version"]

classes = (
    preferences.MeasurementCollection,
    preferences.MaterialCollection,
    preferences.MeasurementsList,
    preferences.MaterialsList,
    preferences.JewelCraftPreferences,
    preferences.WmProperties,
    preferences.SceneProperties,
    ui.VIEW3D_UL_jewelcraft_weighting_set,
    ui.VIEW3D_UL_jewelcraft_measurements,
    ui.VIEW3D_MT_jewelcraft_select_gem_by,
    ui.VIEW3D_MT_jewelcraft_folder,
    ui.VIEW3D_MT_jewelcraft_asset,
    ui.VIEW3D_MT_jewelcraft_weighting_set,
    ui.VIEW3D_MT_jewelcraft_weighting_list,
    ui.VIEW3D_PT_jewelcraft_update,
    ui.VIEW3D_PT_jewelcraft_warning,
    ui.VIEW3D_PT_jewelcraft_gems,
    ui.VIEW3D_PT_jewelcraft_widgets,
    ui.VIEW3D_PT_jewelcraft_assets,
    ui.VIEW3D_PT_jewelcraft_jeweling,
    ui.VIEW3D_PT_jewelcraft_object,
    ui.VIEW3D_PT_jewelcraft_curve,
    ui.VIEW3D_PT_jewelcraft_curve_editmesh,
    ui.VIEW3D_PT_jewelcraft_weighting,
    ui.VIEW3D_PT_jewelcraft_product_report,
    ui.VIEW3D_PT_jewelcraft_measurement,
    mod_update.WM_OT_update_check,
    mod_update.WM_OT_update_download,
    mod_update.WM_OT_update_whats_new,
    op_cutter.OBJECT_OT_cutter_add,
    op_gem_map.VIEW3D_OT_gem_map,
    op_product_report.WM_OT_product_report,
    op_prongs.OBJECT_OT_prongs_add,
    op_scatter.OBJECT_OT_curve_scatter,
    op_scatter.OBJECT_OT_curve_redistribute,
    ops_asset.WM_OT_asset_folder_create,
    ops_asset.WM_OT_asset_folder_rename,
    ops_asset.WM_OT_asset_ui_refresh,
    ops_asset.WM_OT_asset_add_to_library,
    ops_asset.WM_OT_asset_remove_from_library,
    ops_asset.WM_OT_asset_rename,
    ops_asset.WM_OT_asset_replace,
    ops_asset.WM_OT_asset_preview_replace,
    ops_asset.WM_OT_asset_import,
    ops_gem.OBJECT_OT_gem_add,
    ops_gem.OBJECT_OT_gem_edit,
    ops_gem.OBJECT_OT_gem_id_add,
    ops_gem.OBJECT_OT_gem_id_convert_deprecated,
    ops_gem.OBJECT_OT_select_gems_by_trait,
    ops_gem.OBJECT_OT_select_overlapping,
    ops_measurement.WM_OT_ul_measurements_add,
    ops_measurement.WM_OT_ul_measurements_material_select,
    ops_measurement.WM_OT_ul_measurements_del,
    ops_measurement.WM_OT_ul_measurements_move,
    ops_object.CURVE_OT_size_curve_add,
    ops_object.CURVE_OT_length_display,
    ops_object.OBJECT_OT_stretch_along_curve,
    ops_object.OBJECT_OT_move_over_under,
    ops_object.OBJECT_OT_mirror,
    ops_object.OBJECT_OT_radial_instance,
    ops_object.OBJECT_OT_make_instance_face,
    ops_object.OBJECT_OT_lattice_project,
    ops_object.OBJECT_OT_lattice_profile,
    ops_object.OBJECT_OT_resize,
    ops_utils.SCENE_OT_scene_units_set,
    ops_utils.VIEW3D_OT_search_asset,
    ops_utils.OBJECT_OT_widget_override_set,
    ops_utils.OBJECT_OT_widget_override_del,
    ops_weighting.WM_OT_ul_materials_add,
    ops_weighting.WM_OT_ul_materials_del,
    ops_weighting.WM_OT_ul_materials_clear,
    ops_weighting.WM_OT_ul_materials_move,
    ops_weighting.OBJECT_OT_weight_display,
    ops_weighting.WM_OT_weighting_set_add,
    ops_weighting.WM_OT_weighting_set_replace,
    ops_weighting.WM_OT_weighting_set_del,
    ops_weighting.WM_OT_weighting_set_rename,
    ops_weighting.WM_OT_weighting_set_refresh,
    ops_weighting.WM_OT_weighting_set_autoload_mark,
    ops_weighting.WM_OT_weighting_set_load,
    ops_weighting.WM_OT_weighting_set_load_append,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.jewelcraft = PointerProperty(type=preferences.WmProperties)
    bpy.types.Scene.jewelcraft = PointerProperty(type=preferences.SceneProperties)

    # Translations
    # ---------------------------

    for k, v in mod_update.DICTIONARY.items():
        if k in localization.DICTIONARY.keys():
            localization.DICTIONARY[k].update(v)
        else:
            localization.DICTIONARY[k] = v

    bpy.app.translations.register(__name__, localization.DICTIONARY)

    mod_update.DICTIONARY.clear()

    # Previews
    # ---------------------------

    pcoll = bpy.utils.previews.new()

    for entry in os.scandir(var.ICONS_DIR):
        if entry.is_file() and entry.name.endswith(".png"):
            name = os.path.splitext(entry.name)[0]
            pcoll.load(name.upper(), entry.path, "IMAGE")
        if entry.is_dir():
            for subentry in os.scandir(entry.path):
                if subentry.is_file() and subentry.name.endswith(".png"):
                    name = entry.name + os.path.splitext(subentry.name)[0]
                    pcoll.load(name.upper(), subentry.path, "IMAGE")

    var.preview_collections["icons"] = pcoll

    # On load
    # ---------------------------

    on_load.handler_add()

    # mod_update
    # ---------------------------

    mod_update.update_init_check()


def unregister():
    from .lib import dynamic_list, widget

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
    dynamic_list._cache.clear()

    # Handlers
    # ---------------------------

    widget.handler_del()
    on_load.handler_del()


if __name__ == "__main__":
    register()
