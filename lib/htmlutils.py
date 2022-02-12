# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from pathlib import Path
from typing import Union


Value = Union[str, int, float]
Row = tuple[Value]


def tag(value: Value, tag_name: str) -> str:
    return f"<{tag_name}>{value}</{tag_name}>"


def tag_row(values: Row, tag_name: str = "td") -> str:
    return tag("".join(tag(v, tag_name) for v in values), "tr")


class Document:
    __slots__ = ("template", "sections", "contents")

    def __init__(self, template_path: Path) -> None:
        self.template = {}
        self.sections = []
        self.contents = []

        for child in template_path.iterdir():
            if child.is_file() and child.suffix in {".html", ".css"}:
                with open(child, "r", encoding="utf-8") as file:
                    self.template[child.stem] = file.read()

    def write_warning(self, title: str, warns: list[str]) -> None:
        self.contents.append(
            self.template["warning"].format(title, "".join(tag(x, "li") for x in warns))
        )

    def write_table(self, header: Row, body: list[Row], footer: Row) -> None:
        header = tag_row(header, "th")
        body = "".join(tag_row(x) for x in body)

        self.contents.append(self.template["table"].format(header, body, *footer))

    def write_list(self, values: list[Row]) -> None:
        self.contents.append(self.template["list"].format("".join(tag_row(x) for x in values)))

    def write_section(self, title: str) -> None:
        self.sections.append(self.template["section"].format(title, "".join(self.contents)))
        self.contents.clear()

    def make(self, title: str) -> str:
        return self.template["document"].format(title, "".join(self.sections)).format(self.template["styles"])
