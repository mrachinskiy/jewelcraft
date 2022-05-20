# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from collections.abc import Iterator

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

    def overlap(self, dup: DepsgraphObjectInstance) -> None:
        self._overlap_data.append(asset.gem_transform(dup))

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
