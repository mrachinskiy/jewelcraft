# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import collections
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


def data_collect(gem_map: bool = False, show_warnings: bool = True, show_metadata: bool = True) -> _Data:
    Report = _Data()
    Warn = report_warn.Warnings()
    Scale = unit.Scale()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    scene_props = bpy.context.scene.jewelcraft
    wm_props = bpy.context.window_manager.jewelcraft

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

        for item in wm_props.report_metadata.coll:

            value = item.value.format(FILENAME=filename, DATE=date)

            if not value or value == "...":
                continue

            Report.metadata.append((item.name, value))

    # Measurements
    # ---------------------------

    for item in scene_props.measurements.coll:

        if item.collection is None and item.object is None:
            continue

        if item.datablock_type == "OBJECT":
            obs = (item.object,)
            dim = Scale.from_scene_vec(item.object.dimensions)
        else:
            obs = (
                ob for ob in item.collection.all_objects
                if ob.type in {"MESH", "CURVE", "SURFACE", "FONT", "META"}
            )
            if not obs:
                continue
            BBox = asset.ObjectsBoundBox(obs)
            dim = Scale.from_scene_vec(BBox.dimensions)

        if item.type == "WEIGHT":
            density = unit.convert_cm3_mm3(item.material_density)
            vol = Scale.from_scene_vol(mesh.est_volume(obs))
            Report.materials.append((item.name, density, vol))

        elif item.type == "DIMENSIONS":
            axes = [i for i, prop in enumerate((item.x, item.y, item.z)) if prop]
            if not axes:
                continue
            values = tuple(round(dim[x], 2) for x in axes)
            Report.notes.append((item.type, item.name, values))

        elif item.type == "RING_SIZE":
            values = (round(dim[int(item.axis)], 2), item.ring_size)
            Report.notes.append((item.type, item.name, values))

    return Report
