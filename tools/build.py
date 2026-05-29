# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024-2026 Mikhail Rachinskiy

import subprocess
import tomllib
from pathlib import Path

BL_PATH = Path("~/blender-4.5/blender.exe").expanduser()


def get_manifest(path: Path) -> dict[str, str]:
    filepath = path / "blender_manifest.toml"

    with open(filepath, "rb") as file:
        return tomllib.load(file)


def build(src_dir: Path, out_dir: Path) -> None:
    cmd = f"{BL_PATH} --command extension build --source-dir={src_dir} --output-dir={out_dir}"
    subprocess.run(cmd, shell=True, capture_output=True)


def find_by_ext(folder: Path, ext: str) -> str:
    for entry in folder.iterdir():
        if entry.suffix == ext:
            return entry.name

    raise FileNotFoundError


def server_gen(src_dir: Path, package_dir: Path) -> list[str]:
    cmd = f"{BL_PATH} --command extension server-generate --repo-dir={package_dir}"
    subprocess.run(cmd, shell=True, capture_output=True)

    # Edit download url
    # --------------------------
    zip_name = find_by_ext(package_dir, ".zip")
    json_name = find_by_ext(package_dir, ".json")

    manifest = get_manifest(src_dir)
    addon_ver = manifest["version"]
    min_ver = manifest["blender_version_min"]
    old_url = f"./{zip_name}"
    new_url = f"https://github.com/mrachinskiy/jewelcraft/releases/download/v{addon_ver}-blender{min_ver}/{zip_name}"

    with open(package_dir / json_name, "r") as file:
        contents = file.read().replace(old_url, new_url)

    with open(package_dir / json_name, "w", newline="\n") as file:
        file.write(contents)

    return sorted((zip_name, json_name))


def main() -> None:
    print(" ░ ...")

    current_dir = Path(__file__).parent
    src_dir = current_dir.parent / "source"

    build(src_dir, current_dir)
    files = server_gen(src_dir, current_dir)

    input("".join(f" █ {x}\n" for x in files))


main()
