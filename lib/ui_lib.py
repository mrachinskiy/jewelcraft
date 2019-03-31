# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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


import bpy


def popup_report(self, text="", title="", icon="INFO"):

    def draw(self, context):
        self.layout.label(text=text)

    self.report({"INFO"}, f"{title}: {text}")
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def popup_report_batch(self, data=None, title="", icon="INFO"):

    def draw(self, context):
        layout = self.layout
        for text in data:
            layout.label(text=text)

    self.report({"INFO"}, f"{title}:\n")
    for text in data:
        self.report({"INFO"}, text)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
