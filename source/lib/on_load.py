# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.app.handlers import persistent

from .. import var


def handler_add():
    bpy.app.handlers.load_post.append(_execute)


def handler_del():
    bpy.app.handlers.load_post.remove(_execute)


@persistent
def _execute(dummy):
    _scene_props_versioning()
    var.config_naming_versioning()

    scene_props = bpy.context.scene.jewelcraft
    scene_props.measurements.deserialize(is_on_load=True)
    _scene_materials_deserialize()

    wm_props = bpy.context.window_manager.jewelcraft
    wm_props.gem_colors.deserialize()
    wm_props.gem_map_palette.deserialize()
    wm_props.asset_libs.deserialize()


def _scene_materials_deserialize():
    materials = bpy.context.scene.jewelcraft.weighting_materials

    if materials.coll:
        return

    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences

    try:
        materials.deserialize(prefs.weighting_default_list)
    except FileNotFoundError:
        prefs.property_unset("weighting_default_list")
        bpy.context.preferences.is_dirty = True
        materials.deserialize(prefs.weighting_default_list)


def _scene_props_versioning():
    if bpy.app.version < (5, 0, 0):
        return
    if bpy.context.scene.get("jewelcraft"):
        del bpy.context.scene["jewelcraft"]
