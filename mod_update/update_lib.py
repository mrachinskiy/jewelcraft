# ##### BEGIN GPL LICENSE BLOCK #####
#
#  mod_update automatic add-on updates.
#  Copyright (C) 2019  Mikhail Rachinskiy
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
        "last_check": 0,
    }

    if not reset and os.path.exists(var.UPDATE_SAVE_STATE_FILEPATH):
        with open(var.UPDATE_SAVE_STATE_FILEPATH, "r", encoding="utf-8") as file:
            data.update(json.load(file))

    return data


def _save_state_set():
    import datetime
    import json

    data = {
        "update_available": var.update_available,
        "last_check": int(datetime.datetime.now().timestamp()),
    }

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
        last_check = datetime.date.fromtimestamp(save_state["last_check"])
        delta = datetime.date.today() - last_check
        var.update_days_passed = delta.days

    if not use_force_check and not prefs.update_use_auto_check:
        return

    if save_state["update_available"]:
        use_force_check = True

    if not use_force_check and (var.update_days_passed and var.update_days_passed < int(prefs.update_interval)):
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

                if update_version > var.UPDATE_CURRENT_VERSION:
                    break
                else:
                    if var.update_days_passed is None:
                        var.update_days_passed = 0
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
            addons_dir = os.path.dirname(var.ADDON_DIR)
            extract_dirname = zfile.namelist()[0]
            extract_dir = os.path.join(addons_dir, extract_dirname)

            shutil.rmtree(var.ADDON_DIR)
            zfile.extractall(addons_dir)
            os.rename(extract_dir, var.ADDON_DIR)

    var.update_completed = True
    _runtime_state_set(in_progress=True)


def update_init_check(use_force_check=False):
    threading.Thread(target=_update_check, args=(use_force_check,)).start()


def update_init_download():
    threading.Thread(target=_update_download).start()
