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


import bpy
from bpy.app.handlers import persistent

from .. import var


def handler_add():
    bpy.app.handlers.load_post.append(_execute)


def handler_del():
    bpy.app.handlers.load_post.remove(_execute)


@persistent
def _execute(dummy):
    materials = bpy.context.scene.jewelcraft.weighting_materials

    if materials.coll:
        return

    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
    prefs_mats = prefs.weighting_materials

    if prefs_mats.coll:
        materials.copy_from(prefs_mats)
    else:
        for name, dens, comp in var.DEFAULT_WEIGHTING_SETS["JCASSET_PRECIOUS"]:
            item = materials.add()
            item.name = name
            item.composition = comp
            item.density = dens
