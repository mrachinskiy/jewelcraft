# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

class SectionSize:
    __slots__ = "x", "y", "z1", "z2"

    def __init__(self, x: float, y: float, z1: float, z2: float) -> None:
        self.x = x
        self.y = y
        self.z1 = z1
        self.z2 = z2

    @property
    def xyz(self):
        return self.x, self.y, self.z1
