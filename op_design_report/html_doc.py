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


from collections.abc import Callable

from .. import var
from ..lib import htmlutils


def make(Report, filename: str, _: Callable[[str], str]) -> str:
    Doc = htmlutils.Document(var.HTML_DESIGN_REPORT_DIR)

    if Report.gems:
        header = (
            _("Gem"),
            _("Cut"),
            _("Size (mm)"),
            _("Carats"),
            _("Qty"),
            _("Sum (ct)"),
        )
        body = Report.gems
        footer = (
            _("Total"),
            sum(x[4] for x in Report.gems),
            round(sum(x[5] for x in Report.gems), 3),
        )
        if Report.warnings:
            Doc.write_warning(_("WARNING"), (_(x) for x in Report.warnings))
        Doc.write_table(header, body, footer)
        Doc.write_section(_("Settings"))

    if Report.materials:
        Doc.write_list(Report.materials)
        Doc.write_section(_("Materials"))

    if Report.notes:
        Doc.write_list(Report.notes)
        Doc.write_section(_("Notes"))

    return Doc.make(filename)
