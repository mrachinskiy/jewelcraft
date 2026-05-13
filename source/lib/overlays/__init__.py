# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from . import gem_map, spacing


def clear():
    gem_map.handler_del()
    gem_map.resources_clear()
    spacing.handler_del()
