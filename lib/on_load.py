# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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


import os

import bpy
from bpy.app.handlers import persistent

from .. import var
from . import asset


def handler_add():
    bpy.app.handlers.load_post.append(_execute)


def handler_del():
    bpy.app.handlers.load_post.remove(_execute)


@persistent
def _execute(dummy):
    _load_weighting_mats()
    _load_asset_libs()


def _load_weighting_mats():
    materials = bpy.context.scene.jewelcraft.weighting_materials

    if materials.coll:
        return

    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
    asset.weighting_set_deserialize(materials, prefs.weighting_set_autoload)


def _load_asset_libs():
    if os.path.exists(var.ASSET_LIBS_FILEPATH):
        libs = bpy.context.window_manager.jewelcraft.asset_libs
        asset.ul_deserialize(libs, var.ASSET_LIBS_FILEPATH)
        libs.index = 0
        return

    # TODO serialize deprecated property
    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences

    if prefs.asset_libs.values():
        asset.asset_libs_serialize(prefs.asset_libs)

        prefs.asset_libs.clear()
        bpy.context.preferences.is_dirty = True

        _load_asset_libs()
