# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from pathlib import Path

import bpy

from .. import var


_previews = {}


def clear_previews() -> None:
    import bpy.utils.previews

    for pcoll in _previews.values():
        bpy.utils.previews.remove(pcoll)

    _previews.clear()


def scan_icons(pcoll_name: str, folder: Path) -> dict:
    pcoll = _previews.get(pcoll_name)
    if pcoll is not None:
        return pcoll

    import bpy.utils.previews

    pcoll = bpy.utils.previews.new()

    for child in folder.iterdir():
        if child.is_file() and child.suffix == ".png":
            pcoll.load(child.stem.upper(), str(child), "IMAGE")
        elif child.is_dir():
            for subchild in child.iterdir():
                if subchild.is_file() and subchild.suffix == ".png":
                    filename = child.name + subchild.stem
                    pcoll.load(filename.upper(), str(subchild), "IMAGE")

    _previews[pcoll_name] = pcoll
    return pcoll


def icon(name: str, override: float | None = None) -> int:
    if override is not None:
        value = override
    else:
        value = bpy.context.preferences.themes[0].user_interface.wcol_tool.text.v

    theme = "DARK" if value < 0.5 else "LIGHT"
    return scan_icons("icons", var.ICONS_DIR)[theme + name].icon_id


def icon_menu(name: str) -> int:
    return icon(name, override=bpy.context.preferences.themes[0].user_interface.wcol_menu_item.text.v)


def _no_preview() -> int:
    return scan_icons("icons", var.ICONS_DIR)["NO_PREVIEW"].icon_id


# Assets


def asset_img(blend_path: str) -> int:
    pcoll = _previews.get("assets")
    if pcoll is None:
        import bpy.utils.previews
        pcoll = bpy.utils.previews.new()
        _previews["assets"] = pcoll

    img_path = Path(blend_path).with_suffix(".png")

    if img_path.exists():
        preview_id = str(hash(blend_path))
        if preview_id not in pcoll:
            pcoll.load(preview_id, str(img_path), "IMAGE")
        return pcoll[preview_id].icon_id

    return _no_preview()


def asset_img_del(preview_id: str) -> None:
    import bpy.utils.previews

    pcoll = _previews.get("assets")
    if pcoll is None:
        return

    if preview_id == "ALL":
        if pcoll is not None:
            bpy.utils.previews.remove(pcoll)
            del _previews["assets"]
        return

    preview_id = str(hash(preview_id))
    if preview_id in pcoll:
        del pcoll[preview_id]
