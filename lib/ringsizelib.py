# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from typing import Union
from math import modf


CIR_BASE_US = 36.537
CIR_STEP_US = 2.5535

CIR_BASE_UK = 37.5
CIR_STEP_UK = 1.25

MAP_SIZE_JP_TO_US: dict[int, Union[int, float]] = {
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


def _to_int(x: float) -> Union[int, float]:
    if x.is_integer():
        return int(x)
    return x


def to_size(cir: float, fmt: str) -> Union[int, float, str, None]:
    if fmt == "CH":
        size = round(cir - 40.0, 2)
        if size >= 0.0:
            return _to_int(size)

    elif fmt in {"US", "JP"}:
        size = round((cir - CIR_BASE_US) / CIR_STEP_US, 2)

        if size >= 0.0:

            if fmt == "US":
                return _to_int(size)

            for size_jp, size_us in MAP_SIZE_JP_TO_US.items():
                if (size_us - 0.2) < size < (size_us + 0.2):
                    return size_jp

    elif fmt == "UK":
        import string

        size_raw = (cir - CIR_BASE_UK) / CIR_STEP_UK

        if size_raw >= 0.0:
            fraction, integer = modf(size_raw)
            half_size = 0.25 < fraction < 0.75
            if fraction > 0.75:
                integer += 1.0
            if integer < len(string.ascii_uppercase):
                size = string.ascii_uppercase[int(integer)]
                if half_size:
                    size += " 1/2"
                return size


def to_cir(size: Union[int, float], fmt: str) -> float:
    if fmt == "CH":
        cir = size + 40.0

    elif fmt == "UK":
        cir = CIR_BASE_UK + CIR_STEP_UK * size

    elif fmt in {"US", "JP"}:
        if fmt == "JP":
            size = MAP_SIZE_JP_TO_US[size]
        cir = CIR_BASE_US + CIR_STEP_US * size

    return round(cir, 4)
