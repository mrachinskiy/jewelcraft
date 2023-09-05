# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from . import gem_map, spacing


def clear():
    gem_map.handler_del()
    spacing.handler_del()
