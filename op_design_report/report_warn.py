# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


from collections.abc import Iterator

import bpy
from bpy.types import LayerCollection, DepsgraphObjectInstance
from mathutils import Vector, Matrix

from ..lib import unit, asset


ObjectData = tuple[Vector, float, Matrix]


def _collection_walk(coll: LayerCollection) -> Iterator[LayerCollection]:
    for subcoll in coll.children:
        yield subcoll
        if subcoll.children:
            yield from _collection_walk(subcoll)


class Warnings:
    __slots__ = (
        "_overlap_data",
        "_known_stones",
        "_known_cuts",
        "_is_unknown_id",
    )

    def __init__(self) -> None:
        from ..lib import gemlib

        self._overlap_data: list[ObjectData] = []
        self._known_stones = frozenset(gemlib.STONES.keys())
        self._known_cuts = frozenset(gemlib.CUTS.keys())
        self._is_unknown_id = False

    def report(self, report: list) -> None:
        if self._is_unknown_id:
            report.append("Unknown gem IDs, carats are not calculated for marked gems (*)")

        if self._check_overlap(self._overlap_data):
            report.append("Overlapping gems")

        if self._check_collection_visibility():
            report.append("Gems from hidden collections appear in report (don't use Hide in Viewport on collections)")

    def overlap(self, dup: DepsgraphObjectInstance, dim: Vector) -> None:
        rad = max(dim.xy) / 2
        loc, rot, _ = dup.matrix_world.decompose()
        mat = Matrix.LocRotScale(loc, rot, (1.0, 1.0, 1.0))
        loc.freeze()
        mat.freeze()

        self._overlap_data.append((loc, rad, mat))

    def validate_id(self, stone: str, cut: str) -> tuple[str, str]:
        if stone not in self._known_stones:
            stone = "*" + stone
            self._is_unknown_id = True

        if cut not in self._known_cuts:
            cut = "*" + cut
            self._is_unknown_id = True

        return stone, cut

    @staticmethod
    def _check_overlap(ob_data: list[ObjectData]) -> bool:
        threshold = unit.Scale().to_scene(0.1)
        return asset.gem_overlap(ob_data, threshold, first_match=True)

    @staticmethod
    def _check_collection_visibility() -> bool:
        for coll in _collection_walk(bpy.context.view_layer.layer_collection):
            if coll.hide_viewport:
                for ob in coll.collection.all_objects:
                    if "gem" in ob:
                        return True
        return False
