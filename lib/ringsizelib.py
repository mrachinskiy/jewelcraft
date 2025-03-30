# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from math import modf


US_BASE_CIR = 36.5367
US_STEP_CIR = 2.5535

UK_BASE_CIR = 37.5
UK_STEP_CIR = 1.25

JP_TO_US_SIZE_MAP = {
    1: 1,
    2: 2,
    3: 2.5,
    4: 3,
    5: 3.375,
    6: 3.625,
    7: 4,
    8: 4.5,
    9: 5,
    10: 5.375,
    11: 5.875,
    12: 6,
    13: 6.5,
    14: 7,
    15: 7.5,
    16: 8,
    17: 8.5,
    18: 9,
    19: 9.5,
    20: 10,
    21: 10.25,
    22: 10.5,
    23: 11,
    24: 11.5,
    25: 12,
    26: 12.5,
    27: 13,
}

HK_TO_US_SIZE_MAP = {
    5: 2.75,
    6: 3,
    7: 3.5,
    8: 3.75,
    9: 4.25,
    10: 4.75,
    11: 5.25,
    12: 5.5,
    13: 6,
    14: 6.5,
    15: 7,
    16: 7.5,
    17: 7.75,
    18: 8.25,
    19: 8.75,
    20: 9,
    21: 9.5,
    22: 10,
    23: 10.25,
    24: 10.75,
    25: 11.25,
    26: 11.5,
    27: 12,
    28: 12.5,
    29: 12.75,
    30: 13.25,
}


def _to_int(x: float) -> int | float:
    if x.is_integer():
        return int(x)
    return x


def _eq(a: float, b: float) -> bool:
    return abs(a - b) < 0.12  # ~0.1 mm in diameter


def to_size(cir: float, fmt: str) -> int | float | tuple[int, bool] | None:
    if fmt == "CH":
        size = round(cir - 40.0, 2)
        if size >= 0.0:
            return size

    elif fmt in {"US", "JP", "HK"}:
        size = round((cir - US_BASE_CIR) / US_STEP_CIR, 2)
        if size >= 0.0:
            if fmt == "US":
                return size
            elif fmt == "JP":
                for size_jp, size_us in JP_TO_US_SIZE_MAP.items():
                    if _eq(size, size_us):
                        return size_jp
            elif fmt == "HK":
                for size_hk, size_us in HK_TO_US_SIZE_MAP.items():
                    if _eq(size, size_us):
                        return size_hk

    elif fmt == "UK":
        import string

        size_raw = (cir - UK_BASE_CIR) / UK_STEP_CIR
        if size_raw >= 0.0:
            fraction, integer = modf(size_raw)
            if fraction > 0.75:
                integer += 1.0
            if integer < len(string.ascii_uppercase):
                return int(integer), 0.25 < fraction < 0.75


def to_size_fmt(cir: float, fmt: str) -> int | float | str | None:
    size = to_size(cir, fmt)
    if size is None:
        return

    if fmt in {"CH", "US"}:
        return _to_int(size)
    elif fmt == "UK":
        import string

        i, half_size = size
        size_str = string.ascii_uppercase[i]
        if half_size:
            size_str += " 1/2"
        return size_str

    return size


def to_cir(size: int | float, fmt: str) -> float:
    if fmt == "CH":
        return size + 40.0

    if fmt == "UK":
        return UK_BASE_CIR + UK_STEP_CIR * size

    # US\JP\HK
    if fmt == "JP":
        size = JP_TO_US_SIZE_MAP[size]
    elif fmt == "HK":
        size = HK_TO_US_SIZE_MAP[size]
    return US_BASE_CIR + US_STEP_CIR * size
