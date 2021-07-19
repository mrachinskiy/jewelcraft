# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Essential utility functions.
#  Copyright (C) 2021  Mikhail Rachinskiy
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


# v1.1.0


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
