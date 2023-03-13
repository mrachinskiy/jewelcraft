# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import collections
from collections.abc import Iterator
from pathlib import Path

import bpy

from ..lib import unit, mesh, asset
from . import report_warn


class _Data:
    __slots__ = ("preview", "gems", "materials", "notes", "warnings", "metadata")

    def __init__(self):
        self.preview = None
        self.gems = collections.defaultdict(int)
        self.materials = []
        self.notes = []
        self.warnings = []
        self.metadata = []

    def is_empty(self):
        for prop in self.__slots__:
            if getattr(self, prop):
                return False
        return True


def _iter_metadata() -> Iterator[tuple[str, str]]:
    for item in bpy.context.window_manager.jewelcraft.report_metadata.coll:
        yield item.name, item.value
    for item in bpy.context.scene.jewelcraft.measurements.coll:
        if item.type == "METADATA":
            yield item.name, item.value


def data_collect(gem_map: bool = False, show_warnings: bool = True, show_metadata: bool = True) -> _Data:
    Report = _Data()
    Warn = report_warn.Warnings()
    Scale = unit.Scale()

    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Gems
    # ---------------------------

    for dup, ob, _ in asset.iter_gems(depsgraph):
        # Gem
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in Scale.from_scene_vec(ob.dimensions))

        # Warnings
        Warn.overlap(dup)
        stone, cut = Warn.validate_id(stone, cut)

        Report.gems[(stone, cut, size)] += 1

    if show_warnings:
        Warn.report(Report.warnings)

    if gem_map:
        return Report

    # Metadata
    # ---------------------------

    if show_metadata:
        import datetime
        date = datetime.date.today().isoformat()
        filename = Path(bpy.data.filepath).stem

        for meta_name, meta_value in _iter_metadata():
            meta_value = meta_value.format(FILENAME=filename, DATE=date)
            if not meta_value or meta_value == "...":
                continue
            Report.metadata.append((meta_name, meta_value))

    # Measurements
    # ---------------------------

    for item in bpy.context.scene.jewelcraft.measurements.coll:

        if item.collection is None and item.object is None:
            continue

        if item.datablock_type == "OBJECT":
            obs = (item.object,)
            dim = Scale.from_scene_vec(item.object.dimensions)
        else:
            obs = [
                ob for ob in item.collection.all_objects
                if ob.type in {"MESH", "CURVE", "SURFACE", "FONT", "META"}
            ]
            if not obs:
                continue
            BBox = asset.ObjectsBoundBox(obs)
            dim = Scale.from_scene_vec(BBox.dimensions)

        if item.type == "WEIGHT":
            density = unit.convert_cm3_mm3(item.material_density)
            vol = Scale.from_scene_vol(mesh.est_volume(obs))
            Report.materials.append((item.name, density, vol))
        elif item.type == "DIMENSIONS":
            values = tuple(round(v, 2) for k, v in zip((item.x, item.y, item.z), dim) if k)
            if not values:
                continue
            Report.notes.append((item.type, item.name, values))
        elif item.type == "RING_SIZE":
            values = (round(dim[int(item.axis)], 2), item.ring_size)
            Report.notes.append((item.type, item.name, values))

    return Report
