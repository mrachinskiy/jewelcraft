# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Callable

from .. import var
from ..lib import htmlutils


def make(Report, preview: str | None, filename: str, _: Callable[[str], str]) -> str:
    Doc = htmlutils.Document(var.HTML_REPORT_DIR)

    if preview:
        Doc.write_img(preview)

    if Report.metadata:
        Doc.write_list(Report.metadata)

    if Doc.contents:
        Doc.write_section_meta()

    if Report.gems:
        header = (
            _("Gem"),
            _("Cut"),
            _("Color"),
            _("Size (mm)"),
            _("Carats"),
            _("Qty"),
            _("Sum (ct)"),
        )
        body = Report.gems
        footer = (
            _("Total"),
            sum(x.qty for x in Report.gems),
            round(sum(x.ct_sum for x in Report.gems), 3),
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
