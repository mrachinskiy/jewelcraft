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


import collections

from mathutils import Matrix

from ..lib import unit, mesh, gemlib
from . import report_warn


class _Data:
    __slots__ = ("gems", "materials", "notes", "warnings")

    def __init__(self):
        self.gems = collections.defaultdict(int)
        self.materials = collections.defaultdict(float)
        self.notes = []
        self.warnings = []

    def is_empty(self):
        for prop in self.__slots__:
            if getattr(self, prop):
                return False
        return True


def data_collect(self, context, gem_map: bool = False) -> _Data:
    scene = context.scene
    depsgraph = context.evaluated_depsgraph_get()
    props = scene.jewelcraft
    from_scene_scale = unit.Scale(context).from_scene
    Report = _Data()
    Warn = report_warn.Warnings(self.show_warnings)

    if not gem_map:

        for item in props.measurements.coll:

            if not item.object:
                continue

            if item.type == "WEIGHT":
                if item.object.type == "MESH":
                    name = item.material_name
                    density = unit.convert_cm3_mm3(item.material_density)
                    vol = from_scene_scale(mesh.est_volume((item.object,)), volume=True)
                    Report.materials[(name, density)] += vol

            elif item.type == "DIMENSIONS":
                axes = []
                if item.x: axes.append(0)
                if item.y: axes.append(1)
                if item.z: axes.append(2)

                if not axes:
                    continue

                dim = from_scene_scale(item.object.dimensions, batch=True)
                values = tuple(round(dim[x], 2) for x in axes)
                Report.notes.append((item.type, item.name, values))

            elif item.type == "RING_SIZE":
                dim = from_scene_scale(item.object.dimensions[int(item.axis)])
                values = (round(dim, 2), item.ring_size)
                Report.notes.append((item.type, item.name, values))

    # Gems
    # ---------------------------

    known_stones = gemlib.STONES.keys()
    known_cuts = gemlib.CUTS.keys()
    orig_instance_obs = {dup.instance_object.original for dup in depsgraph.object_instances if dup.is_instance}

    for dup in depsgraph.object_instances:

        if dup.is_instance:
            ob = dup.instance_object.original
        else:
            ob = dup.object.original

        if "gem" not in ob or (not dup.is_instance and ob in orig_instance_obs):
            continue  # Skip original instance gem objects

        # Gem
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in from_scene_scale(ob.dimensions, batch=True))

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

        Warn.overlap_data.append((loc, rad, mat))
        Warn.df_leftovers(ob)

        if stone not in known_stones:
            stone = "*" + stone
            Warn.is_unknown_id = True

        if cut not in known_cuts:
            cut = "*" + cut
            Warn.is_unknown_id = True

        Report.gems[(stone, cut, size)] += 1

    # Warnings
    # ---------------------------

    Warn.run_checks()

    if Warn.is_collection_visibility:
        Report.warnings.append("Gems from hidden collections appear in report (don't use Hide in Viewport on collections)")

    if Warn.is_df_leftovers:
        Report.warnings.append("Possible gem instance face leftovers")

    if Warn.is_gem_overlap:
        Report.warnings.append("Overlapping gems")

    if Warn.is_unknown_id:
        Report.warnings.append("Unknown gem IDs, carats are not calculated for marked gems (*)")

    return Report
