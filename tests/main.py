# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025-2026 Mikhail Rachinskiy

import os
import subprocess
import tomllib
from pathlib import Path

BLENDER_APPS_DIR = Path().home()
TESTS_DIR = Path(__file__).parent

# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
INVERSE = "\033[7m"
RESET = "\033[0m"


def print_info(s: str) -> None:
    print(f"{INVERSE} {s} {RESET}")


def print_err(s: str) -> None:
    print(f"{RED}{INVERSE} {s} {RESET}")


def str_to_ver(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.split(".")[:2] if x.isdigit())


def main() -> None:

    # Tests
    # --------------------

    tests = get_tests()

    # Blender apps
    # --------------------

    blender_apps = get_blender_apps()
    if not blender_apps:
        print_err("BLENDER VERSION NOT FOUND")
        return

    # Testing
    # --------------------

    make_examples = input_make_examples()

    print_info("BEGIN")

    for blender in blender_apps:
        for test in tests:
            cmd = [blender / "blender.exe", "-b", "-P", test]
            if make_examples:
                cmd += ["--", "--make_examples"]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode:
                print(f"{RED + blender.name} {test.stem} {INVERSE}FAILED{RESET}")
                print(proc.stderr.decode().strip())
                return
            else:
                print(f"{blender.name} {test.stem} {GREEN + INVERSE}PASSED{RESET}")

        if make_examples:
            break

    print_info("END")


def input_blender_ver() -> str:
    print_info("TEST SPECIFIC BLENDER VERSION?")
    _input = input(
        "\n"
        "DEFAULT: Manifest [blender_version_min]\n"
        "\n"
        "> "
    )
    os.system("cls")
    return _input.strip().lower()


def input_make_examples() -> bool:
    print_info("MAKE TEST EXAMPLES?")
    _input = input(
        "\n"
        "[ y ] Yes\n"
        "[ n ] No\n"
        "\n"
        "> "
    )
    os.system("cls")
    return _input.strip().lower() == "y"


def get_tests() -> list[Path]:
    tests = []
    for entry in TESTS_DIR.iterdir():
        if entry.is_file() and entry.suffix == ".py" and entry.name.startswith("test") and entry.stem != "test_performance":
            tests.append(entry)

    return tests


def get_blender_apps() -> list[Path]:
    blender_ver = input_blender_ver()

    if (use_specific_ver := bool(blender_ver)):
        ver = str_to_ver(blender_ver)
    else:
        with open(TESTS_DIR.parent / "source" / "blender_manifest.toml", "rb") as file:
            manifest = tomllib.load(file)
        ver = str_to_ver(manifest["blender_version_min"])

    apps = []
    for entry in BLENDER_APPS_DIR.iterdir():
        if entry.is_dir() and entry.name.startswith("blender"):
            app_ver = str_to_ver(entry.name.split("-")[1])
            if use_specific_ver:
                if app_ver == ver:
                    apps.append(entry)
            elif app_ver >= ver:
                apps.append(entry)

    return apps


main()
input()
