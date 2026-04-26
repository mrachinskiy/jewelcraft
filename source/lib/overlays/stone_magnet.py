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
_CONSTRAINT_PASSES = 3
_CONSTRAINT_STRENGTH = 0.5
_SPACING_COMPRESSION_TOLERANCE = 0.15
_SUPPORTED_SNAP_ELEMENTS = frozenset({"GRID", "INCREMENT"})
_SURFACE_SNAP_ELEMENTS = frozenset({"FACE", "FACE_MIDPOINT"})
_SURFACE_SNAP_INDIVIDUAL = frozenset({"FACE_PROJECT", "FACE_NEAREST"})
_SNAP_RAY_EPSILON = 0.0001
_ROTATION_EPSILON = 1e-6


class _Gem:
    __slots__ = ("object", "location", "radius", "spacing", "pointer")

    def __init__(self, gem_object: bpy.types.Object, spacing: float) -> None:
        self.object = gem_object
        self.location = gem_object.matrix_world.translation.copy()
        self.radius = max(gem_object.dimensions.xy) / 2.0
        self.spacing = spacing
        self.pointer = gem_object.as_pointer()


class _State:
    __slots__ = ("drag_snapshot", "dragging", "drag_selected_start", "links", "prev_selected", "selected_keys", "time_prev")

    def __init__(self) -> None:
        self.drag_snapshot: dict[str, Matrix] = {}
        self.dragging = False
        self.drag_selected_start: dict[str, Vector] = {}
        self.links: dict[int, tuple[int, ...]] = {}
        self.prev_selected: dict[int, Vector] = {}
        self.selected_keys: frozenset[int] = frozenset()
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
    if self.show_stone_magnet:
        handler_add()
    else:
        handler_del()


def _undo_post(_scene) -> None:
    _STATE.reset()


def _timer() -> float | None:
    context = bpy.context
    wm_props = getattr(getattr(context, "window_manager", None), "jewelcraft", None)

    if wm_props is None or not wm_props.show_stone_magnet:
        _STATE.reset()
        return None

    if context.window_manager.is_interface_locked or context.mode != "OBJECT":
        _STATE.clear_drag()
        return _TIMER_INTERVAL

    selected_gems = _selected_gems(context)
    selected_positions = _selected_positions(selected_gems)
    selected_keys = frozenset(selected_positions)

    if selected_keys != _STATE.selected_keys:
        _STATE.clear_drag()
        _STATE.selected_keys = selected_keys

    current_time = perf_counter()
    delta_time = _delta_time(current_time)

    if not selected_gems:
        _STATE.prev_selected = selected_positions
        return _TIMER_INTERVAL

    scene_props = context.scene.jewelcraft
    gems = _collect_gems(context, scene_props, selected_gems)
    to_scene = unit.Scale().to_scene
    search_distance = to_scene(scene_props.stone_magnet_distance)
    max_distance = to_scene(scene_props.stone_magnet_max_distance)

    if len(gems) < 2:
        _STATE.clear_drag()
        _STATE.prev_selected = selected_positions
        return _TIMER_INTERVAL

    transform_operator = _active_translation_transform_operator(context)

    if transform_operator is not None:
        selection_moved = _selected_moved(selected_positions)

        if selection_moved and not _STATE.dragging:
            _start_drag(gems, selected_keys, search_distance, max_distance)

        if _STATE.dragging and selection_moved:
            _apply_magnet(
                context,
                gems,
                selected_keys,
                search_distance,
                max_distance,
                scene_props.stone_magnet_strength,
                delta_time,
                transform_operator,
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


def _selected_positions(selected_gems: list[bpy.types.Object]) -> dict[int, Vector]:
    return {gem_object.as_pointer(): gem_object.matrix_world.translation.copy() for gem_object in selected_gems}


def _selected_moved(selected_positions: dict[int, Vector]) -> bool:
    if _STATE.selected_keys != frozenset(_STATE.prev_selected):
        return False

    threshold = _move_threshold()

    for pointer, location in selected_positions.items():
        previous_location = _STATE.prev_selected.get(pointer)
        if previous_location is not None and (location - previous_location).length > threshold:
            return True

    return False


def _selected_gems(context) -> list[bpy.types.Object]:
    return [gem_object for gem_object in context.selected_objects if _is_editable_gem(gem_object)]


def _collect_gems(context, props, selected_gems: list[bpy.types.Object]) -> dict[int, _Gem]:
    to_scene = unit.Scale().to_scene
    default_spacing = float(props.overlay_spacing)
    use_overrides = props.overlay_use_overrides
    selected_collection_pointers = (
        {
            collection.as_pointer()
            for gem_object in selected_gems
            for collection in gem_object.users_collection
        }
        if props.stone_magnet_same_collection and selected_gems
        else None
    )
    gems = {}

    for gem_object in context.visible_objects:
        if not _is_editable_gem(gem_object):
            continue

        if selected_collection_pointers is not None and not any(
            collection.as_pointer() in selected_collection_pointers
            for collection in gem_object.users_collection
        ):
            continue

        spacing = default_spacing

        if use_overrides and "gem_overlay" in gem_object:
            spacing = float(gem_object["gem_overlay"].get("spacing", default_spacing))

        gem = _Gem(gem_object, to_scene(spacing))
        gems[gem.pointer] = gem

    return gems


def _is_editable_gem(gem_object: bpy.types.Object | None) -> bool:
    return gem_object is not None and "gem" in gem_object and gem_object.visible_get() and gem_object.is_editable


def _is_fully_translation_locked(gem_object: bpy.types.Object) -> bool:
    return all(bool(is_locked) for is_locked in gem_object.lock_location)


def _is_stationary_gem(pointer: int, gem: _Gem, selected_keys: frozenset[int]) -> bool:
    return pointer in selected_keys or _is_fully_translation_locked(gem.object)


def _gem_mobility(
    pointer: int,
    gem: _Gem,
    selected_keys: frozenset[int],
    selected_distance: float,
    max_distance: float,
) -> float:
    if _is_stationary_gem(pointer, gem, selected_keys):
        return 0.0

    return _distance_mobility(selected_distance, max_distance)


def _active_translation_transform_operator(context):
    window = context.window

    if window is None:
        return None

    for operator in window.modal_operators:
        if operator.bl_idname == "TRANSFORM_OT_translate":
            return operator

        if operator.bl_idname == "TRANSFORM_OT_transform" and getattr(operator, "mode", None) == "TRANSLATION":
            return operator

    return None


def _merge_links(existing: dict[int, tuple[int, ...]], incoming: dict[int, tuple[int, ...]]) -> dict[int, tuple[int, ...]]:
    merged: dict[int, set[int]] = {pointer: set(neighbors) for pointer, neighbors in existing.items()}

    for pointer, neighbors in incoming.items():
        merged.setdefault(pointer, set()).update(neighbors)

    return {pointer: tuple(sorted(neighbors)) for pointer, neighbors in merged.items() if neighbors}


def _girdle_gap(gem1: _Gem, gem2: _Gem, center_distance: float | None = None) -> float:
    if center_distance is None:
        center_distance = (gem1.location - gem2.location).length

    return max(center_distance - gem1.radius - gem2.radius, 0.0)


def _build_links(gems: dict[int, _Gem], search_distance: float) -> dict[int, tuple[int, ...]]:
    gem_items = tuple(gems.values())
    links: dict[int, list[int]] = {gem.pointer: [] for gem in gem_items}
    kd_tree = kdtree.KDTree(len(gem_items))
    max_radius = max(gem.radius for gem in gem_items)

    for index, gem in enumerate(gem_items):
        kd_tree.insert(gem.location, index)

    kd_tree.balance()

    for index, gem1 in enumerate(gem_items):
        search_radius = gem1.radius + max_radius + search_distance

        for _coordinate, index2, center_distance in kd_tree.find_range(gem1.location, search_radius):
            if index2 <= index:
                continue

            gem2 = gem_items[index2]

            if _girdle_gap(gem1, gem2, center_distance) > search_distance:
                continue

            links[gem1.pointer].append(gem2.pointer)
            links[gem2.pointer].append(gem1.pointer)

    return {pointer: tuple(neighbors) for pointer, neighbors in links.items() if neighbors}


def _iter_link_pairs(gems: dict[int, _Gem], distances: dict[int, float]):
    for pointer1, neighbors in _STATE.links.items():
        gem1 = gems.get(pointer1)
        distance1 = distances.get(pointer1)

        if gem1 is None or distance1 is None:
            continue

        for pointer2 in neighbors:
            if pointer2 <= pointer1:
                continue

            gem2 = gems.get(pointer2)
            distance2 = distances.get(pointer2)

            if gem2 is None or distance2 is None:
                continue

            yield pointer1, pointer2, gem1, gem2, distance1, distance2


def _start_drag(
    gems: dict[int, _Gem],
    selected_keys: frozenset[int],
    search_distance: float,
    max_distance: float,
) -> None:
    _STATE.links = _build_links(gems, search_distance)

    if not _STATE.links:
        return

    distances = _distance_map(gems, selected_keys, max_distance)

    if len(distances) <= len(selected_keys):
        return

    _snapshot_drag_gems(gems, distances)
    _STATE.drag_selected_start = {
        gems[pointer].object.name: gems[pointer].location.copy()
        for pointer in selected_keys
        if pointer in gems
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


def _snapshot_drag_gems(gems: dict[int, _Gem], distances: dict[int, float]) -> None:
    for pointer in distances:
        gem = gems.get(pointer)

        if gem is None:
            continue

        _STATE.drag_snapshot.setdefault(gem.object.name, gem.object.matrix_world.copy())


def _apply_magnet(
    context,
    gems: dict[int, _Gem],
    selected_keys: frozenset[int],
    search_distance: float,
    max_distance: float,
    strength: float,
    delta_time: float,
    transform_operator,
) -> None:
    live_links = _build_links(gems, search_distance)

    if live_links:
        _STATE.links = _merge_links(_STATE.links, live_links)

    if not _STATE.links:
        return

    distances = _distance_map(gems, selected_keys, max_distance)

    if len(distances) <= len(selected_keys):
        return

    _snapshot_drag_gems(gems, distances)

    threshold = _move_threshold()
    offsets: dict[int, Vector] = {}

    for pointer1, pointer2, gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, distances):
        spacing = max(gem1.spacing, gem2.spacing)
        offset1, offset2 = _spring_offsets(
            gem1,
            gem2,
            pointer1,
            pointer2,
            selected_keys,
            spacing,
            distance1,
            distance2,
            max_distance,
            strength,
            delta_time,
        )

        if offset1.length_squared:
            offsets[pointer1] = offsets.get(pointer1, Vector()) + offset1

        if offset2.length_squared:
            offsets[pointer2] = offsets.get(pointer2, Vector()) + offset2

    offsets = _resolve_spacing_constraints(gems, distances, selected_keys, max_distance, offsets, strength, delta_time)

    for pointer, offset in offsets.items():
        if pointer in selected_keys:
            continue

        if offset.length <= threshold:
            continue

        gem = gems.get(pointer)

        if gem is None:
            continue

        _move_gem(context, transform_operator, gem, offset)


def _resolve_spacing_constraints(
    gems: dict[int, _Gem],
    distances: dict[int, float],
    selected_keys: frozenset[int],
    max_distance: float,
    offsets: dict[int, Vector],
    strength: float,
    delta_time: float,
) -> dict[int, Vector]:
    proposed: dict[int, Vector] = {}
    constraint_alpha = 1.0 - exp(-_BASE_STRENGTH * _CONSTRAINT_STRENGTH * strength * delta_time)

    if constraint_alpha <= 0.0:
        return offsets

    for pointer in distances:
        gem = gems.get(pointer)

        if gem is None:
            continue

        if _is_stationary_gem(pointer, gem, selected_keys):
            proposed[pointer] = gem.location.copy()
        else:
            proposed[pointer] = gem.location + offsets.get(pointer, Vector())

    for _pass in range(_CONSTRAINT_PASSES):
        changed = False

        for pointer1, pointer2, gem1, gem2, distance1, distance2 in _iter_link_pairs(gems, distances):
            if pointer1 not in proposed or pointer2 not in proposed:
                continue

            spacing = max(gem1.spacing, gem2.spacing)
            target_distance = gem1.radius + gem2.radius + spacing * (1.0 - _SPACING_COMPRESSION_TOLERANCE)
            offset_vector = proposed[pointer2] - proposed[pointer1]
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

            mobility1 = _gem_mobility(pointer1, gem1, selected_keys, distance1, max_distance)
            mobility2 = _gem_mobility(pointer2, gem2, selected_keys, distance2, max_distance)
            mobility_total = mobility1 + mobility2

            if not mobility_total:
                continue

            correction = direction * (target_distance - distance) * constraint_alpha

            if mobility1:
                proposed[pointer1] -= correction * (mobility1 / mobility_total)

            if mobility2:
                proposed[pointer2] += correction * (mobility2 / mobility_total)

            changed = True

        if not changed:
            break

    return {
        pointer: proposed_location - gems[pointer].location
        for pointer, proposed_location in proposed.items()
        if pointer in gems and not _is_stationary_gem(pointer, gems[pointer], selected_keys)
    }


def _nearest_selected_distance(gem: _Gem, selected_gems: tuple[_Gem, ...]) -> float:
    if not selected_gems:
        return float("inf")

    return min(_girdle_gap(gem, selected_gem) for selected_gem in selected_gems)


def _distance_map(gems: dict[int, _Gem], selected_keys: frozenset[int], max_distance: float) -> dict[int, float]:
    distances = {pointer: 0.0 for pointer in selected_keys if pointer in gems}

    if not distances:
        return distances

    selected_gems = tuple(gems[pointer] for pointer in distances)
    queue = deque(distances)

    while queue:
        pointer = queue.popleft()

        for pointer_next in _STATE.links.get(pointer, ()):
            if pointer_next not in gems or pointer_next in selected_keys:
                continue

            distance_next = _nearest_selected_distance(gems[pointer_next], selected_gems)

            if distance_next > max_distance:
                continue

            if distance_next < distances.get(pointer_next, float("inf")):
                distances[pointer_next] = distance_next
                queue.append(pointer_next)

    return distances


def _should_snap_translate(context, transform_operator) -> bool:
    tool_settings = context.scene.tool_settings

    if not tool_settings.use_snap_translate:
        return False

    if transform_operator is not None:
        return bool(tool_settings.use_snap or getattr(transform_operator, "snap", False))

    return bool(tool_settings.use_snap and tool_settings.use_snap_translate)


def _snap_elements(context, transform_operator) -> set[str]:
    elements = getattr(transform_operator, "snap_elements", None)

    if elements:
        return set(elements)

    return set(context.scene.tool_settings.snap_elements)


def _snap_individual_elements(context, transform_operator) -> set[str]:
    elements = getattr(transform_operator, "snap_elements_individual", None)

    if elements:
        return set(elements)

    return set(getattr(context.scene.tool_settings, "snap_elements_individual", ()))


def _snap_step(context, elements: set[str]) -> float:
    overlay = getattr(getattr(context, "space_data", None), "overlay", None)
    base_step = 0.0

    if overlay is not None:
        base_step = getattr(overlay, "grid_scale_unit", 0.0) or getattr(overlay, "grid_scale", 0.0)

    if not base_step:
        base_step = context.scene.unit_settings.scale_length or 1.0

    if "INCREMENT" in elements and "GRID" not in elements:
        subdivisions = getattr(overlay, "grid_subdivisions", 1) if overlay is not None else 1
        if subdivisions > 1:
            base_step /= subdivisions

    return base_step


def _round_vector(value: Vector, step: float, origin: Vector | None = None) -> Vector:
    if origin is None:
        origin = Vector()

    return Vector(
        (
            origin.x + round((value.x - origin.x) / step) * step,
            origin.y + round((value.y - origin.y) / step) * step,
            origin.z + round((value.z - origin.z) / step) * step,
        )
    )


def _snap_location(context, transform_operator, gem: _Gem, next_location: Vector) -> Vector:
    if not _should_snap_translate(context, transform_operator):
        return next_location

    elements = _snap_elements(context, transform_operator)

    if not elements or not elements <= _SUPPORTED_SNAP_ELEMENTS:
        return next_location

    step = _snap_step(context, elements)

    if step <= 0.0:
        return next_location

    tool_settings = context.scene.tool_settings
    use_absolute = "GRID" in elements or tool_settings.use_snap_grid_absolute

    if use_absolute:
        return _round_vector(next_location, step)

    matrix = _STATE.drag_snapshot.get(gem.object.name)

    if matrix is None:
        return next_location

    return _round_vector(next_location, step, matrix.translation)


def _should_snap_to_face(context, transform_operator) -> tuple[bool, set[str]]:
    if not context.scene.jewelcraft.stone_magnet_snap_to_face:
        return False, set()

    elements = _snap_elements(context, transform_operator)
    individual_elements = _snap_individual_elements(context, transform_operator)

    return bool(elements & _SURFACE_SNAP_ELEMENTS or individual_elements & _SURFACE_SNAP_INDIVIDUAL), individual_elements


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
    individual_elements: set[str],
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

    if individual_elements & _SURFACE_SNAP_INDIVIDUAL:
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


def _snap_transform(context, transform_operator, gem: _Gem, next_location: Vector, current_rotation):
    use_face_snap, individual_elements = _should_snap_to_face(context, transform_operator)

    if use_face_snap:
        surface_location, normal = _snap_surface(context, gem, next_location, current_rotation, individual_elements)

        if normal is not None:
            align_rotation = getattr(transform_operator, "use_snap_align_rotation", None)
            use_align_rotation = bool(align_rotation) if align_rotation is not None else bool(context.scene.tool_settings.use_snap_align_rotation)

            if use_align_rotation:
                return surface_location, _align_rotation_to_normal(current_rotation, normal)

        return surface_location, current_rotation

    if not _should_snap_translate(context, transform_operator):
        return next_location, current_rotation

    return _snap_location(context, transform_operator, gem, next_location), current_rotation


def _move_gem(context, transform_operator, gem: _Gem, offset: Vector) -> bool:
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
        transform_operator,
        gem,
        gem.location + offset,
        current_rotation,
    )
    location_changed = (next_location - gem.location).length_squared > 0.0
    rotation_changed = next_rotation.rotation_difference(current_rotation).angle > _ROTATION_EPSILON

    if not location_changed and not rotation_changed:
        return False

    if rotation_changed:
        gem.object.matrix_world = Matrix.LocRotScale(next_location, next_rotation, matrix_world.to_scale())
    else:
        matrix_world.translation = next_location
        gem.object.matrix_world = matrix_world

    gem.location = next_location
    return True


def _distance_mobility(selected_distance: float, max_distance: float) -> float:
    if selected_distance < 0.0 or selected_distance > max_distance or max_distance <= 0.0:
        return 0.0

    return 1.0 - selected_distance / max_distance


def _distance_influence(selected_distance: float, max_distance: float) -> float:
    return _distance_mobility(selected_distance, max_distance)


def _spring_offsets(
    gem1: _Gem,
    gem2: _Gem,
    pointer1: int,
    pointer2: int,
    selected_keys: frozenset[int],
    spacing: float,
    selected_distance1: float,
    selected_distance2: float,
    max_distance: float,
    strength: float,
    delta_time: float,
) -> tuple[Vector, Vector]:
    offset_vector = gem2.location - gem1.location
    distance = offset_vector.length

    if distance:
        direction = offset_vector / distance
    else:
        direction = Vector((1.0, 0.0, 0.0))

    mobility1 = _gem_mobility(pointer1, gem1, selected_keys, selected_distance1, max_distance)
    mobility2 = _gem_mobility(pointer2, gem2, selected_keys, selected_distance2, max_distance)
    mobility_total = mobility1 + mobility2

    if not mobility_total:
        zero = Vector()
        return zero, zero

    target_distance = gem1.radius + gem2.radius + spacing
    influence = max(
        _distance_influence(selected_distance1, max_distance),
        _distance_influence(selected_distance2, max_distance),
    )
    alpha = 1.0 - exp(-_BASE_STRENGTH * strength * influence * delta_time)
    correction = direction * (distance - target_distance) * alpha

    return correction * (mobility1 / mobility_total), -correction * (mobility2 / mobility_total)