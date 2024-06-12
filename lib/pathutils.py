# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import bpy

from .. import var


def get_asset_lib_path() -> Path:
    wm_props = bpy.context.window_manager.jewelcraft
    return Path(bpy.path.abspath(wm_props.asset_libs.active_item().path))


def get_weighting_lib_path() -> Path:
    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
    return Path(bpy.path.abspath(prefs.weighting_lib_path))


def get_weighting_list_filepath(name) -> Path:
    return get_weighting_lib_path() / (name + ".json")
