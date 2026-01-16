# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
from pathlib import Path

import bpy

from ...lib import asset, mesh, unit
from . import report_warn


class _Data:
    __slots__ = "warnings", "metadata", "gems", "entries"

    def __init__(self):
        self.gems = collections.defaultdict(int)
        self.warnings = []
        self.metadata = []
        self.entries = []

    def is_empty(self):
        if any((self.gems, self.entries, self.metadata)):
            return False
        return True

    def asdict(self):
        d = collections.defaultdict(list)

        for prop in self.__slots__:
            if not (value := getattr(self, prop)):
                continue

            if prop == "warnings":
                d[prop] = value
            elif prop == "metadata":
                d[prop] = tuple((k, v) for k, v in value)
            elif prop == "gems":
                d[prop] = [x._asdict() for x in value]
            else:
                for i, k, v in value:
                    d[i.lower()].append((k, v))

        return d


def data_collect(gem_map: bool = False, show_warnings: bool = True) -> _Data:
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
        size = tuple(round(x, 2) for x in Scale.from_scene(ob.dimensions))
        color = ob.material_slots[0].name if ob.material_slots else ""

        # Warnings
        Warn.overlap(dup)
        stone, cut = Warn.validate_id(stone, cut)

        Report.gems[(stone, cut, size, color)] += 1

    if show_warnings:
        Warn.report(Report.warnings)

    if gem_map:
        return Report

    # Entries
    # ---------------------------

    import datetime

    date = datetime.date.today().isoformat()
    filename = Path(bpy.data.filepath).stem
    meta_templates = {
        "blend_name": filename,
        "date": date,
        # Legacy
        "FILENAME": filename,
        "DATE": date,
    }

    for item in bpy.context.scene.jewelcraft.measurements.coll:

        if item.type == "METADATA":
            try:
                meta_value = item.value.format(**meta_templates)
            except KeyError:
                meta_value = "ERROR"

            if not meta_value:
                continue

            Report.metadata.append((item.name, meta_value))
            continue

        if item.collection is None and item.object is None:
            continue

        if item.datablock_type == "OBJECT":
            obs = (item.object,)
            dim = Scale.from_scene(item.object.dimensions)
        else:
            obs = [
                ob for ob in item.collection.all_objects
                if ob.type in {"MESH", "CURVE", "SURFACE", "FONT", "META"}
            ]
            if not obs:
                continue
            BBox = asset.BoundBox(obs)
            dim = Scale.from_scene(BBox.dimensions)

        if item.type == "WEIGHT":
            vol = Scale.from_scene_vol(mesh.est_volume(obs))
            density = unit.convert_cm3_mm3(item.material_density)
            Report.entries.append((item.type, item.name, (vol, density)))
        elif item.type == "VOLUME":
            vol = Scale.from_scene_vol(mesh.est_volume(obs))
            Report.entries.append((item.type, item.name, vol))
        elif item.type == "RING_SIZE":
            values = (round(dim[int(item.axis)], 2), item.ring_size)
            Report.entries.append((item.type, item.name, values))
        elif item.type == "DIMENSIONS":
            values = tuple(round(v, 2) for k, v in zip((item.x, item.y, item.z), dim) if k)
            if not values:
                continue
            Report.entries.append((item.type, item.name, values))

    return Report
