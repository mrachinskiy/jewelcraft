# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy

from math import pi
from pathlib import Path

import bpy

from ...lib import asset, mesh, ringsizelib, unit
from . import report, report_warn


def data_collect(gem_map: bool = False, show_warnings: bool = True) -> report.Data:
    Report = report.Data()
    Warn = report_warn.Warnings()
    Scale = unit.Scale()

    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Gems
    # ---------------------------

    for dup, ob, _ in asset.iter_gems(depsgraph):
        # Gem
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in Scale.from_scene(asset.gem_dimensions(dup)))
        color = ob.material_slots[0].name if ob.material_slots else ""

        # Warnings
        Warn.overlap(dup)
        stone, cut = Warn.validate_id(stone, cut)

        Report.gems[report.GemRaw(stone, cut, size, color)] += 1

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

            Report.metadata.append(report.Meta(item.name, meta_value))
            continue

        # Other entries
        # ---------------------------

        if item.collection is None and item.object is None:
            continue

        value = None

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
            value = round(vol * density, 2)

        elif item.type == "VOLUME":
            value = round(Scale.from_scene_vol(mesh.est_volume(obs)), 2)

        elif item.type == "RING_SIZE":
            dia = round(dim[int(item.axis)], 2)
            cir = dia * pi

            if item.ring_size == "DIAMETER":
                size = dia
            elif item.ring_size == "CIRCUMFERENCE":
                size = round(cir, 2)
            else:
                size = ringsizelib.to_size_fmt(cir, item.ring_size)

            value = report.RingValue(item.ring_size, size)

        elif item.type == "DIMENSIONS":
            if not any((item.x, item.y, item.z)):
                continue
            value = tuple(round(v, 2) for k, v in zip((item.x, item.y, item.z), dim) if k)

        Report.entries.append(report.Entry(item.type, item.name, value))

    return Report
