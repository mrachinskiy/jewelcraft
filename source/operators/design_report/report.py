# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy

import collections
from typing import Any, NamedTuple


class GemRaw(NamedTuple):
    stone: str
    cut: str
    size: tuple[float, float, float]
    color: str


class GemFmt(NamedTuple):
    stone: str
    cut: str
    color: str
    size: float
    ct: float
    qty: int
    ct_sum: float


class Meta(NamedTuple):
    name: str
    value: str


class RingValue(NamedTuple):
    format: str
    size: int | float | str | None


class Entry(NamedTuple):
    type: str
    name: str
    value: float | RingValue | tuple[float, ...] | None


class Data:
    __slots__ = "warnings", "metadata", "gems", "entries"

    gems: dict[GemRaw, int] | list[GemFmt]
    warnings: list[str]
    metadata: list[Meta]
    entries: list[Entry]

    def __init__(self):
        self.gems = collections.defaultdict(int)
        self.warnings = []
        self.metadata = []
        self.entries = []

    def is_empty(self) -> bool:
        if any((self.gems, self.entries, self.metadata)):
            return False
        return True

    def asdict(self) -> dict[str, list[str | dict[str, Any]]]:
        d = collections.defaultdict(list)

        for prop in self.__slots__:
            if not (item := getattr(self, prop)):
                continue

            if prop == "warnings":
                d[prop] = item
            elif prop in {"metadata", "gems"}:
                d[prop] = [x._asdict() for x in item]
            else:
                for typ, name, value in item:
                    if typ == "RING_SIZE":
                        value = value[1]
                    d[typ.lower()].append({"name": name, "value": value})

        return d
