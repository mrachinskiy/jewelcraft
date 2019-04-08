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


from math import pi

from .. import var
from ..lib import unit, asset


def _to_int(x):
    if x.is_integer():
        return int(x)
    return x


def _ct_calc(stone, cut, l, w, h):
    dens = var.STONE_DENSITY.get(stone)
    corr = var.CUT_VOLUME_CORRECTION.get(cut)

    if not dens or not corr:
        return 0

    dens = unit.convert(dens, "CM3_TO_MM3")

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


class DataFormat:

    def data_format(self, data):
        _ = self.gettext
        report = ""

        if data["size"]:
            report += "{}:\n".format(_("Size"))
            report += "    {} {}\n\n".format(round(data["size"], 2), _("mm"))

        if data["shank"]:
            report += "{}:\n".format(_("Shank"))
            report += "    {} × {} {}\n\n".format(*[round(x, 2) for x in data["shank"]], _("mm"))

        if data["dim"]:
            report += "{}:\n".format(_("Dimensions"))
            report += "    {} × {} × {} {}\n\n".format(*[round(x, 2) for x in data["dim"]], _("mm"))

        if data["weight"]:

            vol = data["weight"]

            # Format values
            # ---------------------------
            volf = "{} {}".format(round(vol, 4), _("mm³"))

            materialsf = [(volf, _("Volume"))]
            col_width = len(volf)

            for mat in self.prefs.weighting_materials.values():
                if mat.enabled:
                    density = unit.convert(mat.density, "CM3_TO_MM3")
                    weight = round(vol * density, 2)
                    weightf = "{} {}".format(weight, _("g"))

                    materialsf.append((weightf, mat.name))
                    col_width = max(col_width, len(weightf))

            # Format list
            # ---------------------------
            report += "{}:\n".format(_("Weight"))
            row = "    {value:{width}}  {name}\n"

            for value, name in materialsf:
                report += row.format(width=col_width, value=value, name=name)

            report += "\n"

        if data["gems"]:

            gemsf = []
            table_heading = (_("Gem"), _("Cut"), _("Size"), _("Qty"))
            cols_width = [len(x) for x in table_heading]

            for (stone, cut, size), qty in sorted(data["gems"].items(), key=lambda x: x[0]):

                # Values
                # ---------------------------
                ct = _ct_calc(stone, cut, l=size[1], w=size[0], h=size[2])
                qty_ct = round(qty * ct, 3)

                # Format
                # ---------------------------
                stonef = _(asset.get_name(stone))
                cutf = _(asset.get_name(cut))
                qtyf = "{} {} ({} {})".format(qty, _("pcs"), qty_ct, _("ct."))

                if cut in {"ROUND", "SQUARE", "ASSCHER", "OCTAGON", "FLANDERS"}:
                    sizef = "{} {} ({} {})".format(_to_int(size[1]), _("mm"), ct, _("ct."))
                else:
                    sizef = "{} × {} {} ({} {})".format(_to_int(size[1]), _to_int(size[0]), _("mm"), ct, _("ct."))

                gemf = (stonef, cutf, sizef, qtyf)
                gemsf.append(gemf)

                # Columns width
                # ---------------------------
                for i, width in enumerate(cols_width):
                    cols_width[i] = max(width, len(gemf[i]))

            # Format table
            # ---------------------------
            row = "    {{:{}}} | {{:{}}} | {{:{}}} | {{}}\n".format(*cols_width)

            report += "{}:\n".format(_("Settings"))
            report += row.format(*table_heading)
            report += "    {}\n".format("—" * (sum(cols_width) + 10))

            for gemf in gemsf:
                report += row.format(*gemf)

        return report
