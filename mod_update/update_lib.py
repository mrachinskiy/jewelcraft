# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import threading
import os

import bpy

from .. import var


def _save_state_get(reset=False):
    import json

    data = {
        "update_available": False,
        "last_check": "",
    }

    if not reset and os.path.exists(var.UPDATE_SAVE_STATE_FILEPATH):
        with open(var.UPDATE_SAVE_STATE_FILEPATH, "r", encoding="utf-8") as file:
            data.update(json.load(file))

    return data


def _save_state_set(reset=False):
    import datetime
    import json

    data = {
        "update_available": False if reset else var.update_available,
        "last_check": "" if reset else datetime.date.today().isoformat(),
    }

    if not os.path.exists(var.ADDON_DATA_DIR):
        os.makedirs(var.ADDON_DATA_DIR)

    with open(var.UPDATE_SAVE_STATE_FILEPATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def _runtime_state_set(in_progress=False):
    var.update_in_progress = in_progress

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def _update_check(use_force_check):
    import datetime
    import re
    import urllib.request
    import json

    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
    save_state = _save_state_get()

    if save_state["last_check"]:
        last_check = datetime.datetime.strptime(save_state["last_check"], "%Y-%m-%d").date()
        today = datetime.date.today()
        delta = today - last_check
        var.update_last_check = delta.days

    if not use_force_check and not prefs.update_use_auto_check:
        return

    if save_state["update_available"]:
        use_force_check = True

    if not use_force_check and (var.update_last_check and var.update_last_check < int(prefs.update_interval)):
        return

    _runtime_state_set(in_progress=True)

    with urllib.request.urlopen(var.UPDATE_RELEASES_URL) as response:
        data = json.load(response)

        for release in data:

            if not prefs.update_use_prerelease and release["prerelease"]:
                continue

            if not release["draft"]:
                update_version_string = re.sub(r"[^0-9]", " ", release["tag_name"])
                update_version = tuple(int(x) for x in update_version_string.split())

                if var.UPDATE_MAX_VERSION and update_version >= var.UPDATE_MAX_VERSION:
                    continue

                if update_version > var.UPDATE_ADDON_VERSION:
                    break
                else:
                    if var.update_last_check is None:
                        var.update_last_check = 0
                    _save_state_set()
                    _runtime_state_set(in_progress=False)
                    return

        with urllib.request.urlopen(release["assets_url"]) as response:
            data = json.load(response)

            for asset in data:
                if re.match(r".+\d+.\d+.\d+.+", asset["name"]):
                    break

            prerelease_note = " (pre-release)" if release["prerelease"] else ""
            var.update_download_url = asset["browser_download_url"]
            var.update_html_url = release["html_url"]
            var.update_available = True
            var.update_version = release["tag_name"] + prerelease_note

    _save_state_set()
    _runtime_state_set(in_progress=False)


def _update_download():
    import io
    import zipfile
    import urllib.request
    import shutil

    _runtime_state_set(in_progress=True)

    with urllib.request.urlopen(var.update_download_url) as response:
        with zipfile.ZipFile(io.BytesIO(response.read())) as zfile:
            addon_pardir = os.path.dirname(var.ADDON_DIR)
            extract_dirname = zfile.namelist()[0]
            extract_dir = os.path.join(addon_pardir, extract_dirname)

            shutil.rmtree(var.ADDON_DIR)
            zfile.extractall(addon_pardir)
            os.rename(extract_dir, var.ADDON_DIR)

    var.update_completed = True
    _save_state_set(reset=True)
    _runtime_state_set(in_progress=True)


def update_init_check(use_force_check=False):
    threading.Thread(target=_update_check, args=(use_force_check,)).start()


def update_init_download():
    threading.Thread(target=_update_download).start()
