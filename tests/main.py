# SPDX-FileCopyrightText: 2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from pathlib import Path

TEST_VERSIONS = {
    (4, 2),
    (4, 3),
    (4, 4),
    (4, 5),
}

# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
INVERSE = "\033[7m"
RESET = "\033[0m"

# Messages
FAILED = RED + INVERSE + "FAILED" + RESET
PASSED = GREEN + INVERSE + "PASSED" + RESET


def error(text: str) -> str:
    return RED + text + RESET


def ver_tuple(ver: str) -> tuple[int]:
    return tuple(int(x) for x in ver.split("-")[1].replace(".", ""))


blender_paths = []
for entry in Path().home().iterdir():
    if entry.is_dir() and entry.name.startswith("blender") and ver_tuple(entry.name) in TEST_VERSIONS:
        blender_paths.append(entry / "blender.exe")


print("======================================================")

for entry in Path(__file__).parent.iterdir():
    if entry.is_file() and entry.suffix == ".py" and entry.name.startswith("test"):
        for blender in blender_paths:
            cmd = [blender, "-b", "-P", entry]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode:
                print(f"{error(blender.parent.name)} {error(entry.stem)} {FAILED}")
                print(proc.stderr.decode().strip())
                break
            else:
                print(f"{blender.parent.name} {entry.stem} {PASSED}")

input("======================================================\n")
