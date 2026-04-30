# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from . import gem_map, gems_magnet, spacing


def clear():
    gem_map.handler_del()
    spacing.handler_del()
    gems_magnet.handler_del()
