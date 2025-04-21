# SPDX-FileCopyrightText: 2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import filecmp
import sys
import tempfile
import traceback
from pathlib import Path

import bpy
from bpy.types import Object


def _entry(type: str, ob: Object, **kwargs) -> None:
    item = bpy.context.scene.jewelcraft.measurements.add()

    item.type = type
    item.object = ob
    item.datablock_type = "OBJECT"

    if type == "WEIGHT":
        item.name = kwargs["name"]
        item.material_name = kwargs["name"]
        item.material_density = kwargs["density"]
    elif type == "DIMENSIONS":
        item.name = "{} {}".format(ob.name, "Dimensions")
        item.x = True
        item.y = True
        item.z = kwargs["z"]
    elif type == "RING_SIZE":
        item.name = "{} ({})".format("Ring Size", kwargs["size_format"])
        item.ring_size = kwargs["size_format"]
        item.axis = "0"


def set_up() -> None:
    gems = (
        ({"cut": "ROUND", "stone": "DIAMOND", "size": 1}, 8),
        ({"cut": "ROUND", "stone": "DIAMOND", "size": 1.25}, 4),
        ({"cut": "ROUND", "stone": "DIAMOND", "size": 1.5}, 2),
        ({"cut": "ROUND", "stone": "RUBY", "size": 5}, 1),
    )

    for gem, qty in gems:
        for i in range(qty):
            bpy.ops.object.jewelcraft_gem_add(**gem)

    bpy.ops.curve.jewelcraft_size_curve_add(diameter=15.29)
    curve = bpy.context.object

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    cube.dimensions = 3, 4, 5

    _entry("WEIGHT", cube, name="Gold", density=15.53)
    _entry("WEIGHT", cube, name="Silver", density=10.36)
    _entry("RING_SIZE", curve, size_format="US")
    _entry("RING_SIZE", curve, size_format="DIA")
    _entry("DIMENSIONS", cube, z=True)
    _entry("DIMENSIONS", cube, z=False)


def _make_examples() -> None:
    for fmt in ("HTML", "JSON"):
        path = Path(__file__).parent / "data" / f"Design Report.{fmt.lower()}"
        bpy.ops.wm.jewelcraft_design_report(file_format=fmt, use_metadata=False, use_preview=False, filepath=str(path))


def test_design_report() -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        for fmt in ("HTML", "JSON"):
            test_path = Path(tempdir) / f"Design Report.{fmt.lower()}"
            example_path = Path(__file__).parent / "data" / f"Design Report.{fmt.lower()}"
            bpy.ops.wm.jewelcraft_design_report(file_format=fmt, use_metadata=False, use_preview=False, filepath=str(test_path))
            assert filecmp.cmp(test_path, example_path, shallow=False) == True


try:
    set_up()
    test_design_report()
    # _make_examples()
except:
    traceback.print_exc()
    sys.exit(1)
