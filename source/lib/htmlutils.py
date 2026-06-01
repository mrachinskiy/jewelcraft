# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2015-2026 Mikhail Rachinskiy

from pathlib import Path


def _tag(tag_name: str, value) -> str:
    return f"<{tag_name}>{value}</{tag_name}>"


def _tr(values: tuple, cell_tag: str = "td") -> str:
    return _tag("tr", "".join(_tag(cell_tag, v) for v in values))


def _minify(s: str) -> str:
    return s.replace("    ", "").replace("\n", "")


class Document:
    __slots__ = "template", "sections", "contents"

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
            self.template["warning"].format(title, "\n        ".join(_tag("li", x) for x in warns))
        )

    def write_table(self, header: tuple, body: list[tuple], footer: tuple) -> None:
        header = _tr(header, cell_tag="th")
        body = "\n        ".join(_tr(x) for x in body)
        self.contents.append(self.template["table"].format(header, body, *footer))

    def write_list(self, values: list[tuple]) -> None:
        self.contents.append(self.template["list"].format("\n        ".join(_tr(x) for x in values)))

    def write_img(self, image: str) -> None:
        self.contents.append(f'<img src="data:image/webp;base64,{image}" alt="">\n')

    def write_section(self, title: str) -> None:
        self.sections.append(self.template["section"].format(title, "".join(self.contents).strip()))
        self.contents.clear()

    def write_section_meta(self) -> None:
        self.sections.append(self.template["section_meta"].format("".join(self.contents).strip()))
        self.contents.clear()

    def make(self, title: str) -> str:
        return self.template["document"].format(title, _minify(self.template["styles"]), "\n".join(self.sections).strip())
