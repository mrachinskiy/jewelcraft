# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path


def tag(value, tag_name: str) -> str:
    return f"<{tag_name}>{value}</{tag_name}>"


def tag_row(values: tuple, tag_name: str = "td") -> str:
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

    def write_table(self, header: tuple, body: list[tuple], footer: tuple) -> None:
        header = tag_row(header, "th")
        body = "".join(tag_row(x) for x in body)

        self.contents.append(self.template["table"].format(header, body, *footer))

    def write_list(self, values: list[tuple]) -> None:
        self.contents.append(self.template["list"].format("".join(tag_row(x) for x in values)))

    def write_img(self, img: str) -> None:
        self.contents.append(self.template["img"].format(img))

    def write_section(self, title: str) -> None:
        self.sections.append(self.template["section"].format(title, "".join(self.contents)))
        self.contents.clear()

    def write_section_meta(self) -> None:
        self.sections.append(self.template["section_meta"].format("".join(self.contents)))
        self.contents.clear()

    def make(self, title: str) -> str:
        return self.template["document"].format(title, self.template["styles"], "".join(self.sections))
