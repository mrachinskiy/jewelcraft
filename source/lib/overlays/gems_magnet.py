# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import deque
from math import exp
from time import perf_counter

import bpy
from bpy.types import Object
from mathutils import Matrix, Quaternion, Vector, kdtree

from .. import unit

_TIMER_INTERVAL = 1 / 60
_MAX_DELTA_TIME = 0.1
_BASE_STRENGTH = 10.0
_CONSTRAINT_PASSES = 7
_CONSTRAINT_STRENGTH = 1
_SNAP_RAY_EPSILON = 0.0001

_state: "_State" = None


def handler_toggle(self, context) -> None:
    if self.show_gems_magnet:
        handler_add()
    else:
        handler_del()


def handler_add() -> None:
    global _state

    _state = _State()

    if not bpy.app.timers.is_registered(_timer):
        bpy.app.timers.register(_timer, first_interval=0.0)

    if _undo_post not in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.append(_undo_post)

    if _undo_post not in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.append(_undo_post)


def handler_del() -> None:
    global _state

    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)

    if _undo_post in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(_undo_post)

    if _undo_post in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(_undo_post)

    _state = None


def _undo_post(_) -> None:
    _state.reset()


# Types
# -------------------------------------


class _Gem:
    __slots__ = ("object", "location", "radius", "spacing")

    def __init__(self, gem_object: Object, spacing: float) -> None:
        self.object = gem_object
        self.location = gem_object.matrix_world.translation.copy()
        self.radius = max(gem_object.dimensions.xy) / 2.0
        self.spacing = spacing


class _State:
    __slots__ = "links", "time_prev"

    def __init__(self) -> None:
        self.links: dict[Object, tuple[Object, ...]] = {}
        self.time_prev: float | None = None

    def reset(self) -> None:
        self.links.clear()
        self.time_prev = None


# Helpers
# -------------------------------------


def _move_threshold() -> float:
    return unit.Scale().to_scene(0.001)


def _quat_eq(a: Quaternion, b: Quaternion) -> bool:
    return a.rotation_difference(b).angle < 1e-6


def _is_editable_gem(ob: Object | None) -> bool:
    return ob is not None and "gem" in ob and ob.visible_get() and ob.is_editable


def _is_stationary_gem(ob: Object, gem: _Gem, selected_keys: frozenset[Object]) -> bool:
    return ob in selected_keys or all(gem.object.lock_location)


def _gem_mobility(gem_object: Object, gem: _Gem, selected_keys: frozenset[Object], selected_distance: float, falloff_distance: float) -> float:
    if _is_stationary_gem(gem_object, gem, selected_keys):
        return 0.0
    return _distance_mobility(selected_distance, falloff_distance)


def _is_active_translate_operator(context) -> bool:
    for operator in context.window.modal_operators:
        if operator.bl_idname == "TRANSFORM_OT_translate":
            return True
    return False


def _nearest_selected_distance(gem1: _Gem, selected_gems: tuple[_Gem, ...]) -> float:
    if not selected_gems:
        return float("inf")

    return min(_girdle_gap(gem1, gem2) for gem2 in selected_gems)


def _distance_mobility(selected_distance: float, falloff_distance: float) -> float:
    if selected_distance < 0.0 or selected_distance > falloff_distance or falloff_distance <= 0.0:
        return 0.0
    return 1.0 - selected_distance / falloff_distance


def _delta_time(current_time: float) -> float:
    if _state.time_prev is None:
        _state.time_prev = current_time
        return _TIMER_INTERVAL

    delta_time = min(current_time - _state.time_prev, _MAX_DELTA_TIME)
    _state.time_prev = current_time
    return delta_time


# Main Loop
# -------------------------------------


def _timer() -> float | None:
    global _state

    context = bpy.context
    wm_props = context.window_manager.jewelcraft

    if not wm_props.show_gems_magnet:
        _state = None
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

    current_time = perf_counter()
    delta_time = _delta_time(current_time)

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

        gems[ob] = _Gem(ob, to_scene(spacing))

    return gems


def _merge_links(existing: dict[Object, tuple[Object, ...]], incoming: dict[Object, tuple[Object, ...]]) -> dict[Object, tuple[Object, ...]]:
    merged = {ob: set(neighbors) for ob, neighbors in existing.items()}

    for ob, neighbors in incoming.items():
        merged.setdefault(ob, set()).update(neighbors)

    return {ob: tuple(neighbors) for ob, neighbors in merged.items() if neighbors}


def _girdle_gap(gem1: _Gem, gem2: _Gem, center_distance: float | None = None) -> float:
    if center_distance is None:
        center_distance = (gem1.location - gem2.location).length

    return max(center_distance - gem1.radius - gem2.radius, 0.0)


def _build_links(gems: dict[Object, _Gem], max_spacing: float) -> dict[Object, tuple[Object, ...]]:
    gems_info = tuple(gems.values())
    links = {gem.object: [] for gem in gems_info}
    kd_tree = kdtree.KDTree(len(gems_info))
    max_radius = max(gem.radius for gem in gems_info)

    for i1, gem in enumerate(gems_info):
        kd_tree.insert(gem.location, i1)

    kd_tree.balance()

    for i1, gem1 in enumerate(gems_info):
        search_radius = gem1.radius + max_radius + max_spacing

        for _, i2, distance in kd_tree.find_range(gem1.location, search_radius):
            if i2 <= i1:
                continue

            gem2 = gems_info[i2]
            if _girdle_gap(gem1, gem2, distance) > max_spacing:
                continue

            links[gem1.object].append(gem2.object)
            links[gem2.object].append(gem1.object)

    return {ob: tuple(neighbors) for ob, neighbors in links.items() if neighbors}


def _iter_link_pairs(gems: dict[Object, _Gem], distances: dict[Object, float]):
    for ob1, neighbors in _state.links.items():
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
    selected_keys: frozenset[Object],
    max_spacing: float,
    falloff_distance: float,
    spacing_tolerance: float,
    strength: float,
    delta_time: float,
) -> None:
    live_links = _build_links(gems, max_spacing)

    if live_links:
        _state.links = _merge_links(_state.links, live_links)

    if not _state.links:
        return

    distances = _distance_map(gems, selected_keys, falloff_distance)

    if len(distances) <= len(selected_keys):
        return

    threshold = _move_threshold()
    offsets: dict[Object, Vector] = {}

    for gem_object1, gem_object2, gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, distances):
        spacing = max(gem1.spacing, gem2.spacing)
        offset1, offset2 = _spring_offsets(
            gem1,
            gem2,
            gem_object1,
            gem_object2,
            selected_keys,
            spacing,
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
        distances,
        selected_keys,
        falloff_distance,
        offsets,
        spacing_tolerance,
        strength,
        delta_time,
    )

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
    distances: dict[Object, float],
    selected_keys: frozenset[Object],
    falloff_distance: float,
    offsets: dict[Object, Vector],
    spacing_tolerance: float,
    strength: float,
    delta_time: float,
) -> dict[Object, Vector]:
    proposed: dict[Object, Vector] = {}
    constraint_alpha = 1.0 - exp(-_BASE_STRENGTH * _CONSTRAINT_STRENGTH * strength * delta_time)

    if constraint_alpha <= 0.0:
        return offsets

    for ob in distances:
        gem = gems.get(ob)
        if gem is None:
            continue

        if _is_stationary_gem(ob, gem, selected_keys):
            proposed[ob] = gem.location.copy()
        else:
            proposed[ob] = gem.location + offsets.get(ob, Vector())

    for _ in range(_CONSTRAINT_PASSES):
        changed = False

        for ob1, ob2, gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, distances):
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
                current_offset = gem2.location - gem1.location

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
        ob: loc - gems[ob].location
        for ob, loc in proposed.items()
        if ob in gems and not _is_stationary_gem(ob, gems[ob], selected_keys)
    }


def _distance_map(gems: dict[Object, _Gem], selected_keys: frozenset[Object], falloff_distance: float) -> dict[Object, float]:
    distances = {ob: 0.0 for ob in selected_keys if ob in gems}
    if not distances:
        return distances

    selected_gems = tuple(gems[ob] for ob in distances)
    queue = deque(distances)

    while queue:
        ob = queue.popleft()

        for ob_next in _state.links.get(ob, ()):
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

    use_snap_selectable = context.scene.jewelcraft.gems_magnet_use_snap_selectable
    ray_cast = context.scene.ray_cast
    depsgraph = context.evaluated_depsgraph_get()
    direction = direction.normalized()
    distance_left = max_distance
    origin_current = origin

    while distance_left > 0.0:
        is_hit, loc, normal, _, ob, _ = ray_cast(depsgraph, origin_current, direction, distance=distance_left)
        if not is_hit:
            return None

        if (
            ob is not None
            and ob.visible_get()
            and not ob.hide_surface_pick
            and "gem" not in ob
            and not (use_snap_selectable and ob.hide_select)
        ):
            return loc.copy(), normal.normalized()

        travelled = (loc - origin_current).length
        step = max(travelled, _SNAP_RAY_EPSILON)
        origin_current = loc + direction * _SNAP_RAY_EPSILON
        distance_left -= step + _SNAP_RAY_EPSILON

    return None


def _snap_surface(context, gem: _Gem, loc_next: Vector, rot_current: Quaternion) -> tuple[Vector, Vector | None]:
    axis = rot_current @ Vector((0.0, 0.0, 1.0))

    if axis.length_squared == 0.0:
        axis = Vector((0.0, 0.0, 1.0))
    else:
        axis.normalize()

    snap_distance = max(max(gem.object.dimensions), gem.radius * 4.0, unit.Scale().to_scene(1.0))
    candidates = []

    for direction in (axis, -axis):
        origin = loc_next - direction * snap_distance
        hit = _ray_cast_surface(context, origin, direction, snap_distance * 2.0)

        if hit is not None:
            candidates.append(hit)

    if candidates:
        location, normal = min(candidates, key=lambda item: (item[0] - loc_next).length_squared)
        return location, normal

    return loc_next, None


def _align_rotation_to_normal(rot_current: Quaternion, normal: Vector) -> Quaternion:
    if normal.length_squared == 0.0:
        return rot_current

    axis_current = rot_current @ Vector((0.0, 0.0, 1.0))
    if axis_current.length_squared == 0.0:
        return rot_current

    try:
        return axis_current.normalized().rotation_difference(normal.normalized()) @ rot_current
    except ValueError:
        return rot_current


def _snap_transform(context, gem: _Gem, loc_next: Vector, rot_current: Quaternion):
    if context.scene.jewelcraft.gems_magnet_snap_to_face:
        surface_location, normal = _snap_surface(context, gem, loc_next, rot_current)

        if normal is not None:
            return surface_location, _align_rotation_to_normal(rot_current, normal)

        return surface_location, rot_current

    return loc_next, rot_current


def _move_gem(context, gem: _Gem, offset: Vector) -> bool:
    x, y, z = gem.object.lock_location
    offset = Vector((
        0.0 if x else offset.x,
        0.0 if y else offset.y,
        0.0 if z else offset.z,
    ))

    if offset.length_squared == 0.0:
        return False

    mat = gem.object.matrix_world.copy()
    rot_current = mat.to_quaternion()
    loc_next, rot_next = _snap_transform(context, gem, gem.location + offset, rot_current)
    is_loc_changed = (loc_next - gem.location).length_squared > 0.0
    is_rot_changed = not _quat_eq(rot_next, rot_current)

    if not is_loc_changed and not is_rot_changed:
        return False

    if is_rot_changed:
        gem.object.matrix_world = Matrix.LocRotScale(loc_next, rot_next, mat.to_scale())
    else:
        mat.translation = loc_next
        gem.object.matrix_world = mat

    gem.location = loc_next
    return True


def _spring_offsets(
    gem1: _Gem,
    gem2: _Gem,
    ob1: Object,
    ob2: Object,
    selected_keys: frozenset[Object],
    spacing: float,
    selected_distance1: float,
    selected_distance2: float,
    falloff_distance: float,
    strength: float,
    delta_time: float,
) -> tuple[Vector, Vector]:
    offset_vector = gem2.location - gem1.location
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

    target_distance = gem1.radius + gem2.radius + spacing
    influence = max(
        _distance_mobility(selected_distance1, falloff_distance),
        _distance_mobility(selected_distance2, falloff_distance),
    )
    alpha = 1.0 - exp(-_BASE_STRENGTH * strength * influence * delta_time)
    correction = direction * (distance - target_distance) * alpha

    return correction * (mobility1 / mobility_total), -correction * (mobility2 / mobility_total)
