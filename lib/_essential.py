# SPDX-FileCopyrightText: 2021-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

# v1.1.2

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


def check(*args: Path | str) -> None:
    for arg in args:

        if isinstance(arg, Path):
            if not arg.exists():
                raise FileNotFoundError("Incorrect package, follow installation guide")

        elif isinstance(arg, str):
            if tuple([int(x) for x in arg.split(".")]) > bpy.app.version:
                raise RuntimeError(f"Blender {arg} is required")
