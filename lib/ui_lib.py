# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
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


from __future__ import annotations
from typing import List


def popup_report(self, context, msg: str = "", title: str = "", icon: str = "INFO") -> None:

    def draw(self, context):
        self.layout.label(text=msg)

    self.report({"INFO"}, f"{title}: {msg}")
    context.window_manager.popup_menu(draw, title=title, icon=icon)


def popup_report_batch(self, context, msgs: List[str] = None, title: str = "", icon: str = "INFO") -> None:

    def draw(self, context):
        layout = self.layout
        for text in msgs:
            layout.label(text=text)

    self.report({"OPERATOR"}, f"{title}:")

    for text in msgs:
        self.report({"INFO"}, text)

    context.window_manager.popup_menu(draw, title=title, icon=icon)
