# ##### BEGIN GPL LICENSE BLOCK #####
#
#  mod_update automatic add-on updates.
#  Copyright (C) 2019-2020  Mikhail Rachinskiy
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
from . import state


ADDON_VERSION = None
RELEASES_URL = None
SAVE_STATE_FILEPATH = os.path.join(var.CONFIG_DIR, "update_state.json")


def _parse_tag(tag):
    import re

    vers = [
        tuple(int(x) for x in ver_str)
        for ver_str in
        [re.sub(r"[^0-9]", " ", ver_raw).split() for ver_raw in tag.split("-")]
    ]

    if len(vers) == 1:
        vers.append((0, 0, 0))

    return vers


def _save_state_deserialize():
    import datetime
    import json

    data = {
        "update_available": False,
        "last_check": 0,
    }

    if os.path.exists(SAVE_STATE_FILEPATH):
        with open(SAVE_STATE_FILEPATH, "r", encoding="utf-8") as file:
            data.update(json.load(file))

            last_check = datetime.date.fromtimestamp(data["last_check"])
            delta = datetime.date.today() - last_check
            state.days_passed = delta.days

    return data


def _save_state_serialize():
    import datetime
    import json

    state.days_passed = 0
    data = {
        "update_available": state.update_available,
        "last_check": int(datetime.datetime.now().timestamp()),
    }

    if not os.path.exists(var.CONFIG_DIR):
        os.makedirs(var.CONFIG_DIR)

    with open(SAVE_STATE_FILEPATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def _runtime_state_set(status):
    state.status = status

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def _update_check(use_force_check):
    import re
    import urllib.request
    import urllib.error
    import json
    import ssl

    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
    save_state = _save_state_deserialize()

    if not use_force_check and not prefs.update_use_auto_check:
        return

    if save_state["update_available"]:
        use_force_check = True

    if not use_force_check and (
        state.days_passed is not None and
        state.days_passed < int(prefs.update_interval)
    ):
        return

    _runtime_state_set(state.CHECKING)
    ssl_context = ssl.SSLContext()

    try:

        with urllib.request.urlopen(RELEASES_URL, context=ssl_context) as response:
            data = json.load(response)

            for release in data:

                if not prefs.update_use_prerelease and release["prerelease"]:
                    continue

                if not release["draft"]:
                    update_version, required_blender = _parse_tag(release["tag_name"])

                    if update_version > ADDON_VERSION:
                        if required_blender <= bpy.app.version:
                            break
                        else:
                            continue
                    else:
                        _save_state_serialize()
                        _runtime_state_set(None)
                        return

            with urllib.request.urlopen(release["assets_url"], context=ssl_context) as response:
                data = json.load(response)

                for asset in data:
                    if re.match(r".+\d+.\d+.\d+.+", asset["name"]):
                        break

                prerelease_note = " (pre-release)" if release["prerelease"] else ""

                state.update_available = True
                state.update_version = ".".join(str(x) for x in update_version) + prerelease_note
                state.download_url = asset["browser_download_url"]
                state.changelog_url = release["html_url"]

        _save_state_serialize()
        _runtime_state_set(None)

    except (urllib.error.HTTPError, urllib.error.URLError) as e:

        state.error_msg = str(e)

        _save_state_serialize()
        _runtime_state_set(state.ERROR)


def _update_download():
    import io
    import pathlib
    import zipfile
    import urllib.request
    import urllib.error
    import shutil
    import ssl

    _runtime_state_set(state.INSTALLING)
    ssl_context = ssl.SSLContext()

    try:

        with urllib.request.urlopen(state.download_url, context=ssl_context) as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as zfile:
                addons_dir = os.path.dirname(var.ADDON_DIR)
                extract_relpath = pathlib.Path(zfile.namelist()[0])
                extract_dir = os.path.join(addons_dir, extract_relpath.parts[0])

                shutil.rmtree(var.ADDON_DIR)
                zfile.extractall(addons_dir)
                os.rename(extract_dir, var.ADDON_DIR)

        _runtime_state_set(state.COMPLETED)

    except (urllib.error.HTTPError, urllib.error.URLError) as e:

        state.error_msg = str(e)
        _runtime_state_set(state.ERROR)


def update_init_check(use_force_check=False):
    threading.Thread(target=_update_check, args=(use_force_check,)).start()


def update_init_download():
    threading.Thread(target=_update_download).start()


def init(addon_version=None, releases_url=None):
    global ADDON_VERSION
    global RELEASES_URL

    ADDON_VERSION = addon_version
    RELEASES_URL = releases_url

    update_init_check()
