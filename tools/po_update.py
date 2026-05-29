# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021-2026 Mikhail Rachinskiy

import re
from collections.abc import Iterator
from pathlib import Path

POHeader = dict[str, str]
POTranslation = dict[tuple[str, str], str]

PO_REF = "ru_RU.po"


def po_parse(text: str) -> tuple[POHeader, POTranslation]:
    header = {
        "Project-Id-Version": "",
        "POT-Creation-Date": "",
        "PO-Revision-Date": "",
        "Last-Translator": "",
        "Language-Team": "Mikhail Rachinskiy",
        "Language": "",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
    }

    for k, v in header.items():
        if not v:
            s = re.search(f"{k}:" + r'\s(.+)\\n', text)
            if s is not None and s.group(1):
                header[k] = s.group(1)

    concat_multiline = text.replace('"\n"', "")
    entries = re.findall(r'(?:msgctxt\s*"(.+)")?\s*msgid\s*"(.+)"\s*msgstr\s*"(.*)"', concat_multiline)

    return header, {
        (ctxt or "*", key.replace("\\n", "\n")): msg.replace("\\n", "\n")
        for ctxt, key, msg in entries
        if msg
    }


def po_get(po_file: Path) -> tuple[POHeader, POTranslation]:
    with open(po_file, "r", encoding="utf-8") as file:
        return po_parse(file.read())


def po_walk(po_dir) -> Iterator[tuple[str, POHeader, POTranslation]]:
    for child in po_dir.iterdir():
        if child.is_file() and child.suffix == ".po" and child.name != PO_REF:
            header, translation = po_get(child)
            yield child.stem, header, translation


def po_update(po_dir: Path, po_ref: tuple[POHeader, POTranslation]) -> Iterator[tuple[str, str, int]]:
    ref_h, ref_d = po_ref
    text_all = len(ref_d)

    for name, header, dictionary in po_walk(po_dir):
        text = ""
        text_complete = 0

        # Header

        text += 'msgid ""'
        text += '\nmsgstr ""'

        for k in ("Project-Id-Version", "POT-Creation-Date"):
            header[k] = ref_h[k]

        for k, v in header.items():
            text += f'\n"{k}: {v}\\n"'

        text += "\n"

        # Entries

        for ref_key, _ in ref_d.items():

            if ref_key in dictionary.keys():
                text_complete += 1

            msgid = ref_key[1].replace("\n", "\\n").strip()
            msgstr = dictionary.get(ref_key, "").replace("\n", "\\n").strip()

            if ref_key[0] != "*":
                text += f'\nmsgctxt "{ref_key[0]}"'

            text += f'\nmsgid "{msgid}"'
            text += f'\nmsgstr "{msgstr}"'
            text += "\n"

        yield name, text, int(text_complete * 100 / text_all)


def main() -> None:
    po_dir = Path(__file__).parent.parent / "source" / "localization"
    po_ref = po_get(po_dir / PO_REF)

    results: list[str, int] = []
    for name, text, percent in po_update(po_dir, po_ref):
        with open(po_dir / (name + ".po"), "w", encoding="utf-8", newline="\n") as file:
            file.write(text)
            results.append((name, percent))

    for name, percent in sorted(results, key=lambda x: x[1], reverse=True):
        print(f"{percent}%", name)

    input("\nDONE\n")


main()
