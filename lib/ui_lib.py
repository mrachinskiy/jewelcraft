# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy


def popup_list(op, title: str, msgs: list, icon: str = "INFO") -> None:

    def draw(self, context):
        for text in msgs:
            self.layout.label(text=text)

    op.report({"INFO"}, f"{title}:")

    for text in msgs:
        op.report({"INFO"}, text)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
