# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021-2022 Mikhail Rachinskiy

# v1.1.1

from __future__ import annotations
from pathlib import Path
from typing import Any

import bpy


def reload_recursive(path: Path, mods: dict[str, Any]) -> None:
    import importlib

    for child in path.iterdir():

        if child.is_file() and child.suffix == ".py" and not child.name.startswith("__") and child.stem in mods:
            importlib.reload(mods[child.stem])

        elif child.is_dir() and not child.name.startswith((".", "__")):

            if child.name in mods:
                reload_recursive(child, mods[child.name].__dict__)
                importlib.reload(mods[child.name])
                continue

            reload_recursive(child, mods)


def check(*args: Any) -> None:
    for arg in args:

        if isinstance(arg, Path) and not arg.exists():
            msg = "READ INSTALLATION GUIDE"
            error = FileNotFoundError(f"\n\n!!! {msg} !!! {msg} !!! {msg} !!!\n")
            raise error

        if isinstance(arg, tuple) and arg > bpy.app.version:
            ver = "{}.{}".format(*arg)
            error = RuntimeError(f"\n\n!!! BLENDER {ver} IS REQUIRED !!!\n")
            raise error
