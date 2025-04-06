# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "JewelCraft",
    "author": "Mikhail Rachinskiy",
    "version": (2, 17, 4),
    "blender": (3, 5, 0),
    "location": "3D View > Sidebar",
    "description": "Jewelry design toolkit.",
    "doc_url": "https://github.com/mrachinskiy/jewelcraft#readme",
    "tracker_url": "https://github.com/mrachinskiy/jewelcraft/issues",
    "category": "Object",
}


if "bpy" in locals():
    essentials.reload_recursive(var.ADDON_DIR, locals())
else:
    from . import var
    from .lib import essentials

    essentials.check(var.ICONS_DIR)

    import bpy
    from bpy.props import PointerProperty

    from . import (localization, op_cutter, op_design_report, op_distribute,
                   op_gem_map, op_microprong, op_prongs, ops_asset, ops_gem,
                   ops_measurement, ops_object, ops_utils, ops_weighting,
                   preferences, ui)
    from .lib import on_load, previewlib


classes = essentials.get_classes(
    (op_cutter, op_design_report, op_distribute, op_gem_map, op_microprong,
     op_prongs, ops_asset, ops_gem, ops_measurement, ops_object, ops_utils,
     ops_weighting, preferences, ui)
)


def register():
    var.config_dir_versioning()

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
