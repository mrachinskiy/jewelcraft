# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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
