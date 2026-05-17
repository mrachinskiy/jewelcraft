# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict, deque
from math import exp
from time import perf_counter
from typing import NamedTuple

import bpy
from bpy.types import Object
from mathutils import Matrix, Quaternion, Vector, kdtree

from . import unit

_TIMER_INTERVAL = 1 / 60
_BASE_STRENGTH = 10.0
_CONSTRAINT_PASSES = 7
_SNAP_RAY_EPSILON = 0.0001

_time_prev = 0.0


class _Gem(NamedTuple):
    ob: Object
    radius: float
    spacing: float
    locked: bool


def handler_toggle(self, context) -> None:
    if self.use_spacing:
        handler_add()
    else:
        handler_del()


def handler_add() -> None:
    if not bpy.app.timers.is_registered(_timer):
        bpy.app.timers.register(_timer, first_interval=0.0)


def handler_del() -> None:
    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)


# Utility
# -------------------------------------


def _quat_eq(a: Quaternion, b: Quaternion) -> bool:
    return a.rotation_difference(b).angle < 1e-6


def _is_active_translate_operator(context) -> bool:
    for operator in context.window.modal_operators:
        if operator.bl_idname == "TRANSFORM_OT_translate":
            return True
    return False


def _gem_mobility(gem: _Gem, dist: float, falloff: float) -> float:
    if gem.locked:
        return 0.0
    return _mobility(dist, falloff)


def _mobility(dist: float, falloff: float) -> float:
    return 1.0 - dist / falloff


def _delta_time() -> float:
    global _time_prev

    now = perf_counter()
    delta = min(now - _time_prev, 0.1)
    _time_prev = now

    return delta


# Main Loop
# -------------------------------------


def _timer() -> float | None:
    context = bpy.context
    wm_props = context.window_manager.jewelcraft

    if not wm_props.use_spacing:
        return None

    if not _is_active_translate_operator(context) or context.window_manager.is_interface_locked or context.mode != "OBJECT":
        return _TIMER_INTERVAL

    selected_gems = {ob for ob in context.selected_objects if "gem" in ob}
    if not selected_gems:
        return _TIMER_INTERVAL

    scene_props = context.scene.jewelcraft
    gems_info = _collect_gems(context, scene_props, selected_gems)
    if len(gems_info) < 2:
        return _TIMER_INTERVAL

    _apply_spacing(
        gems_info,
        selected_gems,
        scene_props.spacing_radius,
        scene_props.spacing_tether,
        scene_props.spacing_tolerance,
        scene_props.spacing_strength,
        _delta_time(),
    )

    return _TIMER_INTERVAL


def _collect_gems(context, props, selected: list[Object]) -> dict[Object, _Gem]:
    default_spacing = props.overlay_spacing
    use_overrides = props.overlay_use_overrides
    radius_thold = props.spacing_radius + 1.0

    colls = None
    if props.spacing_restrict_by_collection and selected:
        colls = {
            coll
            for ob in selected
            for coll in ob.users_collection
        }

    locs_selected = [ob.matrix_world.translation for ob in selected]
    info = {}
    for ob in context.visible_objects:
        if "gem" not in ob or not any((ob.matrix_world.translation - loc).length < radius_thold for loc in locs_selected):
            continue

        spacing = default_spacing
        locked = False
        if use_overrides and "gem_overlay" in ob:
            spacing = ob["gem_overlay"].get("spacing", default_spacing)
            locked |= ob["gem_overlay"].get("locked", False)

        if (colls is not None and colls.isdisjoint(set(ob.users_collection))):
            info[ob] = _Gem(ob, max(ob.dimensions.xy) / 2.0, spacing, True)
        else:
            locked |= ob in selected
            info[ob] = _Gem(ob, max(ob.dimensions.xy) / 2.0, spacing, locked)

    return info


def _apply_spacing(
    gems_info: dict[Object, _Gem],
    selected: set[Object],
    effect_radius: float,
    tether: float,
    tolerance: float,
    strength: float,
    delta_time: float,
) -> None:

    links = _build_links(gems_info, tether)
    distances = _distance_map(selected, links, effect_radius)
    if len(distances) <= len(selected):
        return

    offsets = {}

    for gem1, gem2, dist1, dist2 in _iter_link_pairs(gems_info, links, distances):
        offset1, offset2 = _spring_offsets(
            gem1,
            gem2,
            dist1,
            dist2,
            effect_radius,
            strength,
            delta_time,
        )

        if offset1.length_squared:
            offsets[gem1.ob] = offsets.get(gem1.ob, Vector()) + offset1
        if offset2.length_squared:
            offsets[gem2.ob] = offsets.get(gem2.ob, Vector()) + offset2

    offsets = _resolve_spacing_constraints(
        gems_info,
        links,
        distances,
        offsets,
        effect_radius,
        tolerance,
        strength,
        delta_time,
    )
    threshold = unit.Scale().to_scene(0.001)

    for ob, offset in offsets.items():
        if ob in selected or offset.length <= threshold:
            continue
        _move_gem(gems_info[ob], offset)


def _build_links(gems_info: dict[Object, _Gem], tether: float) -> dict[Object, list[Object]]:
    info = tuple(gems_info.values())
    max_radius = max(gem.radius for gem in info)
    links = defaultdict(list)

    kd_tree = kdtree.KDTree(len(info))

    for i1, gem in enumerate(info):
        kd_tree.insert(gem.ob.matrix_world.translation, i1)

    kd_tree.balance()

    for i1, gem1 in enumerate(info):
        search_radius = gem1.radius + max_radius + tether

        for _, i2, distance in kd_tree.find_range(gem1.ob.matrix_world.translation, search_radius):
            if i2 <= i1:
                continue

            gem2 = info[i2]
            if max(distance - gem1.radius - gem2.radius, 0.0) > tether:
                continue

            links[gem1.ob].append(gem2.ob)
            links[gem2.ob].append(gem1.ob)

    return links


def _distance_map(selected: set[Object], links: dict[Object, list[Object]], effect_radius: float) -> dict[Object, float]:
    distances = {ob: 0.0 for ob in selected}
    queue = deque(selected)

    while queue:
        ob = queue.popleft()

        for ob_next in links[ob]:
            if ob_next in selected:
                continue

            distance_next = min(
                (ob_next.matrix_world.translation - ob2.matrix_world.translation).length
                for ob2 in selected
            )

            if distance_next > effect_radius:
                continue

            if distance_next < distances.get(ob_next, float("inf")):
                distances[ob_next] = distance_next
                queue.append(ob_next)

    return distances


def _iter_link_pairs(gems_info: dict[Object, _Gem], links: dict[Object, list[Object]], distances: dict[Object, float]):
    for ob1, neighbors in links.items():
        gem1 = gems_info[ob1]
        dist1 = distances.get(ob1)
        if dist1 is None:
            continue

        for ob2 in neighbors:
            if ob2.as_pointer() <= ob1.as_pointer():
                continue

            gem2 = gems_info[ob2]
            dist2 = distances.get(ob2)
            if dist2 is None:
                continue

            yield gem1, gem2, dist1, dist2


def _spring_offsets(
    gem1: _Gem,
    gem2: _Gem,
    dist1: float,
    dist2: float,
    effect_radius: float,
    strength: float,
    delta_time: float,
) -> tuple[Vector, Vector]:

    offset_vector = gem2.ob.matrix_world.translation - gem1.ob.matrix_world.translation
    distance = offset_vector.length

    if distance:
        direction = offset_vector / distance
    else:
        direction = Vector((1.0, 0.0, 0.0))

    m1 = _gem_mobility(gem1, dist1, effect_radius)
    m2 = _gem_mobility(gem2, dist2, effect_radius)
    m_total = m1 + m2

    if not m_total:
        zero = Vector()
        return zero, zero

    target_distance = gem1.radius + gem2.radius + max(gem1.spacing, gem2.spacing)
    influence = max(_mobility(dist1, effect_radius), _mobility(dist2, effect_radius))
    alpha = 1.0 - exp(-_BASE_STRENGTH * strength * influence * delta_time)
    correction = direction * (distance - target_distance) * alpha

    return correction * (m1 / m_total), -correction * (m2 / m_total)


def _resolve_spacing_constraints(
    gems_info: dict[Object, _Gem],
    links: dict[Object, list[Object]],
    distances: dict[Object, float],
    offsets: dict[Object, Vector],
    effect_radius: float,
    tolerance: float,
    strength: float,
    delta_time: float,
) -> dict[Object, Vector]:

    constraint_alpha = 1.0 - exp(-_BASE_STRENGTH * strength * delta_time)
    if constraint_alpha <= 0.0:
        return offsets

    proposed: dict[Object, Vector] = {}

    for ob in distances:
        if gems_info[ob].locked:
            proposed[ob] = ob.matrix_world.translation.copy()
        else:
            proposed[ob] = ob.matrix_world.translation + offsets.get(ob, Vector())

    for _ in range(_CONSTRAINT_PASSES):
        changed = False

        for gem1, gem2, dist1, dist2 in _iter_link_pairs(gems_info, links, distances):
            if gem1.ob not in proposed or gem2.ob not in proposed or (gem1.locked and gem2.locked):
                continue

            spacing = max(gem1.spacing, gem2.spacing)
            compressed_spacing = spacing - min(tolerance, spacing)
            target_distance = gem1.radius + gem2.radius + compressed_spacing
            offset_vector = proposed[gem2.ob] - proposed[gem1.ob]
            distance = offset_vector.length

            if distance >= target_distance:
                continue

            if distance:
                direction = offset_vector / distance
            else:
                current_offset = gem2.ob.matrix_world.translation - gem1.ob.matrix_world.translation

                if current_offset.length_squared:
                    direction = current_offset.normalized()
                else:
                    direction = Vector((1.0, 0.0, 0.0))

            m1 = _gem_mobility(gem1, dist1, effect_radius)
            m2 = _gem_mobility(gem2, dist2, effect_radius)
            correction = direction * (target_distance - distance) * constraint_alpha
            m_total = m1 + m2

            if not m_total:
                continue

            if m1:
                proposed[gem1.ob] -= correction * (m1 / m_total)
            if m2:
                proposed[gem2.ob] += correction * (m2 / m_total)

            changed = True

        if not changed:
            break

    return {
        ob: loc - ob.matrix_world.translation
        for ob, loc in proposed.items() if not gems_info[ob].locked
    }


def _move_gem(gem: _Gem, offset: Vector) -> bool:
    x, y, z = gem.ob.lock_location
    offset = Vector((
        0.0 if x else offset.x,
        0.0 if y else offset.y,
        0.0 if z else offset.z,
    ))

    if offset.length_squared == 0.0:
        return False

    loc, rot, sca = gem.ob.matrix_world.decompose()
    loc_next, rot_next = _snap_transform(gem, loc + offset, rot)
    is_loc_changed = (loc_next - loc).length_squared > 0.0
    is_rot_changed = not _quat_eq(rot_next, rot)

    if not is_loc_changed and not is_rot_changed:
        return False

    if is_rot_changed:
        gem.ob.matrix_world = Matrix.LocRotScale(loc_next, rot_next, sca)
    else:
        gem.ob.matrix_world.translation = loc_next

    return True


# Project on Surface
# -------------------------------------


def _snap_transform(gem: _Gem, loc_next: Vector, rot_current: Quaternion) -> tuple[Vector, Quaternion]:
    if bpy.context.scene.jewelcraft.spacing_snap_to_surface:
        loc_surface, normal = _snap_surface(gem, loc_next, rot_current)

        if normal is not None:
            return loc_surface, _align_rotation_to_normal(rot_current, normal)

        return loc_surface, rot_current

    return loc_next, rot_current


def _snap_surface(gem: _Gem, loc_next: Vector, rot_current: Quaternion) -> tuple[Vector, Vector | None]:
    axis = rot_current @ Vector((0.0, 0.0, 1.0))
    if axis.length_squared == 0.0:
        axis = Vector((0.0, 0.0, 1.0))
    else:
        axis.normalize()

    snap_distance = max(gem.ob.dimensions) * 2.0
    candidates = []

    for direction in (axis, -axis):
        origin = loc_next - direction * snap_distance
        hit = _ray_cast_surface(origin, direction, snap_distance * 2.0)
        if hit is not None:
            candidates.append(hit)

    if candidates:
        loc, normal = min(candidates, key=lambda item: (item[0] - loc_next).length_squared)
        return loc, normal

    return loc_next, None


def _ray_cast_surface(origin: Vector, direction: Vector, max_distance: float) -> tuple[Vector, Vector] | None:
    if direction.length_squared == 0.0 or max_distance <= 0.0:
        return None

    direction.normalize()

    context = bpy.context
    use_snap_selectable = context.scene.jewelcraft.spacing_snap_selectable
    ray_cast = context.scene.ray_cast
    depsgraph = context.evaluated_depsgraph_get()

    while max_distance > 0.0:
        is_hit, loc, normal, _, ob, _ = ray_cast(depsgraph, origin, direction, distance=max_distance)
        if not is_hit:
            return None

        if (
            ob is not None
            and not ob.hide_surface_pick
            and "gem" not in ob
            and not (use_snap_selectable and ob.hide_select)
        ):
            return loc, normal

        step = max((loc - origin).length, _SNAP_RAY_EPSILON)
        origin = loc + direction * _SNAP_RAY_EPSILON
        max_distance -= step + _SNAP_RAY_EPSILON

    return None


def _align_rotation_to_normal(rot: Quaternion, normal: Vector) -> Quaternion:
    if normal.length_squared == 0.0:
        return rot

    axis = rot @ Vector((0.0, 0.0, 1.0))
    if axis.length_squared == 0.0:
        return rot

    try:
        return axis.normalized().rotation_difference(normal.normalized()) @ rot
    except ValueError:
        return rot
