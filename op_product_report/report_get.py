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


from mathutils import Matrix


from .. import var
from ..lib import unit, mesh, asset


class DataCollect:

    def data_collect(self, context):
        import collections

        scene = context.scene
        depsgraph = context.depsgraph
        props = scene.jewelcraft
        UScale = unit.Scale()
        _from_scene = UScale.from_scene
        data = {
            "size": 0.0,
            "shank": [],
            "dim": [],
            "weight": 0.0,
            "gems": collections.defaultdict(int),
            "warn": [],
        }

        # Size
        # ---------------------------

        if props.product_report_ob_size:
            ob = props.product_report_ob_size
            size = max(ob.dimensions)
            data["size"] = _from_scene(size)

        # Shank
        # ---------------------------

        if props.product_report_ob_shank:
            ob = props.product_report_ob_shank

            asset.mod_curve_off(ob, reverse=True)
            dim = list(ob.dimensions)
            scene.update()

            dim.remove(max(dim))
            data["shank"] = _from_scene(dim, batch=True)

        # Dimensions
        # ---------------------------

        if props.product_report_ob_dim:
            ob = props.product_report_ob_dim
            data["dim"] = _from_scene(ob.dimensions.to_tuple(), batch=True)

        # Weight
        # ---------------------------

        if props.product_report_ob_weight:
            ob = props.product_report_ob_weight

            if ob.type == "MESH":
                data["weight"] = _from_scene(mesh.est_volume((ob,)), volume=True)

        # Gems
        # ---------------------------

        gems = data["gems"]
        known_stones = var.STONE_DENSITY.keys()
        known_cuts = var.CUT_VOLUME_CORRECTION.keys()
        ob_data = []
        df_leftovers = False
        deprecated_id = False
        unknown_id = False
        instance_orig = set(dup.instance_object.original for dup in depsgraph.object_instances if dup.is_instance)

        for dup in depsgraph.object_instances:

            if dup.is_instance:
                ob = dup.instance_object.original
            else:
                ob = dup.object.original

            if not deprecated_id:
                deprecated_id = ob.type == "MESH" and "gem" in ob.data

            if "gem" not in ob or (not dup.is_instance and ob in instance_orig):
                continue

            # Gem
            stone = ob["gem"]["stone"]
            cut = ob["gem"]["cut"]
            size = tuple(round(x, 2) for x in _from_scene(ob.dimensions, batch=True))
            gems[(stone, cut, size)] += 1

            # Warnings
            loc = dup.matrix_world.to_translation()
            rad = max(ob.dimensions[:2]) / 2
            if dup.is_instance:
                mat = dup.matrix_world.copy()
            else:
                mat_loc = Matrix.Translation(loc)
                mat_rot = dup.matrix_world.to_quaternion().to_matrix().to_4x4()
                mat = mat_loc @ mat_rot
            loc.freeze()
            mat.freeze()
            ob_data.append((loc, rad, mat))

            if stone not in known_stones:
                stone = "*" + stone
                unknown_id = True

            if cut not in known_cuts:
                cut = "*" + cut
                unknown_id = True

            if (
                not df_leftovers and
                ob.parent and
                ob.parent.type == "MESH" and
                ob.parent.instance_type == "NONE"
            ):
                df_leftovers = True

        # Find overlaps
        # ---------------------------

        overlaps = False

        if self.prefs.product_report_use_overlap:
            thold = UScale.to_scene(0.1)
            overlaps = asset.gem_overlap(ob_data, threshold=thold, first_match=True)

        # Find hidden gems
        # ---------------------------

        hidden = False

        if self.prefs.product_report_use_hidden_gems:
            for ob in scene.objects:
                if "gem" in ob and not ob.visible_get():
                    hidden = True
                    break

        # Warnings
        # ---------------------------

        if hidden:
            data["warn"].append("Hidden gems (use Show Hidden/Alt H)")

        if df_leftovers:
            data["warn"].append("Possible gem dupli-face leftovers")

        if overlaps:
            data["warn"].append("Overlapping gems")

        if deprecated_id:
            data["warn"].append("Deprecated gem IDs (use Convert Deprecated Gem IDs from Operator Search menu)")

        if unknown_id:
            data["warn"].append("Unknown gem IDs, carats are not calculated for marked gems (*)")

        return data
