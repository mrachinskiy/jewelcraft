# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy

from mathutils import Color


def hex_to_rgb(v: str) -> Color:
    if v[0] == "#":
        v = v[1:]

    v = int(v, base=16)

    r = (v >> 16) & 255
    g = (v >> 8) & 255
    b = v & 255

    return Color((r / 255, g / 255, b / 255)).from_srgb_to_scene_linear()


def rbg_to_hex(color: Color) -> str:
    r, g, b = [int(v * 255 + 0.5) for v in color.copy().from_scene_linear_to_srgb()]
    return f"{r:02x}{g:02x}{b:02x}"


def luma(rgb: tuple[float, float, float, ...]) -> float:
    r, g, b, *a = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b
