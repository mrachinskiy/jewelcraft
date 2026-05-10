# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from . import gem_map, gem_map_2, spacing


def clear():
    gem_map.handler_del()
    gem_map_2.handler_del()
    gem_map_2.resources_clear()
    spacing.handler_del()
