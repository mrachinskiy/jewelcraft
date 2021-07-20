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
from bpy.types import LayerCollection, Object
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
        "run_checks",
        "df_leftovers",
        "overlap_data",
        "is_unknown_id",
        "is_df_leftovers",
        "is_gem_overlap",
        "is_collection_visibility",
    )

    def __init__(self, show_warnings: bool) -> None:
        self.overlap_data: list[ObjectData] = []
        self.is_unknown_id = False
        self.is_df_leftovers = False
        self.is_gem_overlap = False
        self.is_collection_visibility = False

        methods = ("run_checks", "df_leftovers")

        for method in methods:

            if show_warnings:
                func = getattr(self, f"_{method}")
            else:
                func = self._blank

            setattr(self, method, func)

    def _run_checks(self) -> None:
        self.is_gem_overlap = self._gem_overlap(self.overlap_data)
        self.is_collection_visibility = self._collection_visibility()

    @staticmethod
    def _blank(x=None):
        pass

    def _df_leftovers(self, ob: Object) -> None:
        if (
            ob.parent and
            ob.parent.type == "MESH" and
            ob.parent.instance_type == "NONE"
        ):
            self.is_df_leftovers = True
            self.df_leftovers = self._blank

    @staticmethod
    def _gem_overlap(ob_data: list[ObjectData]) -> bool:
        threshold = unit.Scale(bpy.context).to_scene(0.1)
        return asset.gem_overlap(bpy.context, ob_data, threshold, first_match=True)

    @staticmethod
    def _collection_visibility() -> bool:
        for coll in _collection_walk(bpy.context.view_layer.layer_collection):
            if coll.hide_viewport:
                for ob in coll.collection.all_objects:
                    if "gem" in ob:
                        return True
        return False
