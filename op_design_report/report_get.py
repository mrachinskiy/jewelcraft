# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import collections

import bpy

from ..lib import unit, mesh
from . import report_warn


class _Data:
    __slots__ = ("gems", "materials", "notes", "warnings")

    def __init__(self):
        self.gems = collections.defaultdict(int)
        self.materials = []
        self.notes = []
        self.warnings = []

    def is_empty(self):
        for prop in self.__slots__:
            if getattr(self, prop):
                return False
        return True


def data_collect(gem_map: bool = False, show_warnings: bool = True) -> _Data:
    Report = _Data()
    Warn = report_warn.Warnings()
    Scale = unit.Scale()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    props = bpy.context.scene.jewelcraft

    # Gems
    # ---------------------------

    for dup in depsgraph.object_instances:

        if dup.is_instance:
            ob = dup.instance_object.original
            visible = dup.parent.original.visible_get()  # T74368
        else:
            ob = dup.object.original
            visible = ob.visible_get()

        if "gem" not in ob or not visible:
            continue

        # Gem
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in Scale.from_scene_vec(ob.dimensions))

        # Warnings
        Warn.overlap(dup, ob.dimensions)
        stone, cut = Warn.validate_id(stone, cut)

        Report.gems[(stone, cut, size)] += 1

    if show_warnings:
        Warn.report(Report.warnings)

    if gem_map:
        return Report

    # Measurements
    # ---------------------------

    for item in props.measurements.coll:

        if item.collection is None and item.object is None:
            continue

        if item.type == "WEIGHT":
            name = item.material_name
            density = unit.convert_cm3_mm3(item.material_density)
            obs = (
                ob for ob in item.collection.objects
                if ob.type in {"MESH", "CURVE", "SURFACE", "FONT", "META"}
            )
            vol = Scale.from_scene_vol(mesh.est_volume(obs))
            Report.materials.append((name, density, vol))

        elif item.type == "DIMENSIONS":
            axes = []
            if item.x: axes.append(0)
            if item.y: axes.append(1)
            if item.z: axes.append(2)

            if not axes:
                continue

            dim = Scale.from_scene_vec(item.object.dimensions)
            values = tuple(round(dim[x], 2) for x in axes)
            Report.notes.append((item.type, item.name, values))

        elif item.type == "RING_SIZE":
            dim = Scale.from_scene(item.object.dimensions[int(item.axis)])
            values = (round(dim, 2), item.ring_size)
            Report.notes.append((item.type, item.name, values))

    return Report
