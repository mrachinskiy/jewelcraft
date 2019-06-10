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


from math import pi, modf

from .. import var
from ..lib import unit, asset, gettext


def _ct_calc(stone, cut, size):
    dens = var.STONE_DENSITY.get(stone)
    corr = var.CUT_VOLUME_CORRECTION.get(cut)

    if not dens or not corr:
        return 0

    dens = unit.convert(dens, "CM3_TO_MM3")
    l = size[1]
    w = size[0]
    h = size[2]

    if cut in {"ROUND", "OVAL", "PEAR", "MARQUISE", "OCTAGON", "HEART"}:
        vol = pi * (l / 2) * (w / 2) * (h / 3)  # Cone

    elif cut in {"SQUARE", "ASSCHER", "PRINCESS", "CUSHION", "RADIANT", "FLANDERS"}:
        vol = l * w * h / 3  # Pyramid

    elif cut in {"BAGUETTE", "EMERALD"}:
        vol = l * w * (h / 2)  # Prism

    elif cut in {"TRILLION", "TRILLIANT", "TRIANGLE"}:
        vol = l * w * h / 6  # Tetrahedron

    g = vol * corr * dens
    ct = unit.convert(g, "G_TO_CT")

    return round(ct, 3)


def _to_ring_size(cir, size_format):
    if size_format in {"US", "JP"}:
        size = (cir - var.CIR_BASE_US) / var.CIR_STEP_US

        if size >= 0.0:

            if size_format == "US":
                return asset.to_int(round(size, 2))

            for i, v in enumerate(var.MAP_SIZE_JP_TO_US):
                if 0.0 < abs(v - size) < 0.2:
                    return i + 1

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
            return size

    return "*OUT OF BOUNDS"


def data_format(self, context, data):
    _ = gettext.GetText(context, self.lang).gettext
    _mm = _("mm")
    _g = _("g")
    report = []

    if data["gems"]:

        gemsf = []
        table_heading = (_("Gem"), _("Cut"), _("Size"), _("Carats"), _("Qty"))
        col_width = [len(x) for x in table_heading]

        for (stone, cut, size), qty in sorted(
            data["gems"].items(),
            key=lambda x: (x[0][0], x[0][1], -x[0][2][1], -x[0][2][0]),
        ):
            # Values
            # ---------------------------

            ct = _ct_calc(stone, cut, size)
            l = size[1]
            w = size[0]

            # Format values
            # ---------------------------

            stonef = _(asset.get_name(stone))
            cutf = _(asset.get_name(cut))
            ctf = f"{ct}"
            qtyf = f"{qty}"

            if cut in var.CUT_SIZE_SINGLE:
                sizef = f"{l}"
            else:
                sizef = f"{l} × {w}"

            gemf = (stonef, cutf, sizef, ctf, qtyf)
            gemsf.append(gemf)

            # Columns width
            # ---------------------------

            for i, width in enumerate(col_width):
                col_width[i] = max(width, len(gemf[i]))

        # Format report
        # ---------------------------

        row = "    {{:{}}}   {{:{}}}   {{:{}}}   {{:{}}}   {{}}\n".format(*col_width)

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
