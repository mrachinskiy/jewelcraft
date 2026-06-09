# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Artem Viveritsa
# SPDX-FileContributor: Modified by Mikhail Rachinskiy

from itertools import combinations
from statistics import median
from typing import NamedTuple

import bl_math
from mathutils import Matrix, Vector

from ...lib import asset, unit

_EPS = 1e-6
_MAX_CONNECTIONS = 2048
_MAX_PRONGS = 4096
_CHAIN_MAX_CONNECTIONS = 2
_CHAIN_CURVATURE_SHIFT_FACTOR = 0.25
_CHAIN_CURVATURE_SIZE_FACTOR = 0.25


class GemInfo(NamedTuple):
    location: Vector
    radius: float
    matrix: Matrix
    normal: Vector


class ConnectionInfo(NamedTuple):
    first: GemInfo
    second: GemInfo
    first_point: Vector
    second_point: Vector


class ProngInfo(NamedTuple):
    position: Vector
    normal: Vector
    size: float
    height: float
    matrix: Matrix


def create_prongs_auto(
    gems,
    size_ratio: float,
    height_ratio: float,
    gap: float,
    uniformity: float,
    max_gap: float,
    merge_distance: float,
    size_step: float,
) -> list[ProngInfo]:
    gem_infos = [_to_gem_info(ob) for ob in gems]
    connections = _find_valid_connections(gem_infos, max_gap)

    if not connections:
        return []

    prong_infos = _create_prong_infos(connections, size_ratio, height_ratio, gap, size_step)

    if merge_distance and len(prong_infos) > 1:
        prong_infos = _merge_nearby_prongs(prong_infos, merge_distance, size_step)

    if uniformity and len(prong_infos) > 1:
        prong_infos = _apply_uniformity(prong_infos, uniformity, size_step)

    if len(prong_infos) > _MAX_PRONGS:
        raise ValueError("Too many prongs generated. Reduce Max Gap or selection size")

    return prong_infos


def _to_gem_info(ob) -> GemInfo:
    loc, rot, _ = ob.matrix_world.decompose()
    mat = Matrix.LocRotScale(loc, rot, (1.0, 1.0, 1.0))
    nor = mat.to_3x3() @ Vector((0.0, 0.0, 1.0))

    if nor.length_squared <= _EPS:
        nor = Vector((0.0, 0.0, 1.0))
    else:
        nor.normalize()

    rad = max(ob.dimensions.xy) / 2.0

    loc.freeze()
    mat.freeze()
    nor.freeze()

    return GemInfo(loc, rad, mat, nor)


def _find_valid_connections(gems: list[GemInfo], max_gap: float) -> list[ConnectionInfo]:
    connections = []
    app = connections.append

    for first, second in combinations(gems, 2):
        dist_locs = (first.location - second.location).length
        first_point, second_point = asset.nearest_coords(first.radius, second.radius, first.matrix, second.matrix)
        gap = asset.calc_gap(first_point, second_point, first.location, dist_locs, first.radius)

        if gap <= max_gap:
            app(ConnectionInfo(first, second, first_point, second_point))
            if len(connections) > _MAX_CONNECTIONS:
                raise ValueError("Too many gem connections found. Reduce Max Gap or selection size")

    return connections


def _chain_curvature_ratio(
    connection: ConnectionInfo, neighbor_map: dict[GemInfo, list[GemInfo]], width_direction: Vector, avg_diameter: float
) -> float:

    if avg_diameter <= _EPS:
        return 0.0

    first_neighbors = neighbor_map.get(connection.first, ())
    second_neighbors = neighbor_map.get(connection.second, ())

    if len(first_neighbors) > _CHAIN_MAX_CONNECTIONS or len(second_neighbors) > _CHAIN_MAX_CONNECTIONS:
        return 0.0

    extra_locations = []

    prev_neighbors = [info for info in first_neighbors if info is not connection.second]
    next_neighbors = [info for info in second_neighbors if info is not connection.first]

    if len(prev_neighbors) == 1:
        extra_locations.append(prev_neighbors[0].location)
    if len(next_neighbors) == 1:
        extra_locations.append(next_neighbors[0].location)

    if not extra_locations:
        return 0.0

    neighbors_center = Vector()
    for location in extra_locations:
        neighbors_center += location
    neighbors_center /= len(extra_locations)

    chord_midpoint = (connection.first.location + connection.second.location) * 0.5
    ratio = (neighbors_center - chord_midpoint).dot(width_direction) / avg_diameter

    return max(-1.0, min(ratio, 1.0))


def _create_prong_infos(
    connections: list[ConnectionInfo], size_ratio: float, height_ratio: float, gap: float, size_step: float
) -> list[ProngInfo]:

    Scale = unit.Scale()
    prong_infos = []
    app = prong_infos.append
    neighbor_map = {}

    for connection in connections:
        neighbor_map.setdefault(connection.first, []).append(connection.second)
        neighbor_map.setdefault(connection.second, []).append(connection.first)

    for connection in connections:
        axis = connection.second_point - connection.first_point
        if axis.length_squared <= _EPS:
            axis = connection.second.location - connection.first.location
            if axis.length_squared <= _EPS:
                continue

        axis.normalize()

        normal = connection.first.normal + connection.second.normal
        if normal.length_squared <= _EPS:
            normal = connection.first.normal.copy()
            if normal.length_squared <= _EPS:
                normal = Vector((0.0, 0.0, 1.0))
        normal.normalize()

        perpendicular = axis.cross(normal)
        if perpendicular.length_squared <= _EPS:
            perpendicular = normal.cross(Vector((1.0, 0.0, 0.0)))
            if perpendicular.length_squared <= _EPS:
                perpendicular = normal.cross(Vector((0.0, 1.0, 0.0)))
                if perpendicular.length_squared <= _EPS:
                    continue
        perpendicular.normalize()

        midpoint = connection.first_point.lerp(connection.second_point, 0.5)
        avg_diameter = connection.first.radius + connection.second.radius
        if avg_diameter <= _EPS:
            continue

        half_width = avg_diameter * gap * 0.5
        size = avg_diameter * size_ratio
        height = avg_diameter * height_ratio
        if size <= _EPS or height <= _EPS:
            continue

        rotation = normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
        curvature_ratio = _chain_curvature_ratio(connection, neighbor_map, perpendicular, avg_diameter)
        outward_sign = -1.0 if curvature_ratio > 0.0 else 1.0
        shift_magnitude = abs(curvature_ratio) * _CHAIN_CURVATURE_SHIFT_FACTOR * half_width
        size_delta = abs(curvature_ratio) * _CHAIN_CURVATURE_SIZE_FACTOR

        for spread_direction in (-1.0, 1.0):
            position = midpoint + (perpendicular * (half_width * spread_direction))
            prong_size = size

            if curvature_ratio:
                position += perpendicular * (outward_sign * shift_magnitude)
                is_inner = (spread_direction * curvature_ratio) > 0.0
                prong_size *= 1.0 - size_delta if is_inner else 1.0 + size_delta

            prong_size = _round_size(Scale, prong_size, size_step)
            matrix = Matrix.Translation(position) @ rotation
            app(ProngInfo(position.copy(), normal.copy(), prong_size, height, matrix))

    return prong_infos


def _merge_nearby_prongs(prongs: list[ProngInfo], merge_distance: float, size_step: float) -> list[ProngInfo]:
    unit_scale = unit.Scale()
    parent = list(range(len(prongs)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first: int, second: int) -> None:
        root_first = find(first)
        root_second = find(second)
        if root_first != root_second:
            parent[root_second] = root_first

    for i, base in enumerate(prongs):
        for j in range(i + 1, len(prongs)):
            if (base.position - prongs[j].position).length < merge_distance:
                union(i, j)

    groups = {}

    for index in range(len(prongs)):
        root = find(index)
        groups.setdefault(root, []).append(prongs[index])

    merged = []
    app = merged.append

    for group in groups.values():
        if len(group) == 1:
            app(group[0])
            continue

        position = Vector()
        normal = Vector()

        size = 0.0
        height = 0.0

        for info in group:
            position += info.position
            normal += info.normal
            size += info.size
            height += info.height

        count = len(group)
        position /= count
        size /= count
        height /= count
        size = _round_size(unit_scale, size, size_step)

        if normal.length_squared <= _EPS:
            normal = group[0].normal.copy()
        else:
            normal.normalize()

        matrix = Matrix.Translation(position) @ normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
        app(ProngInfo(position, normal, size, height, matrix))

    return merged


def _round_size(Scale: unit.Scale, size: float, size_step: float) -> float:
    if size <= _EPS:
        size_mm = size_step
    else:
        size_mm = Scale.from_scene(size)
        size_mm = round(size_mm / size_step) * size_step
        size_mm = max(size_mm, size_step)

    return Scale.to_scene(size_mm)


def _apply_uniformity(prongs: list[ProngInfo], uniformity: float, size_step: float) -> list[ProngInfo]:
    unit_scale = unit.Scale()
    median_size = median(info.size for info in prongs)
    median_height = median(info.height for info in prongs)
    normalized = []
    app = normalized.append

    for info in prongs:
        size = bl_math.lerp(info.size, median_size, uniformity)
        height = bl_math.lerp(info.height, median_height, uniformity)
        size = _round_size(unit_scale, size, size_step)
        height = max(height, _EPS)
        app(ProngInfo(info.position, info.normal, size, height, info.matrix.copy()))

    return normalized
