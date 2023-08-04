# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from typing import Any
from collections.abc import Iterator


def spot_last(iterable) -> Iterator[tuple[bool, Any]]:
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
