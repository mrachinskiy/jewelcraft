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


def spot_last(iterable):
    iterator = iter(iterable)
    ret = next(iterator)

    for value in iterator:
        yield False, ret
        ret = value

    yield True, ret


def pairwise(iterable):
    import itertools
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def pairwise_cyclic(a):
    import itertools
    b = itertools.cycle(a)
    next(b)
    return zip(a, b)


def quadwise_cyclic(a1, b1):
    import itertools
    a2 = itertools.cycle(a1)
    next(a2)
    b2 = itertools.cycle(b1)
    next(b2)
    return zip(a2, a1, b1, b2)
