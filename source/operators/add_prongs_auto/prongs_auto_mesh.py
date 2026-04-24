# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from itertools import combinations
from statistics import median

from mathutils import Matrix, Vector

from ...lib import asset
from ...lib import unit
from ..add_prongs import prongs_mesh

_EPS = 1e-6
_BUMP_SCALE = 0.5
_TAPER = 0.0
_DETALIZATION = 32
_SIZE_ROUND_MM = 0.025
_MAX_CONNECTIONS = 2048
_MAX_PRONGS = 4096


@dataclass(slots=True)
class GemInfo:
    location: Vector
    radius: float
    matrix: Matrix
    normal: Vector


@dataclass(slots=True)
class ConnectionInfo:
    first: GemInfo
    second: GemInfo
    first_point: Vector
    second_point: Vector


@dataclass(slots=True)
class ProngInfo:
    position: Vector
    normal: Vector
    size: float
    height: float
    matrix: Matrix


def create_prongs_auto(
    gems,
    size_ratio: float,
    height_ratio: float,
    width_between_prongs: float,
    uniformity: float,
    max_gap: float,
    weld_distance: float,
) -> list[ProngInfo]:
    size_ratio = _clamp(size_ratio, 0.1, 0.5)
    height_ratio = _clamp(height_ratio, 0.1, 1.0)
    width_between_prongs = _clamp(width_between_prongs, 0.1, 1.0)
    uniformity = _clamp(uniformity, 0.0, 1.0)
    max_gap = max(0.0, max_gap)
    weld_distance = max(0.0, weld_distance)

    gem_infos = [_to_gem_info(ob) for ob in gems]
    connections = _find_valid_connections(gem_infos, max_gap)

    if not connections:
        return []

    prong_infos = _create_prong_infos(connections, size_ratio, height_ratio, width_between_prongs)

    if weld_distance > 0.0 and len(prong_infos) > 1:
        prong_infos = _merge_nearby_prongs(prong_infos, weld_distance)

    if uniformity > 0.0 and len(prong_infos) > 1:
        prong_infos = _apply_uniformity(prong_infos, uniformity)

    if len(prong_infos) > _MAX_PRONGS:
        raise ValueError("Too many prongs generated. Reduce Max Gap or selection size")

    return prong_infos


def create_prong_mesh(info: ProngInfo):
    return prongs_mesh.create_prong(
        info.size,
        info.height,
        info.height,
        _BUMP_SCALE,
        _TAPER,
        _DETALIZATION,
    )


def _to_gem_info(ob) -> GemInfo:
    loc, rot, _sca = ob.matrix_world.decompose()
    matrix = Matrix.LocRotScale(loc, rot, (1.0, 1.0, 1.0))
    normal = matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))

    if normal.length_squared <= _EPS:
        normal = Vector((0.0, 0.0, 1.0))
    else:
        normal.normalize()

    radius = max(ob.dimensions.x, ob.dimensions.y) / 2

    return GemInfo(loc.copy(), radius, matrix, normal)


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


def _create_prong_infos(
    connections: list[ConnectionInfo],
    size_ratio: float,
    height_ratio: float,
    width_between_prongs: float,
) -> list[ProngInfo]:
    unit_scale = unit.Scale()
    prong_infos = []
    app = prong_infos.append

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

        half_width = avg_diameter * width_between_prongs * 0.5
        size = _round_size(unit_scale, avg_diameter * size_ratio)
        height = avg_diameter * height_ratio
        if size <= _EPS or height <= _EPS:
            continue

        offset = perpendicular * half_width
        matrix = Matrix.Translation(midpoint - offset) @ normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
        app(ProngInfo((midpoint - offset).copy(), normal.copy(), size, height, matrix))

        matrix = Matrix.Translation(midpoint + offset) @ normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
        app(ProngInfo((midpoint + offset).copy(), normal.copy(), size, height, matrix))

    return prong_infos


def _merge_nearby_prongs(prongs: list[ProngInfo], weld_distance: float) -> list[ProngInfo]:
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
            if (base.position - prongs[j].position).length < weld_distance:
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

        position = Vector((0.0, 0.0, 0.0))
        normal = Vector((0.0, 0.0, 0.0))
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
        size = _round_size(unit_scale, size)

        if normal.length_squared <= _EPS:
            normal = group[0].normal.copy()
        else:
            normal.normalize()

        matrix = Matrix.Translation(position) @ normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
        app(ProngInfo(position, normal, size, height, matrix))

    return merged


def _round_size(unit_scale: unit.Scale, size: float) -> float:
    if size <= _EPS:
        size_mm = _SIZE_ROUND_MM
    else:
        size_mm = unit_scale.from_scene(size)
        size_mm = round(size_mm / _SIZE_ROUND_MM) * _SIZE_ROUND_MM
        size_mm = max(size_mm, _SIZE_ROUND_MM)

    return unit_scale.to_scene(size_mm)


def _apply_uniformity(prongs: list[ProngInfo], uniformity: float) -> list[ProngInfo]:
    unit_scale = unit.Scale()
    median_size = median(info.size for info in prongs)
    median_height = median(info.height for info in prongs)
    normalized = []
    app = normalized.append

    for info in prongs:
        size = _lerp(info.size, median_size, uniformity)
        height = _lerp(info.height, median_height, uniformity)
        size = _round_size(unit_scale, size)
        height = max(height, _EPS)
        app(ProngInfo(info.position, info.normal, size, height, info.matrix.copy()))

    return normalized


def _lerp(current: float, target: float, factor: float) -> float:
    return current + (target - current) * factor


def _clamp(value: float, minimum: float, maximum: float) -> float:
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value