# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


if "bpy" in locals():
    _essential.reload_recursive(var.ADDON_DIR, locals())
else:
    from . import var
    from .lib import _essential

    _essential.check(var.ICONS_DIR, var.MANIFEST["blender_version_min"])

    import bpy
    from bpy.props import PointerProperty

    from . import (localization, op_cutter, op_design_report, op_distribute,
                   op_gem_map, op_microprong, op_prongs, ops_asset, ops_gem,
                   ops_measurement, ops_object, ops_utils, ops_weighting,
                   preferences, ui)
    from .lib import data, on_load, previewlib


classes = (
    preferences.MeasurementCollection,
    preferences.Metadata,
    preferences.MaterialCollection,
    preferences.MaterialListCollection,
    preferences.AssetLibCollection,
    preferences.SizeCollection,
    preferences.MeasurementList,
    preferences.MetadataList,
    preferences.MaterialList,
    preferences.AssetLibList,
    preferences.SizeList,
    preferences.Preferences,
    preferences.WmProperties,
    preferences.SceneProperties,
    ui.VIEW3D_UL_jewelcraft_material_list,
    ui.VIEW3D_UL_jewelcraft_measurements,
    ui.VIEW3D_UL_jewelcraft_metadata,
    ui.VIEW3D_UL_jewelcraft_asset_libs,
    ui.VIEW3D_UL_jewelcraft_asset_libs_select,
    ui.VIEW3D_UL_jewelcraft_sizes,
    ui.VIEW3D_MT_jewelcraft,
    ui.VIEW3D_MT_jewelcraft_select_gem_by,
    ui.VIEW3D_MT_jewelcraft_asset_folder,
    ui.VIEW3D_MT_jewelcraft_weighting_mats,
    ui.VIEW3D_PT_jewelcraft_asset_libs,
    ui.VIEW3D_PT_jewelcraft_weighting_lib,
    ui.VIEW3D_PT_jewelcraft_warning,
    ui.VIEW3D_PT_jewelcraft_gems,
    ui.VIEW3D_PT_jewelcraft_spacing_overlay,
    ui.VIEW3D_PT_jewelcraft_gem_map_overlay,
    ui.VIEW3D_PT_jewelcraft_assets,
    ui.VIEW3D_PT_jewelcraft_jeweling,
    ui.VIEW3D_PT_jewelcraft_object,
    ui.VIEW3D_PT_jewelcraft_object_editmesh,
    ui.VIEW3D_PT_jewelcraft_curve,
    ui.VIEW3D_PT_jewelcraft_curve_editmesh,
    ui.VIEW3D_PT_jewelcraft_weighting,
    ui.VIEW3D_PT_jewelcraft_design_report,
    ui.VIEW3D_PT_jewelcraft_measurement,
    op_cutter.Dimensions,
    op_cutter.OBJECT_OT_cutter_add,
    op_gem_map.VIEW3D_OT_gem_map,
    op_microprong.OBJECT_OT_microprong_cutter_add,
    op_design_report.WM_OT_design_report,
    op_prongs.OBJECT_OT_prongs_add,
    op_distribute.OBJECT_OT_curve_distribute,
    op_distribute.OBJECT_OT_curve_redistribute,
    ops_asset.WM_OT_asset_folder_create,
    ops_asset.WM_OT_asset_folder_rename,
    ops_asset.WM_OT_asset_ui_refresh,
    ops_asset.WM_OT_asset_add,
    ops_asset.WM_OT_asset_remove,
    ops_asset.WM_OT_asset_rename,
    ops_asset.WM_OT_asset_replace,
    ops_asset.WM_OT_asset_preview_replace,
    ops_asset.WM_OT_asset_import,
    ops_asset.WM_OT_asset_favorite_add,
    ops_asset.WM_OT_asset_favorite_del,
    ops_asset.WM_OT_asset_menu,
    ops_gem.OBJECT_OT_gem_add,
    ops_gem.OBJECT_OT_gem_edit,
    ops_gem.OBJECT_OT_gem_recover,
    ops_gem.OBJECT_OT_gem_select_by_trait,
    ops_gem.OBJECT_OT_gem_select_overlapping,
    ops_measurement.WM_OT_ul_measurements_add,
    ops_measurement.WM_OT_ul_measurements_material_select,
    ops_object.CURVE_OT_size_curve_add,
    ops_object.CURVE_OT_length_display,
    ops_object.OBJECT_OT_stretch_along_curve,
    ops_object.OBJECT_OT_move_over_under,
    ops_object.OBJECT_OT_mirror,
    ops_object.OBJECT_OT_radial_instance,
    ops_object.OBJECT_OT_instance_face,
    ops_object.OBJECT_OT_lattice_project,
    ops_object.OBJECT_OT_lattice_profile,
    ops_object.OBJECT_OT_resize,
    ops_utils.SCENE_OT_ul_del,
    ops_utils.SCENE_OT_ul_clear,
    ops_utils.SCENE_OT_ul_move,
    ops_utils.WM_OT_ul_add,
    ops_utils.WM_OT_ul_del,
    ops_utils.WM_OT_ul_clear,
    ops_utils.WM_OT_ul_move,
    ops_utils.SCENE_OT_scene_units_set,
    ops_utils.WM_OT_goto_prefs,
    ops_utils.OBJECT_OT_overlay_override_add,
    ops_utils.OBJECT_OT_overlay_override_del,
    ops_weighting.WM_OT_ul_material_add,
    ops_weighting.OBJECT_OT_weight_display,
    ops_weighting.WM_OT_weighting_list_add,
    ops_weighting.WM_OT_weighting_list_replace,
    ops_weighting.WM_OT_weighting_list_del,
    ops_weighting.WM_OT_weighting_ui_refresh,
    ops_weighting.WM_OT_weighting_list_set_default,
    ops_weighting.WM_OT_weighting_list_import,
)


def register():
    for cls in classes:
        if cls is ui.VIEW3D_PT_jewelcraft_assets:
            prefs = bpy.context.preferences.addons[__package__].preferences
            cls.bl_ui_units_x = prefs.asset_popover_width
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.jewelcraft = PointerProperty(type=preferences.WmProperties)
    bpy.types.Scene.jewelcraft = PointerProperty(type=preferences.SceneProperties)

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.append(ui.draw_jewelcraft_menu)

    # On load
    # ---------------------------

    on_load.handler_add()

    # Translations
    # ---------------------------

    bpy.app.translations.register(__name__, localization.DICTIONARY)

    # Versioning
    # ---------------------------

    data.versioning_asset_favs()


def unregister():
    from .lib import overlays

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.jewelcraft
    del bpy.types.Scene.jewelcraft

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.remove(ui.draw_jewelcraft_menu)

    # Handlers
    # ---------------------------

    overlays.clear()
    on_load.handler_del()

    # Translations
    # ---------------------------

    bpy.app.translations.unregister(__name__)

    # Previews
    # ---------------------------

    previewlib.clear_previews()

    # Other
    # ---------------------------

    preferences._folder_cache.clear()


if __name__ == "__main__":
    register()
