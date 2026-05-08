# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict, deque
from math import exp
from time import perf_counter
from typing import NamedTuple

import bpy
from bpy.types import Object
from mathutils import Matrix, Quaternion, Vector, kdtree

from .. import unit

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
    if self.show_gems_magnet:
        handler_add()
    else:
        handler_del()


def handler_add() -> None:
    if not bpy.app.timers.is_registered(_timer):
        bpy.app.timers.register(_timer, first_interval=0.0)


def handler_del() -> None:
    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)


# Helpers
# -------------------------------------


def _quat_eq(a: Quaternion, b: Quaternion) -> bool:
    return a.rotation_difference(b).angle < 1e-6


def _is_active_translate_operator(context) -> bool:
    for operator in context.window.modal_operators:
        if operator.bl_idname == "TRANSFORM_OT_translate":
            return True
    return False


def _nearest_selected_distance(gem1: _Gem, selected: tuple[_Gem, ...]) -> float:
    if not selected:
        return float("inf")

    return min(
        (gem1.ob.matrix_world.translation - gem2.ob.matrix_world.translation).length
        for gem2 in selected
    )


def _gem_mobility(gem: _Gem, dist: float, falloff: float) -> float:
    if gem.locked:
        return 0.0
    return _distance_mobility(dist, falloff)


def _distance_mobility(dist: float, falloff: float) -> float:
    if dist < 0.0 or dist > falloff or falloff <= 0.0:
        return 0.0
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

    if not wm_props.show_gems_magnet:
        return None

    if not _is_active_translate_operator(context) or context.window_manager.is_interface_locked or context.mode != "OBJECT":
        return _TIMER_INTERVAL

    selected_gems = {ob for ob in context.selected_objects if "gem" in ob}
    if not selected_gems:
        return _TIMER_INTERVAL

    scene_props = context.scene.jewelcraft
    gems = _collect_gems(context, scene_props, selected_gems)
    if len(gems) < 2:
        return _TIMER_INTERVAL

    to_scene = unit.Scale().to_scene
    max_spacing = to_scene(scene_props.gems_magnet_max_spacing)
    falloff_distance = to_scene(scene_props.gems_magnet_falloff_distance)
    spacing_tolerance = to_scene(scene_props.gems_magnet_spacing_tolerance)
    delta_time = _delta_time()

    _apply_magnet(
        context,
        gems,
        selected_gems,
        max_spacing,
        falloff_distance,
        spacing_tolerance,
        scene_props.gems_magnet_strength,
        delta_time,
    )

    return _TIMER_INTERVAL


def _collect_gems(context, props, selected: list[Object]) -> dict[Object, _Gem]:
    to_scene = unit.Scale().to_scene
    default_spacing = props.overlay_spacing
    use_overrides = props.overlay_use_overrides

    colls = None
    if props.gems_magnet_same_collection and selected:
        colls = {
            coll
            for ob in selected
            for coll in ob.users_collection
        }

    gems = {}
    for ob in context.visible_objects:
        if "gem" not in ob:
            continue

        spacing = default_spacing
        if use_overrides and "gem_overlay" in ob:
            spacing = ob["gem_overlay"].get("spacing", default_spacing)

        if (colls is not None and colls.isdisjoint(set(ob.users_collection))):
            gems[ob] = _Gem(ob, max(ob.dimensions.xy) / 2.0, to_scene(spacing), True)
        else:
            locked = ob in selected or ob.get("gem_lock", False)
            gems[ob] = _Gem(ob, max(ob.dimensions.xy) / 2.0, to_scene(spacing), locked)

    return gems


def _build_links(gems: dict[Object, _Gem], max_spacing: float) -> dict[Object, list[Object]]:
    gems_info = tuple(gems.values())
    max_radius = max(gem.radius for gem in gems_info)
    links = defaultdict(list)

    kd_tree = kdtree.KDTree(len(gems_info))

    for i1, gem in enumerate(gems_info):
        kd_tree.insert(gem.ob.matrix_world.translation, i1)

    kd_tree.balance()

    for i1, gem1 in enumerate(gems_info):
        search_radius = gem1.radius + max_radius + max_spacing

        for _, i2, distance in kd_tree.find_range(gem1.ob.matrix_world.translation, search_radius):
            if i2 <= i1:
                continue

            gem2 = gems_info[i2]
            if max(distance - gem1.radius - gem2.radius, 0.0) > max_spacing:
                continue

            links[gem1.ob].append(gem2.ob)
            links[gem2.ob].append(gem1.ob)

    return links


def _iter_link_pairs(gems: dict[Object, _Gem], links: dict[Object, list[Object]], distances: dict[Object, float]):
    for ob1, neighbors in links.items():
        gem1 = gems.get(ob1)
        distance1 = distances.get(ob1)

        if distance1 is None:
            continue

        for ob2 in neighbors:
            if ob2.as_pointer() <= ob1.as_pointer():
                continue

            gem2 = gems.get(ob2)
            distance2 = distances.get(ob2)

            if distance2 is None:
                continue

            yield gem1, gem2, distance1, distance2


def _apply_magnet(
    context,
    gems: dict[Object, _Gem],
    selected_keys: set[Object],
    max_spacing: float,
    falloff_distance: float,
    spacing_tolerance: float,
    strength: float,
    delta_time: float,
) -> None:

    links = _build_links(gems, max_spacing)
    if not links:
        return

    distances = _distance_map(gems, links, selected_keys, falloff_distance)
    if len(distances) <= len(selected_keys):
        return

    offsets: dict[Object, Vector] = {}

    for gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, links, distances):
        offset1, offset2 = _spring_offsets(
            gem1,
            gem2,
            distance1,
            distance2,
            falloff_distance,
            strength,
            delta_time,
        )

        if offset1.length_squared:
            offsets[gem1.ob] = offsets.get(gem1.ob, Vector()) + offset1
        if offset2.length_squared:
            offsets[gem2.ob] = offsets.get(gem2.ob, Vector()) + offset2

    offsets = _resolve_spacing_constraints(
        gems,
        links,
        distances,
        falloff_distance,
        offsets,
        spacing_tolerance,
        strength,
        delta_time,
    )
    threshold = unit.Scale().to_scene(0.001)

    for gem_object, offset in offsets.items():
        if gem_object in selected_keys:
            continue

        if offset.length <= threshold:
            continue

        gem = gems.get(gem_object)

        if gem is None:
            continue

        _move_gem(context, gem, offset)


def _resolve_spacing_constraints(
    gems: dict[Object, _Gem],
    links: dict[Object, list[Object]],
    distances: dict[Object, float],
    falloff: float,
    offsets: dict[Object, Vector],
    spacing_tolerance: float,
    strength: float,
    delta_time: float,
) -> dict[Object, Vector]:

    constraint_alpha = 1.0 - exp(-_BASE_STRENGTH * strength * delta_time)
    if constraint_alpha <= 0.0:
        return offsets

    proposed: dict[Object, Vector] = {}

    for ob in distances:
        if gems[ob].locked:
            proposed[ob] = ob.matrix_world.translation.copy()
        else:
            proposed[ob] = ob.matrix_world.translation + offsets.get(ob, Vector())

    for _ in range(_CONSTRAINT_PASSES):
        changed = False

        for gem1, gem2, dist1, dist2 in _iter_link_pairs(gems, links, distances):
            if gem1.ob not in proposed or gem2.ob not in proposed or (gem1.locked and gem2.locked):
                continue

            spacing = max(gem1.spacing, gem2.spacing)
            compressed_spacing = spacing - min(spacing_tolerance, spacing)
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

            m1 = _gem_mobility(gem1, dist1, falloff)
            m2 = _gem_mobility(gem2, dist2, falloff)
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
        for ob, loc in proposed.items() if not gems[ob].locked
    }


def _distance_map(gems: dict[Object, _Gem], links: dict[Object, list[Object]], selected_keys: set[Object], falloff_distance: float) -> dict[Object, float]:
    distances = {ob: 0.0 for ob in selected_keys if ob in gems}
    if not distances:
        return distances

    selected_gems = tuple(gems[ob] for ob in distances)
    queue = deque(distances)

    while queue:
        ob = queue.popleft()

        for ob_next in links.get(ob, ()):
            if ob_next not in gems or ob_next in selected_keys:
                continue

            distance_next = _nearest_selected_distance(gems[ob_next], selected_gems)

            if distance_next > falloff_distance:
                continue

            if distance_next < distances.get(ob_next, float("inf")):
                distances[ob_next] = distance_next
                queue.append(ob_next)

    return distances


def _ray_cast_surface(context, origin: Vector, direction: Vector, max_distance: float) -> tuple[Vector, Vector] | None:
    if direction.length_squared == 0.0 or max_distance <= 0.0:
        return None

    direction.normalize()
    use_snap_selectable = context.scene.jewelcraft.gems_magnet_use_snap_selectable
    ray_cast = context.scene.ray_cast
    depsgraph = context.evaluated_depsgraph_get()

    while max_distance > 0.0:
        is_hit, loc, normal, _, ob, _ = ray_cast(depsgraph, origin, direction, distance=max_distance)
        if not is_hit:
            return None

        if (
            ob is not None
            and ob.visible_get()
            and not ob.hide_surface_pick
            and "gem" not in ob
            and not (use_snap_selectable and ob.hide_select)
        ):
            return loc, normal

        step = max((loc - origin).length, _SNAP_RAY_EPSILON)
        origin = loc + direction * _SNAP_RAY_EPSILON
        max_distance -= step + _SNAP_RAY_EPSILON

    return None


def _snap_surface(context, gem: _Gem, loc_next: Vector, rot_current: Quaternion) -> tuple[Vector, Vector | None]:
    axis = rot_current @ Vector((0.0, 0.0, 1.0))
    if axis.length_squared == 0.0:
        axis = Vector((0.0, 0.0, 1.0))
    else:
        axis.normalize()

    snap_distance = max(gem.ob.dimensions) * 2.0
    candidates = []

    for direction in (axis, -axis):
        origin = loc_next - direction * snap_distance
        hit = _ray_cast_surface(context, origin, direction, snap_distance * 2.0)
        if hit is not None:
            candidates.append(hit)

    if candidates:
        loc, normal = min(candidates, key=lambda item: (item[0] - loc_next).length_squared)
        return loc, normal

    return loc_next, None


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


def _snap_transform(context, gem: _Gem, loc_next: Vector, rot_current: Quaternion):
    if context.scene.jewelcraft.gems_magnet_snap_to_face:
        loc_surface, normal = _snap_surface(context, gem, loc_next, rot_current)

        if normal is not None:
            return loc_surface, _align_rotation_to_normal(rot_current, normal)

        return loc_surface, rot_current

    return loc_next, rot_current


def _move_gem(context, gem: _Gem, offset: Vector) -> bool:
    x, y, z = gem.ob.lock_location
    offset = Vector((
        0.0 if x else offset.x,
        0.0 if y else offset.y,
        0.0 if z else offset.z,
    ))

    if offset.length_squared == 0.0:
        return False

    loc, rot, sca = gem.ob.matrix_world.decompose()
    loc_next, rot_next = _snap_transform(context, gem, loc + offset, rot)
    is_loc_changed = (loc_next - loc).length_squared > 0.0
    is_rot_changed = not _quat_eq(rot_next, rot)

    if not is_loc_changed and not is_rot_changed:
        return False

    if is_rot_changed:
        gem.ob.matrix_world = Matrix.LocRotScale(loc_next, rot_next, sca)
    else:
        gem.ob.matrix_world.translation = loc_next

    return True


def _spring_offsets(
    gem1: _Gem,
    gem2: _Gem,
    dist1: float,
    dist2: float,
    falloff: float,
    strength: float,
    delta_time: float,
) -> tuple[Vector, Vector]:

    offset_vector = gem2.ob.matrix_world.translation - gem1.ob.matrix_world.translation
    distance = offset_vector.length

    if distance:
        direction = offset_vector / distance
    else:
        direction = Vector((1.0, 0.0, 0.0))

    m1 = _gem_mobility(gem1, dist1, falloff)
    m2 = _gem_mobility(gem2, dist2, falloff)
    m_total = m1 + m2

    if not m_total:
        zero = Vector()
        return zero, zero

    target_distance = gem1.radius + gem2.radius + max(gem1.spacing, gem2.spacing)
    influence = max(
        _distance_mobility(dist1, falloff),
        _distance_mobility(dist2, falloff),
    )
    alpha = 1.0 - exp(-_BASE_STRENGTH * strength * influence * delta_time)
    correction = direction * (distance - target_distance) * alpha

    return correction * (m1 / m_total), -correction * (m2 / m_total)
