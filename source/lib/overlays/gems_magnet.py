# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import deque
from math import exp
from time import perf_counter

import bpy
from mathutils import Matrix, Vector, kdtree

from .. import unit

_TIMER_INTERVAL = 1 / 60
_MAX_DELTA_TIME = 0.1
_BASE_STRENGTH = 10.0
_MOVE_EPSILON = 0.001
_CONSTRAINT_PASSES = 7
_CONSTRAINT_STRENGTH = 1
_SNAP_RAY_EPSILON = 0.0001


class _Gem:
    __slots__ = ("object", "location", "radius", "spacing")

    def __init__(self, gem_object: bpy.types.Object, spacing: float) -> None:
        self.object = gem_object
        self.location = gem_object.matrix_world.translation.copy()
        self.radius = max(gem_object.dimensions.xy) / 2.0
        self.spacing = spacing


class _State:
    __slots__ = ("drag_snapshot", "dragging", "drag_selected_start", "links", "prev_selected", "selected_keys", "time_prev")

    def __init__(self) -> None:
        self.drag_snapshot: dict[str, Matrix] = {}
        self.dragging = False
        self.drag_selected_start: dict[str, Vector] = {}
        self.links: dict[bpy.types.Object, tuple[bpy.types.Object, ...]] = {}
        self.prev_selected: dict[bpy.types.Object, Vector] = {}
        self.selected_keys: frozenset[bpy.types.Object] = frozenset()
        self.time_prev: float | None = None

    def reset(self) -> None:
        self.clear_drag()
        self.prev_selected.clear()
        self.selected_keys = frozenset()
        self.time_prev = None

    def clear_drag(self) -> None:
        self.drag_snapshot.clear()
        self.dragging = False
        self.drag_selected_start.clear()
        self.links.clear()


_STATE = _State()


def handler_add() -> None:
    if not bpy.app.timers.is_registered(_timer):
        _STATE.reset()
        bpy.app.timers.register(_timer, first_interval=0.0)

    if _undo_post not in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.append(_undo_post)

    if _undo_post not in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.append(_undo_post)


def handler_del() -> None:
    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)

    if _undo_post in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(_undo_post)

    if _undo_post in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(_undo_post)

    _STATE.reset()


def handler_toggle(self, context) -> None:
    if self.show_gems_magnet:
        handler_add()
    else:
        handler_del()


def _undo_post(_scene) -> None:
    _STATE.reset()


def _timer() -> float | None:
    context = bpy.context
    wm_props = getattr(getattr(context, "window_manager", None), "jewelcraft", None)

    if wm_props is None or not wm_props.show_gems_magnet:
        _STATE.reset()
        return None

    if context.window_manager.is_interface_locked or context.mode != "OBJECT":
        _STATE.clear_drag()
        return _TIMER_INTERVAL

    selected_gems = [gem_object for gem_object in context.selected_objects if _is_editable_gem(gem_object)]

    if not selected_gems:
        if _STATE.selected_keys:
            _STATE.clear_drag()
            _STATE.selected_keys = frozenset()

        _STATE.prev_selected = {}
        return _TIMER_INTERVAL

    selected_positions = _selected_positions(selected_gems)
    selected_keys = frozenset(selected_positions)

    if selected_keys != _STATE.selected_keys:
        _STATE.clear_drag()
        _STATE.selected_keys = selected_keys

    current_time = perf_counter()
    delta_time = _delta_time(current_time)

    scene_props = context.scene.jewelcraft
    gems = _collect_gems(context, scene_props, selected_gems)
    to_scene = unit.Scale().to_scene
    max_spacing = to_scene(scene_props.gems_magnet_max_spacing)
    falloff_distance = to_scene(scene_props.gems_magnet_falloff_distance)
    spacing_tolerance = to_scene(scene_props.gems_magnet_spacing_tolerance)

    if len(gems) < 2:
        _STATE.clear_drag()
        _STATE.prev_selected = selected_positions
        return _TIMER_INTERVAL

    if _is_active_translate_operator(context):
        selection_moved = _selected_moved(selected_positions)

        if selection_moved and not _STATE.dragging:
            _start_drag(gems, selected_keys, max_spacing, falloff_distance)

        if _STATE.dragging and selection_moved:
            _apply_magnet(
                context,
                gems,
                selected_keys,
                max_spacing,
                falloff_distance,
                spacing_tolerance,
                scene_props.gems_magnet_strength,
                delta_time,
            )
    elif _STATE.dragging:
        _finish_drag()

    _STATE.prev_selected = selected_positions

    return _TIMER_INTERVAL


def _delta_time(current_time: float) -> float:
    if _STATE.time_prev is None:
        _STATE.time_prev = current_time
        return _TIMER_INTERVAL

    delta_time = min(current_time - _STATE.time_prev, _MAX_DELTA_TIME)
    _STATE.time_prev = current_time
    return delta_time


def _move_threshold() -> float:
    return unit.Scale().to_scene(_MOVE_EPSILON)


def _selected_positions(selected_gems: list[bpy.types.Object]) -> dict[bpy.types.Object, Vector]:
    return {gem_object: gem_object.matrix_world.translation.copy() for gem_object in selected_gems}


def _selected_moved(selected_positions: dict[bpy.types.Object, Vector]) -> bool:
    if _STATE.selected_keys != frozenset(_STATE.prev_selected):
        return False

    threshold = _move_threshold()

    for pointer, location in selected_positions.items():
        previous_location = _STATE.prev_selected.get(pointer)
        if previous_location is not None and (location - previous_location).length > threshold:
            return True

    return False


def _collect_gems(context, props, selected_gems: list[bpy.types.Object]) -> dict[bpy.types.Object, _Gem]:
    to_scene = unit.Scale().to_scene
    default_spacing = float(props.overlay_spacing)
    use_overrides = props.overlay_use_overrides
    selected_collections = (
        {
            collection
            for gem_object in selected_gems
            for collection in gem_object.users_collection
        }
        if props.gems_magnet_same_collection and selected_gems
        else None
    )
    gems = {}

    for gem_object in context.visible_objects:
        if not _is_editable_gem(gem_object):
            continue

        if selected_collections is not None and not any(
            collection in selected_collections
            for collection in gem_object.users_collection
        ):
            continue

        spacing = default_spacing

        if use_overrides and "gem_overlay" in gem_object:
            spacing = float(gem_object["gem_overlay"].get("spacing", default_spacing))

        gems[gem_object] = _Gem(gem_object, to_scene(spacing))

    return gems


def _is_editable_gem(gem_object: bpy.types.Object | None) -> bool:
    return gem_object is not None and "gem" in gem_object and gem_object.visible_get() and gem_object.is_editable


def _is_stationary_gem(gem_object: bpy.types.Object, gem: _Gem, selected_keys: frozenset[bpy.types.Object]) -> bool:
    return gem_object in selected_keys or all(gem.object.lock_location)


def _gem_mobility(
    gem_object: bpy.types.Object,
    gem: _Gem,
    selected_keys: frozenset[bpy.types.Object],
    selected_distance: float,
    falloff_distance: float,
) -> float:
    if _is_stationary_gem(gem_object, gem, selected_keys):
        return 0.0

    return _distance_mobility(selected_distance, falloff_distance)


def _is_active_translate_operator(context) -> bool:
    window = context.window
    if window is None:
        return False

    for operator in window.modal_operators:
        if operator.bl_idname == "TRANSFORM_OT_translate":
            return True
    return False


def _merge_links(
    existing: dict[bpy.types.Object, tuple[bpy.types.Object, ...]],
    incoming: dict[bpy.types.Object, tuple[bpy.types.Object, ...]],
) -> dict[bpy.types.Object, tuple[bpy.types.Object, ...]]:
    merged: dict[bpy.types.Object, set[bpy.types.Object]] = {
        gem_object: set(neighbors) for gem_object, neighbors in existing.items()
    }

    for gem_object, neighbors in incoming.items():
        merged.setdefault(gem_object, set()).update(neighbors)

    return {gem_object: tuple(neighbors) for gem_object, neighbors in merged.items() if neighbors}


def _girdle_gap(gem1: _Gem, gem2: _Gem, center_distance: float | None = None) -> float:
    if center_distance is None:
        center_distance = (gem1.location - gem2.location).length

    return max(center_distance - gem1.radius - gem2.radius, 0.0)


def _build_links(
    gems: dict[bpy.types.Object, _Gem],
    max_spacing: float,
) -> dict[bpy.types.Object, tuple[bpy.types.Object, ...]]:
    gem_items = tuple(gems.values())
    links: dict[bpy.types.Object, list[bpy.types.Object]] = {gem.object: [] for gem in gem_items}
    kd_tree = kdtree.KDTree(len(gem_items))
    max_radius = max(gem.radius for gem in gem_items)

    for index, gem in enumerate(gem_items):
        kd_tree.insert(gem.location, index)

    kd_tree.balance()

    for index, gem1 in enumerate(gem_items):
        search_radius = gem1.radius + max_radius + max_spacing

        for _coordinate, index2, center_distance in kd_tree.find_range(gem1.location, search_radius):
            if index2 <= index:
                continue

            gem2 = gem_items[index2]

            if _girdle_gap(gem1, gem2, center_distance) > max_spacing:
                continue

            links[gem1.object].append(gem2.object)
            links[gem2.object].append(gem1.object)

    return {gem_object: tuple(neighbors) for gem_object, neighbors in links.items() if neighbors}


def _iter_link_pairs(gems: dict[bpy.types.Object, _Gem], distances: dict[bpy.types.Object, float]):
    for gem_object1, neighbors in _STATE.links.items():
        gem1 = gems.get(gem_object1)
        distance1 = distances.get(gem_object1)

        if gem1 is None or distance1 is None:
            continue

        for gem_object2 in neighbors:
            if gem_object2.as_pointer() <= gem_object1.as_pointer():
                continue

            gem2 = gems.get(gem_object2)
            distance2 = distances.get(gem_object2)

            if gem2 is None or distance2 is None:
                continue

            yield gem_object1, gem_object2, gem1, gem2, distance1, distance2


def _start_drag(
    gems: dict[bpy.types.Object, _Gem],
    selected_keys: frozenset[bpy.types.Object],
    max_spacing: float,
    falloff_distance: float,
) -> None:
    _STATE.links = _build_links(gems, max_spacing)

    if not _STATE.links:
        return

    distances = _distance_map(gems, selected_keys, falloff_distance)

    if len(distances) <= len(selected_keys):
        return

    _snapshot_drag_gems(gems, distances)
    _STATE.drag_selected_start = {
        gems[gem_object].object.name: gems[gem_object].location.copy()
        for gem_object in selected_keys
        if gem_object in gems
    }
    _STATE.dragging = True


def _finish_drag() -> None:
    if _is_cancelled_drag():
        _restore_drag_snapshot()

    _STATE.clear_drag()


def _is_cancelled_drag() -> bool:
    if not _STATE.drag_selected_start:
        return False

    threshold = _move_threshold()

    for name, start_location in _STATE.drag_selected_start.items():
        object_ = bpy.data.objects.get(name)

        if object_ is None or (object_.matrix_world.translation - start_location).length > threshold:
            return False

    return True


def _restore_drag_snapshot() -> None:
    for name, matrix in _STATE.drag_snapshot.items():
        if (object_ := bpy.data.objects.get(name)) is None:
            continue

        object_.matrix_world = matrix.copy()


def _snapshot_drag_gems(gems: dict[bpy.types.Object, _Gem], distances: dict[bpy.types.Object, float]) -> None:
    for gem_object in distances:
        gem = gems.get(gem_object)

        if gem is None:
            continue

        _STATE.drag_snapshot.setdefault(gem.object.name, gem.object.matrix_world.copy())


def _apply_magnet(
    context,
    gems: dict[bpy.types.Object, _Gem],
    selected_keys: frozenset[bpy.types.Object],
    max_spacing: float,
    falloff_distance: float,
    spacing_tolerance: float,
    strength: float,
    delta_time: float,
) -> None:
    live_links = _build_links(gems, max_spacing)

    if live_links:
        _STATE.links = _merge_links(_STATE.links, live_links)

    if not _STATE.links:
        return

    distances = _distance_map(gems, selected_keys, falloff_distance)

    if len(distances) <= len(selected_keys):
        return

    _snapshot_drag_gems(gems, distances)

    threshold = _move_threshold()
    offsets: dict[bpy.types.Object, Vector] = {}

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
    gems: dict[bpy.types.Object, _Gem],
    distances: dict[bpy.types.Object, float],
    selected_keys: frozenset[bpy.types.Object],
    falloff_distance: float,
    offsets: dict[bpy.types.Object, Vector],
    spacing_tolerance: float,
    strength: float,
    delta_time: float,
) -> dict[bpy.types.Object, Vector]:
    proposed: dict[bpy.types.Object, Vector] = {}
    constraint_alpha = 1.0 - exp(-_BASE_STRENGTH * _CONSTRAINT_STRENGTH * strength * delta_time)

    if constraint_alpha <= 0.0:
        return offsets

    for gem_object in distances:
        gem = gems.get(gem_object)

        if gem is None:
            continue

        if _is_stationary_gem(gem_object, gem, selected_keys):
            proposed[gem_object] = gem.location.copy()
        else:
            proposed[gem_object] = gem.location + offsets.get(gem_object, Vector())

    for _pass in range(_CONSTRAINT_PASSES):
        changed = False

        for gem_object1, gem_object2, gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, distances):
            if gem_object1 not in proposed or gem_object2 not in proposed:
                continue

            spacing = max(gem1.spacing, gem2.spacing)
            compressed_spacing = spacing - min(spacing_tolerance, spacing)
            target_distance = gem1.radius + gem2.radius + compressed_spacing
            offset_vector = proposed[gem_object2] - proposed[gem_object1]
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

            mobility1 = _gem_mobility(gem_object1, gem1, selected_keys, distance1, falloff_distance)
            mobility2 = _gem_mobility(gem_object2, gem2, selected_keys, distance2, falloff_distance)
            mobility_total = mobility1 + mobility2

            if not mobility_total:
                continue

            correction = direction * (target_distance - distance) * constraint_alpha

            if mobility1:
                proposed[gem_object1] -= correction * (mobility1 / mobility_total)

            if mobility2:
                proposed[gem_object2] += correction * (mobility2 / mobility_total)

            changed = True

        if not changed:
            break

    return {
        gem_object: proposed_location - gems[gem_object].location
        for gem_object, proposed_location in proposed.items()
        if gem_object in gems and not _is_stationary_gem(gem_object, gems[gem_object], selected_keys)
    }


def _nearest_selected_distance(gem: _Gem, selected_gems: tuple[_Gem, ...]) -> float:
    if not selected_gems:
        return float("inf")

    return min(_girdle_gap(gem, selected_gem) for selected_gem in selected_gems)


def _distance_map(
    gems: dict[bpy.types.Object, _Gem],
    selected_keys: frozenset[bpy.types.Object],
    falloff_distance: float,
) -> dict[bpy.types.Object, float]:
    distances = {gem_object: 0.0 for gem_object in selected_keys if gem_object in gems}

    if not distances:
        return distances

    selected_gems = tuple(gems[pointer] for pointer in distances)
    queue = deque(distances)

    while queue:
        gem_object = queue.popleft()

        for gem_object_next in _STATE.links.get(gem_object, ()):
            if gem_object_next not in gems or gem_object_next in selected_keys:
                continue

            distance_next = _nearest_selected_distance(gems[gem_object_next], selected_gems)

            if distance_next > falloff_distance:
                continue

            if distance_next < distances.get(gem_object_next, float("inf")):
                distances[gem_object_next] = distance_next
                queue.append(gem_object_next)

    return distances


def _is_surface_snap_target(context, object_) -> bool:
    tool_settings = context.scene.tool_settings

    if object_ is None or not object_.visible_get() or getattr(object_, "hide_surface_pick", False):
        return False

    if _is_editable_gem(object_):
        return False

    if tool_settings.use_snap_selectable and object_.hide_select:
        return False

    return True


def _ray_cast_surface(context, origin: Vector, direction: Vector, max_distance: float) -> tuple[Vector, Vector] | None:
    if direction.length_squared == 0.0 or max_distance <= 0.0:
        return None

    scene = context.scene
    depsgraph = context.evaluated_depsgraph_get()
    tool_settings = scene.tool_settings
    direction = direction.normalized()
    distance_left = max_distance
    origin_current = origin

    while distance_left > 0.0:
        hit, location, normal, _index, object_, _matrix = scene.ray_cast(depsgraph, origin_current, direction, distance=distance_left)

        if not hit:
            return None

        travelled = (location - origin_current).length
        is_backface = normal.dot(direction) > 0.0

        if _is_surface_snap_target(context, object_) and not (tool_settings.use_snap_backface_culling and is_backface):
            return location.copy(), normal.normalized()

        step = max(travelled, _SNAP_RAY_EPSILON)
        origin_current = location + direction * _SNAP_RAY_EPSILON
        distance_left -= step + _SNAP_RAY_EPSILON

    return None


def _closest_surface_point(context, location: Vector) -> tuple[Vector, Vector] | None:
    depsgraph = context.evaluated_depsgraph_get()
    best_distance_squared = None
    best_hit = None

    for mesh_object in context.visible_objects:
        if mesh_object.type != "MESH" or not _is_surface_snap_target(context, mesh_object):
            continue

        local_location = mesh_object.matrix_world.inverted() @ location
        hit, nearest_location, normal, _index = mesh_object.closest_point_on_mesh(local_location, depsgraph=depsgraph)

        if not hit:
            continue

        location_world = mesh_object.matrix_world @ nearest_location
        normal_world = mesh_object.matrix_world.to_3x3() @ normal

        if normal_world.length_squared == 0.0:
            continue

        distance_squared = (location_world - location).length_squared

        if best_distance_squared is None or distance_squared < best_distance_squared:
            best_distance_squared = distance_squared
            best_hit = (location_world.copy(), normal_world.normalized())

    return best_hit


def _snap_surface(
    context,
    gem: _Gem,
    next_location: Vector,
    current_rotation,
) -> tuple[Vector, Vector | None]:
    axis = current_rotation @ Vector((0.0, 0.0, 1.0))

    if axis.length_squared == 0.0:
        axis = Vector((0.0, 0.0, 1.0))
    else:
        axis.normalize()

    snap_distance = max(max(gem.object.dimensions), gem.radius * 4.0, unit.Scale().to_scene(1.0))
    candidates = []

    for direction in (axis, -axis):
        origin = next_location - direction * snap_distance
        hit = _ray_cast_surface(context, origin, direction, snap_distance * 2.0)

        if hit is not None:
            candidates.append(hit)

    if candidates:
        location, normal = min(candidates, key=lambda item: (item[0] - next_location).length_squared)
        return location, normal

    if (hit := _closest_surface_point(context, next_location)) is not None:
        return hit

    return next_location, None


def _align_rotation_to_normal(current_rotation, normal: Vector):
    if normal.length_squared == 0.0:
        return current_rotation

    axis_current = current_rotation @ Vector((0.0, 0.0, 1.0))

    if axis_current.length_squared == 0.0:
        return current_rotation

    try:
        return axis_current.normalized().rotation_difference(normal.normalized()) @ current_rotation
    except ValueError:
        return current_rotation


def _is_same_rotation(rotation1, rotation2) -> bool:
    return rotation1.rotation_difference(rotation2).angle < 1e-6


def _snap_transform(context, gem: _Gem, next_location: Vector, current_rotation):
    if context.scene.jewelcraft.gems_magnet_snap_to_face:
        surface_location, normal = _snap_surface(context, gem, next_location, current_rotation)

        if normal is not None:
            return surface_location, _align_rotation_to_normal(current_rotation, normal)

        return surface_location, current_rotation

    return next_location, current_rotation


def _move_gem(context, gem: _Gem, offset: Vector) -> bool:
    locked_axes = gem.object.lock_location
    offset = Vector(
        (
            0.0 if locked_axes[0] else offset.x,
            0.0 if locked_axes[1] else offset.y,
            0.0 if locked_axes[2] else offset.z,
        )
    )

    if offset.length_squared == 0.0:
        return False

    matrix_world = gem.object.matrix_world.copy()
    current_rotation = matrix_world.to_quaternion()
    next_location, next_rotation = _snap_transform(
        context,
        gem,
        gem.location + offset,
        current_rotation,
    )
    location_changed = (next_location - gem.location).length_squared > 0.0
    rotation_changed = not _is_same_rotation(next_rotation, current_rotation)

    if not location_changed and not rotation_changed:
        return False

    if rotation_changed:
        gem.object.matrix_world = Matrix.LocRotScale(next_location, next_rotation, matrix_world.to_scale())
    else:
        matrix_world.translation = next_location
        gem.object.matrix_world = matrix_world

    gem.location = next_location
    return True


def _distance_mobility(selected_distance: float, falloff_distance: float) -> float:
    if selected_distance < 0.0 or selected_distance > falloff_distance or falloff_distance <= 0.0:
        return 0.0

    return 1.0 - selected_distance / falloff_distance


def _distance_influence(selected_distance: float, falloff_distance: float) -> float:
    return _distance_mobility(selected_distance, falloff_distance)


def _spring_offsets(
    gem1: _Gem,
    gem2: _Gem,
    gem_object1: bpy.types.Object,
    gem_object2: bpy.types.Object,
    selected_keys: frozenset[bpy.types.Object],
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

    mobility1 = _gem_mobility(gem_object1, gem1, selected_keys, selected_distance1, falloff_distance)
    mobility2 = _gem_mobility(gem_object2, gem2, selected_keys, selected_distance2, falloff_distance)
    mobility_total = mobility1 + mobility2

    if not mobility_total:
        zero = Vector()
        return zero, zero

    target_distance = gem1.radius + gem2.radius + spacing
    influence = max(
        _distance_influence(selected_distance1, falloff_distance),
        _distance_influence(selected_distance2, falloff_distance),
    )
    alpha = 1.0 - exp(-_BASE_STRENGTH * strength * influence * delta_time)
    correction = direction * (distance - target_distance) * alpha

    return correction * (mobility1 / mobility_total), -correction * (mobility2 / mobility_total)
