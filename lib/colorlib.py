# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


def hex_to_rgb(v: str | int) -> tuple[float, float, float]:
    if isinstance(v, str):
        v = int(v[1:], base=16)

    return (
        _srgb_to_linear((v >> 16) & 255),
        _srgb_to_linear((v >> 8) & 255),
        _srgb_to_linear(v & 255),
    )


def rbg_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = [int(linear_to_srgb(v) * 255 + 0.5) for v in rgb]
    return f"#{r:02X}{g:02X}{b:02X}"


def _srgb_to_linear(v: int) -> float:
    v = v / 255

    if v == 1.0:
        return v

    if v <= 0.04045:
        return v / 12.92

    return ((v + 0.055) / 1.055) ** 2.4


def linear_to_srgb(v: float) -> float:
        if v >= 1.0:
            return 1.0

        if v <= 0.0031308:
            return v * 12.92

        return 1.055 * (v ** (1 / 2.4)) - 0.055


def luma(rgb: tuple[float, float, float, ...]) -> float:
    r, g, b, *a = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b
