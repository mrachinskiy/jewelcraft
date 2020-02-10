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


from math import pi, modf

from .. import var
from ..lib import unit, asset, gettext


def _to_ring_size(cir, size_format):
    if size_format in {"US", "JP"}:
        size = round((cir - var.CIR_BASE_US) / var.CIR_STEP_US, 2)

        if size >= 0.0:

            if size_format == "US":
                return asset.to_int(size)

            for size_jp, size_us in enumerate(var.MAP_SIZE_JP_TO_US, start=1):
                if size_us - 0.2 < size < size_us + 0.2:
                    return size_jp

    if size_format == "UK":
        import string

        size_raw = (cir - var.CIR_BASE_UK) / var.CIR_STEP_UK

        if size_raw >= 0.0:
            fraction, integer = modf(size_raw)
            half_size = 0.25 < fraction < 0.75
            if fraction > 0.75:
                integer += 1.0

            if integer < len(string.ascii_uppercase):
                size = string.ascii_uppercase[int(integer)]
                if half_size:
                    size += " 1/2"
                return size

    if size_format == "CH":
        size = round(cir - 40.0, 2)
        if size >= 0.0:
            return asset.to_int(size)

    return "[NO CORRESPONDING SIZE]"


def data_format(self, context, data):
    _ = gettext.GetText(context, self.lang).gettext
    _mm = _("mm")
    _g = _("g")
    report = []

    if data["gems"]:

        table_heading = [_("Gem"), _("Cut"), _("Size"), _("Carats"), _("Qty")]

        if self.show_total_ct:
            table_heading.append(_("Total (ct.)"))

        col_width = [len(x) for x in table_heading]
        gemsf = []

        for (stone, cut, size), qty in sorted(
            data["gems"].items(),
            key=lambda x: (x[0][0], x[0][1], -x[0][2][1], -x[0][2][0]),
        ):
            # Values
            # ---------------------------

            ct = asset.ct_calc(stone, cut, size)
            w, l, h = size

            # Format values
            # ---------------------------

            try:
                stonef = _(var.STONES[stone].name)
                cutf = _(var.CUTS[cut].name)
                xy_symmetry = var.CUTS[cut].xy_symmetry
            except KeyError:
                stonef = stone
                cutf = cut
                xy_symmetry = False

            if xy_symmetry:
                sizef = str(l)
            else:
                sizef = f"{l} × {w}"

            ctf = str(ct)
            qtyf = str(qty)
            total_ctf = str(round(ct * qty, 3))

            gemf = (stonef, cutf, sizef, ctf, qtyf, total_ctf)
            gemsf.append(gemf)

            # Columns width
            # ---------------------------

            for i, width in enumerate(col_width):
                col_width[i] = max(width, len(gemf[i]))

        # Format report
        # ---------------------------

        row = ["{{:{}}}" if x < 2 else "{{:>{}}}" for x in range(len(col_width))]
        row = "   ".join(row).format(*col_width)
        row = f"    {row}\n"

        report_gems = _("Settings") + "\n\n"
        report_gems += row.format(*table_heading)
        report_gems += "\n"

        for gemf in gemsf:
            report_gems += row.format(*gemf)

        report.append(report_gems)

    if data["materials"]:

        # Format values
        # ---------------------------

        materialsf = []
        col_width = 0

        for (mat_name, density), vol in data["materials"].items():
            weight = round(vol * density, 2)
            weightf = f"{weight} {_g}"

            materialsf.append((mat_name, weightf))
            col_width = max(col_width, len(mat_name))

        # Format report
        # ---------------------------

        report_materials = _("Materials") + "\n\n"

        for name, value in materialsf:
            report_materials += f"    {name:{col_width}}   {value}\n"

        report.append(report_materials)

    if data["notes"]:

        # Format values
        # ---------------------------

        notesf = []
        col_width = 0

        for item_type, name, values in data["notes"]:

            if item_type == "DIMENSIONS":
                valuef = " × ".join([str(x) for x in values])
                valuef += f" {_mm}"

            elif item_type == "RING_SIZE":
                dia, size_format = values
                cir = dia * pi

                if size_format == "DIA":
                    valuef = f"{dia} {_mm}"
                elif size_format == "CIR":
                    valuef = f"{round(cir, 2)} {_mm}"
                else:
                    valuef = _to_ring_size(cir, size_format)

            notesf.append((name, valuef))
            col_width = max(col_width, len(name))

        # Format report
        # ---------------------------

        report_notes = _("Additional Notes") + "\n\n"

        for name, value in notesf:
            report_notes += f"    {name:{col_width}}  {value}\n"

        report.append(report_notes)

    return "\n\n".join(report)
