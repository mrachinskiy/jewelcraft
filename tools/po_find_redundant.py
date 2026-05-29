# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021-2026 Mikhail Rachinskiy

import re
from collections.abc import Iterator
from pathlib import Path

PO_REF = "ru_RU.po"


def po_msgids(po_file: Path) -> set[str]:
    with open(po_file, "r", encoding="utf-8") as file:
        return set(re.findall(r'msgid\s*"(.+)"', file.read()))


def get_msgs(path: Path) -> Iterator[set[str]]:
    for child in path.iterdir():
        if child.is_file() and child.suffix in {".py", ".json"}:
            with open(child, "r", encoding="utf8") as f:

                if child.suffix == ".py":
                    text = re.sub(r'("\n\s*")', "", f.read())
                    msgs = set()
                else:
                    text = f.read()
                    msgs = {child.stem}

                msgs |= set(re.findall(r'"(.+?)"', text))
                yield msgs

        elif child.is_dir() and not child.name.startswith((".", "__")):
            yield from get_msgs(child)


def main() -> None:
    src_dir = Path(__file__).parent.parent / "source"
    po_dir = src_dir / "localization"

    trns_msgs = po_msgids(po_dir / PO_REF)
    code_msgs = set.union(*get_msgs(src_dir))
    redundant_msgs = trns_msgs - code_msgs

    for msg in redundant_msgs:
        print(" █", msg)

    input(f"\n Found {len(redundant_msgs)} redundant translations\n")


main()
