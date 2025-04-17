# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


import bpy

from .. import var

repo_name = ""
is_remote_repo = False


def _init() -> None:
    global repo_name
    global is_remote_repo

    addon_module = var.ADDON_ID.split(".")[1]

    for repo in bpy.context.preferences.extensions.repos:
        if repo.use_remote_url and repo.module == addon_module:
            repo_name = repo.name
            is_remote_repo = True
            return


def check() -> bool:
    if not is_remote_repo:
        return False

    repo = bpy.context.preferences.extensions.repos.get(repo_name)
    if repo is None:
        _init()
        return False

    if repo.use_sync_on_startup is True:
        return False

    return True


_init()
