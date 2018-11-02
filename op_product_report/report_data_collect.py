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


import collections

import bpy

from .. import var
from ..lib import unit, mesh, asset


def data_collect():
    scene = bpy.context.scene
    props = scene.jewelcraft
    prefs = bpy.context.user_preferences.addons[var.ADDON_ID].preferences
    data = {
        "size": 0.0,
        "shank": [],
        "dim": [],
        "weight": 0.0,
        "gems": {},
        "warn": [],
    }

    # Size
    # ---------------------------

    if props.product_report_ob_size:
        ob = props.product_report_ob_size
        size = max(ob.dimensions)
        data["size"] = unit.to_metric(size)

    # Shank
    # ---------------------------

    if props.product_report_ob_shank:
        ob = props.product_report_ob_shank

        asset.mod_curve_off(ob, reverse=True)
        dim = list(ob.dimensions)
        scene.update()

        dim.remove(max(dim))
        data["shank"] = unit.to_metric(dim, batch=True)

    # Dimensions
    # ---------------------------

    if props.product_report_ob_dim:
        ob = props.product_report_ob_dim
        data["dim"] = unit.to_metric(ob.dimensions.to_tuple(), batch=True)

    # Weight
    # ---------------------------

    if props.product_report_ob_weight:
        ob = props.product_report_ob_weight

        if ob.type == "MESH":
            data["weight"] = unit.to_metric(mesh.est_volume((ob,)), volume=True)

    # Gems
    # ---------------------------

    gms = data["gems"]
    known_stones = var.STONE_DENSITY.keys()
    known_cuts = var.CUT_VOLUME_CORRECTION.keys()

    doubles = collections.defaultdict(int)
    hidden = False
    df_leftovers = False
    deprecated_id = False
    unknown_id = False

    if prefs.product_report_use_layers:
        visible_layers = [i for i, x in enumerate(scene.layers) if x]
        obs = []
        app = obs.append
        for ob in scene.objects:
            for i in visible_layers:
                if ob.layers[i]:
                    app(ob)
                    break
    else:
        obs = scene.objects

    for ob in obs:

        if not deprecated_id:
            deprecated_id = ob.type == "MESH" and "gem" in ob.data

        if "gem" in ob:

            # Gem
            stone = ob["gem"]["stone"]
            cut = ob["gem"]["cut"]
            size = tuple(round(x, 2) for x in unit.to_metric(ob.dimensions, batch=True))
            count = 1

            # Warnings
            if not hidden and not ob.is_visible(scene):
                hidden = True

            loc = ob.matrix_world.to_translation().to_tuple()
            doubles[loc] += 1

            if stone not in known_stones:
                stone = "*" + stone
                unknown_id = True

            if cut not in known_cuts:
                cut = "*" + cut
                unknown_id = True

            # Dupli-faces
            if ob.parent and ob.parent.type == "MESH":
                if ob.parent.dupli_type == "FACES":
                    ob.parent.dupli_list_create(scene)
                    count = len([x for x in ob.parent.dupli_list if x.object == ob])
                    ob.parent.dupli_list_clear()
                elif ob.parent.dupli_type == "NONE":
                    df_leftovers = True

            if stone in gms and cut in gms[stone] and size in gms[stone][cut]:
                gms[stone][cut][size] += count
            elif stone in gms and cut in gms[stone]:
                gms[stone][cut][size] = count
            elif stone in gms:
                gms[stone][cut] = {size: count}
            else:
                gms[stone] = {cut: {size: count}}

    # Find duplicates
    # ---------------------------

    doubles = [x for x in doubles.values() if x > 1]

    # Warnings
    # ---------------------------

    if hidden:
        data["warn"].append("Hidden gems (use Show Hidden/Alt H)")

    if df_leftovers:
        data["warn"].append("Possible gem dupli-face leftovers")

    if doubles:
        data["warn"].append("Duplicated gems")

    if deprecated_id:
        data["warn"].append("Deprecated gem IDs (use Convert Deprecated Gem IDs from Operator Search menu)")

    if unknown_id:
        data["warn"].append("Unknown gem IDs, carats are not calculated for marked gems (*)")

    return data
