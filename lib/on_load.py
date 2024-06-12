# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.app.handlers import persistent

from .. import var
from . import data


def handler_add():
    bpy.app.handlers.load_post.append(_execute)


def handler_del():
    bpy.app.handlers.load_post.remove(_execute)


@persistent
def _execute(dummy):
    _load_weighting_mats()
    data.asset_libs_deserialize()
    data.report_metadata_deserialize()


def _load_weighting_mats():
    materials = bpy.context.scene.jewelcraft.weighting_materials

    if materials.coll:
        return

    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences

    try:
        data.weighting_list_deserialize(prefs.weighting_default_list)
    except FileNotFoundError:
        prefs.property_unset("weighting_default_list")
        bpy.context.preferences.is_dirty = True
        data.weighting_list_deserialize(prefs.weighting_default_list)
