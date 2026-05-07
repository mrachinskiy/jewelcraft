# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import deque
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


def _is_editable_gem(ob: Object) -> bool:
    return "gem" in ob and ob.visible_get() and ob.is_editable


def _is_stationary_gem(ob: Object, gem: _Gem, selected: set[Object]) -> bool:
    return ob in selected or all(gem.ob.lock_location)


def _gem_mobility(ob: Object, gem: _Gem, selected: set[Object], selected_distance: float, falloff_distance: float) -> float:
    if _is_stationary_gem(ob, gem, selected):
        return 0.0
    return _distance_mobility(selected_distance, falloff_distance)


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


def _distance_mobility(selected_distance: float, falloff_distance: float) -> float:
    if selected_distance < 0.0 or selected_distance > falloff_distance or falloff_distance <= 0.0:
        return 0.0
    return 1.0 - selected_distance / falloff_distance


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

    if not _is_active_translate_operator(context):
        return _TIMER_INTERVAL

    if context.window_manager.is_interface_locked or context.mode != "OBJECT":
        return _TIMER_INTERVAL

    selected_gems = {ob for ob in context.selected_objects if _is_editable_gem(ob)}
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


def _collect_gems(context, props, obs: list[Object]) -> dict[Object, _Gem]:
    to_scene = unit.Scale().to_scene
    default_spacing = props.overlay_spacing
    use_overrides = props.overlay_use_overrides

    colls = None
    if props.gems_magnet_same_collection and obs:
        colls = {
            coll
            for ob in obs
            for coll in ob.users_collection
        }

    gems = {}
    for ob in context.visible_objects:
        if not _is_editable_gem(ob) or (colls is not None and colls.isdisjoint(set(ob.users_collection))):
            continue

        spacing = default_spacing
        if use_overrides and "gem_overlay" in ob:
            spacing = ob["gem_overlay"].get("spacing", default_spacing)

        gems[ob] = _Gem(ob, max(ob.dimensions.xy) / 2.0, to_scene(spacing))

    return gems


def _build_links(gems: dict[Object, _Gem], max_spacing: float) -> dict[Object, tuple[Object, ...]]:
    gems_info = tuple(gems.values())
    links = {gem.ob: [] for gem in gems_info}
    kd_tree = kdtree.KDTree(len(gems_info))
    max_radius = max(gem.radius for gem in gems_info)

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

    return {ob: tuple(neighbors) for ob, neighbors in links.items() if neighbors}


def _iter_link_pairs(gems: dict[Object, _Gem], links: dict[Object, tuple[Object, ...]], distances: dict[Object, float]):
    for ob1, neighbors in links.items():
        gem1 = gems.get(ob1)
        distance1 = distances.get(ob1)

        if gem1 is None or distance1 is None:
            continue

        for ob2 in neighbors:
            if ob2.as_pointer() <= ob1.as_pointer():
                continue

            gem2 = gems.get(ob2)
            distance2 = distances.get(ob2)

            if gem2 is None or distance2 is None:
                continue

            yield ob1, ob2, gem1, gem2, distance1, distance2


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

    for gem_object1, gem_object2, gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, links, distances):
        offset1, offset2 = _spring_offsets(
            gem1,
            gem2,
            gem_object1,
            gem_object2,
            selected_keys,
            distance1,
            distance2,
            falloff_distance,
            strength,
            delta_time,
        )

        if offset1.length_squared:
            offsets[gem_object1] = offsets.get(gem_object1, Vector()) + offset1
        if offset2.length_squared:
            offsets[gem_object2] = offsets.get(gem_object2, Vector()) + offset2

    offsets = _resolve_spacing_constraints(
        gems,
        links,
        distances,
        selected_keys,
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
    links: dict[Object, tuple[Object, ...]],
    distances: dict[Object, float],
    selected_keys: set[Object],
    falloff_distance: float,
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
        gem = gems.get(ob)
        if gem is None:
            continue

        if _is_stationary_gem(ob, gem, selected_keys):
            proposed[ob] = gem.ob.matrix_world.translation.copy()
        else:
            proposed[ob] = gem.ob.matrix_world.translation + offsets.get(ob, Vector())

    for _ in range(_CONSTRAINT_PASSES):
        changed = False

        for ob1, ob2, gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, links, distances):
            if ob1 not in proposed or ob2 not in proposed:
                continue

            spacing = max(gem1.spacing, gem2.spacing)
            compressed_spacing = spacing - min(spacing_tolerance, spacing)
            target_distance = gem1.radius + gem2.radius + compressed_spacing
            offset_vector = proposed[ob2] - proposed[ob1]
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

            mobility1 = _gem_mobility(ob1, gem1, selected_keys, distance1, falloff_distance)
            mobility2 = _gem_mobility(ob2, gem2, selected_keys, distance2, falloff_distance)
            mobility_total = mobility1 + mobility2

            if not mobility_total:
                continue

            correction = direction * (target_distance - distance) * constraint_alpha

            if mobility1:
                proposed[ob1] -= correction * (mobility1 / mobility_total)
            if mobility2:
                proposed[ob2] += correction * (mobility2 / mobility_total)

            changed = True

        if not changed:
            break

    return {
        ob: loc - ob.matrix_world.translation
        for ob, loc in proposed.items()
        if ob in gems and not _is_stationary_gem(ob, gems[ob], selected_keys)
    }


def _distance_map(gems: dict[Object, _Gem], links: dict[Object, tuple[Object, ...]], selected_keys: set[Object], falloff_distance: float) -> dict[Object, float]:
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
    ob1: Object,
    ob2: Object,
    selected_keys: set[Object],
    selected_distance1: float,
    selected_distance2: float,
    falloff_distance: float,
    strength: float,
    delta_time: float,
) -> tuple[Vector, Vector]:

    offset_vector = gem2.ob.matrix_world.translation - gem1.ob.matrix_world.translation
    distance = offset_vector.length

    if distance:
        direction = offset_vector / distance
    else:
        direction = Vector((1.0, 0.0, 0.0))

    mobility1 = _gem_mobility(ob1, gem1, selected_keys, selected_distance1, falloff_distance)
    mobility2 = _gem_mobility(ob2, gem2, selected_keys, selected_distance2, falloff_distance)
    mobility_total = mobility1 + mobility2

    if not mobility_total:
        zero = Vector()
        return zero, zero

    target_distance = gem1.radius + gem2.radius + max(gem1.spacing, gem2.spacing)
    influence = max(
        _distance_mobility(selected_distance1, falloff_distance),
        _distance_mobility(selected_distance2, falloff_distance),
    )
    alpha = 1.0 - exp(-_BASE_STRENGTH * strength * influence * delta_time)
    correction = direction * (distance - target_distance) * alpha

    return correction * (mobility1 / mobility_total), -correction * (mobility2 / mobility_total)
