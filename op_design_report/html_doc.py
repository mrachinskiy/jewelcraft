# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from collections.abc import Callable

from .. import var
from ..lib import htmlutils


def make(Report, filename: str, _: Callable[[str], str]) -> str:
    Doc = htmlutils.Document(var.HTML_DESIGN_REPORT_DIR)

    if Report.preview:
        Doc.write_img(Report.preview)

    if Report.metadata:
        Doc.write_list(Report.metadata)

    if Doc.contents:
        Doc.write_section_meta()

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
