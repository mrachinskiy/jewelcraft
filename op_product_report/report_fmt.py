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
from ..lib import unit, asset, gettext


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


def data_format(context, data):
    prefs = context.preferences.addons[var.ADDON_ID].preferences
    _ = gettext.GetText(context).gettext
    _mm = _("mm")
    _g = _("g")
    _pcs = _("pcs")
    _ct = _("ct.")
    report = ""

    if data["size"]:
        report += _("Size") + ":\n"
        report += "    {} {}\n\n".format(round(data["size"], 2), _mm)

    if data["shank"]:
        report += _("Shank") + ":\n"
        report += "    {} × {} {}\n\n".format(*[round(x, 2) for x in data["shank"]], _mm)

    if data["dim"]:
        report += _("Dimensions") + ":\n"
        report += "    {} × {} × {} {}\n\n".format(*[round(x, 2) for x in data["dim"]], _mm)

    if data["weight"]:

        vol = data["weight"]

        # Format values
        # ---------------------------

        volf = "{} {}".format(round(vol, 4), _("mm³"))

        materialsf = [(volf, _("Volume"))]
        col_width = len(volf)

        for mat in prefs.weighting_materials.values():
            if mat.enabled:
                density = unit.convert(mat.density, "CM3_TO_MM3")
                weight = round(vol * density, 2)
                weightf = f"{weight} {_g}"

                materialsf.append((weightf, mat.name))
                col_width = max(col_width, len(weightf))

        # Format list
        # ---------------------------

        report += _("Weight") + ":\n"

        for value, name in materialsf:
            report += f"    {value:{col_width}}  {name}\n"

        report += "\n"

    if data["gems"]:

        gemsf = []
        table_heading = (_("Gem"), _("Cut"), _("Size"), _("Qty"))
        cols_width = [len(x) for x in table_heading]

        for (stone, cut, size), qty in sorted(
            data["gems"].items(),
            key=lambda x: (x[0][0], x[0][1], -x[0][2][1], -x[0][2][0]),
        ):
            # Values
            # ---------------------------

            ct = _ct_calc(stone, cut, l=size[1], w=size[0], h=size[2])
            qty_ct = round(qty * ct, 3)

            # Format
            # ---------------------------

            l = asset.to_int(size[1])
            w = asset.to_int(size[0])

            stonef = _(asset.get_name(stone))
            cutf = _(asset.get_name(cut))
            qtyf = "{} {} ({} {})".format(qty, _pcs, qty_ct, _ct)

            if cut in var.CUT_SIZE_SINGLE:
                sizef = "{} {} ({} {})".format(l, _mm, ct, _ct)
            else:
                sizef = "{} × {} {} ({} {})".format(l, w, _mm, ct, _ct)

            gemf = (stonef, cutf, sizef, qtyf)
            gemsf.append(gemf)

            # Columns width
            # ---------------------------

            for i, width in enumerate(cols_width):
                cols_width[i] = max(width, len(gemf[i]))

        # Format table
        # ---------------------------

        row = "    {{:{}}} | {{:{}}} | {{:{}}} | {{}}\n".format(*cols_width)
        sep = "—" * (sum(cols_width) + 10)

        report += _("Settings") + ":\n"
        report += row.format(*table_heading)
        report += f"    {sep}\n"

        for gemf in gemsf:
            report += row.format(*gemf)

    return report
