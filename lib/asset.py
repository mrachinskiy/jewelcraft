# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from collections.abc import Iterator
from pathlib import Path

import bpy
from bpy.app.translations import pgettext_iface as _
from bpy.types import ID, BlendData, Depsgraph, DepsgraphObjectInstance, Object, Space
from mathutils import Matrix, Vector, kdtree

from . import mesh, unit

LocRadMat = tuple[Vector, float, Matrix]
Color = tuple[float, float, float, float]
BoundBox = list[Vector]


# Gem
# ------------------------------------


def iter_gems(depsgraph: Depsgraph) -> Iterator[tuple[DepsgraphObjectInstance, Object, Object]]:
    for dup in depsgraph.object_instances:
        if dup.is_instance:
            ob = dup.instance_object.original
            instancer = dup.parent.original
        else:
            ob = instancer = dup.object.original

        if "gem" not in ob or not instancer.visible_get():  # T74368
            continue

        yield dup, ob, instancer


def gem_transform(dup: DepsgraphObjectInstance) -> LocRadMat:
    loc, rot, sca = dup.matrix_world.decompose()

    if dup.is_instance:
        bbox = dup.instance_object.original.bound_box
        x, y, z = bbox[0]
        dim = Vector((
            bbox[4][0] - x,
            bbox[3][1] - y,
            bbox[1][2] - z,
        ))
        rad = max(dim.xy * sca.xy) / 2
    else:
        dim = dup.object.original.dimensions
        rad = max(dim.xy) / 2

    mat = Matrix.LocRotScale(loc, rot, (1.0, 1.0, 1.0))
    loc.freeze()
    mat.freeze()

    return loc, rad, mat


def nearest_coords(rad1: float, rad2: float, mat1: Matrix, mat2: Matrix) -> tuple[Vector, Vector]:
    vec1 = mat1.inverted() @ mat2.translation
    vec1.z = 0.0

    if not vec1.length:
        vec1.x = rad1
        return mat1 @ vec1, mat2 @ Vector((rad2, 0.0, 0.0))

    vec1 *= rad1 / vec1.length

    vec2 = mat2.inverted() @ mat1.translation
    vec2.z = 0.0
    vec2 *= rad2 / vec2.length

    return mat1 @ vec1, mat2 @ vec2


def calc_gap(co1: Vector, co2: Vector, loc1: Vector, dist_locs: float, rad1: float) -> float:
    if (loc1 - co2).length < rad1 or dist_locs < rad1:
        return -(co1 - co2).length

    return (co1 - co2).length


def gem_overlap(data: list[LocRadMat], threshold: float, first_match=False) -> set[int] | bool:
    kd = kdtree.KDTree(len(data))

    for i, (loc, _, _) in enumerate(data):
        kd.insert(loc, i)

    kd.balance()

    UnitScale = unit.Scale()
    from_scene_scale = UnitScale.from_scene

    overlap_indices = set()
    seek_range = UnitScale.to_scene(4.0)

    for i1, (loc1, rad1, mat1) in enumerate(data):

        if i1 in overlap_indices:
            continue

        for loc2, i2, dis_obs in kd.find_range(loc1, seek_range):

            _, rad2, mat2 = data[i2]
            dis_gap = dis_obs - (rad1 + rad2)

            if dis_gap > threshold or i1 == i2:
                continue

            co1, co2 = nearest_coords(rad1, rad2, mat1, mat2)
            dis_gap = from_scene_scale(calc_gap(co1, co2, loc1, dis_obs, rad1))

            if dis_gap < threshold:
                if first_match:
                    return True
                overlap_indices.add(i1)
                break

    if first_match:
        return False

    return overlap_indices


# Material
# ------------------------------------


def color_rnd() -> Color:
    import random
    seq = (0.0, 0.5, 1.0)
    return random.choice(seq), random.choice(seq), random.choice(seq), 1.0


def add_material(ob: Object, name="New Material", color: Color | None = None, is_gem=False) -> None:
    mat = bpy.data.materials.get(name)

    if not mat:
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = color

        if bpy.context.scene.render.engine in {"CYCLES", "BLENDER_EEVEE"}:
            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            for node in nodes:
                nodes.remove(node)

            node = nodes.new("ShaderNodeBsdfPrincipled")
            node.inputs["Base Color"].default_value = color
            node.inputs["Roughness"].default_value = 0.0

            if is_gem:
                node.inputs["Transmission"].default_value = 1.0
                node.inputs["IOR"].default_value = 2.42
            else:
                node.inputs["Metallic"].default_value = 1.0

            node.location = (0.0, 0.0)

            node_out = nodes.new("ShaderNodeOutputMaterial")
            node_out.location = (400.0, 0.0)

            mat.node_tree.links.new(node.outputs["BSDF"], node_out.inputs["Surface"])

    if ob.material_slots:
        ob.material_slots[0].material = mat
    else:
        ob.data.materials.append(mat)


# Asset
# ------------------------------------


def asset_import(filepath: Path, ob_name=False, me_name=False, ng_name=False) -> BlendData:

    with bpy.data.libraries.load(str(filepath)) as (data_from, data_to):

        if ob_name:
            data_to.objects = [ob_name]

        if me_name:
            data_to.meshes = [me_name]

        if ng_name:
            data_to.node_groups = [ng_name]

    return data_to


def asset_import_batch(filepath: str) -> BlendData:

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.objects = data_from.objects
        data_to.collections = data_from.collections

    return data_to


def asset_export(data_blocks: set[ID], filepath: Path) -> None:
    if not filepath.parent.exists():
        filepath.parent.mkdir(parents=True)

    bpy.data.libraries.write(str(filepath), data_blocks, compress=True)


def render_preview(width: int, height: int, filepath: Path, compression=100, gamma: float | None = None, use_transparent=True) -> None:
    scene = bpy.context.scene
    render_props = scene.render
    image_props = render_props.image_settings
    view_props = scene.view_settings
    overlay_props = bpy.context.space_data.overlay
    shading_props = bpy.context.space_data.shading

    render_config = {
        "filepath": str(filepath),
        "resolution_x": width,
        "resolution_y": height,
        "resolution_percentage": 100,
        "film_transparent": use_transparent,
        "dither_intensity": 0.0,
    }

    image_config = {
        "file_format": "PNG",
        "color_mode": "RGBA",
        "compression": compression,
    }

    view_config = {}

    if shading_props.type in {"WIREFRAME", "SOLID"}:
        view_config["view_transform"] = "Standard"
        view_config["look"] = "None"

    if gamma is not None:
        view_config["gamma"] = gamma

    overlay_config = {
        "show_overlays": False,
    }

    shading_config = {
        "show_object_outline": False,
    }

    configs = [
        [render_props, render_config],
        [image_props, image_config],
        [view_props, view_config],
        [overlay_props, overlay_config],
        [shading_props, shading_config],
    ]

    # Apply settings
    # ---------------------------

    for props, config in configs:
        for k, v in config.items():
            x = getattr(props, k)
            setattr(props, k, v)
            config[k] = x

    # Render and save
    # ---------------------------

    bpy.ops.render.opengl(write_still=True)

    # Revert settings
    # ---------------------------

    for props, config in configs:
        for k, v in config.items():
            setattr(props, k, v)


def show_window(width: int, height: int, area_type: str | None = None, space_data: Space | None = None) -> None:
    render = bpy.context.scene.render

    render_config = {
        "resolution_x": width,
        "resolution_y": height,
        "resolution_percentage": 100,
    }

    prefs = bpy.context.preferences
    _is_dirty = prefs.is_dirty
    display_type = "WINDOW"

    # Apply settings
    # ---------------------------

    for k, v in render_config.items():
        x = getattr(render, k)
        setattr(render, k, v)
        render_config[k] = x

    prefs.view.render_display_type, display_type = display_type, prefs.view.render_display_type

    # Invoke window
    # ---------------------------

    bpy.ops.render.view_show("INVOKE_DEFAULT")

    # Set window
    # ---------------------------

    area = bpy.context.window_manager.windows[-1].screen.areas[0]

    if area_type is not None:
        area.type = area_type

    if space_data is not None:
        space = area.spaces[0]
        for k, v in space_data.items():
            setattr(space, k, v)

    # Revert settings
    # ---------------------------

    for k, v in render_config.items():
        setattr(render, k, v)

    prefs.view.render_display_type = display_type
    prefs.is_dirty = _is_dirty


# Object
# ------------------------------------


def bm_to_scene(bm, name="New object", color: Color | None = None) -> None:
    space_data = bpy.context.space_data
    use_local_view = bool(space_data.local_view)

    bpy.context.view_layer.update()
    size = bpy.context.object.dimensions.y

    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()

    for parent in bpy.context.selected_objects:

        ob = bpy.data.objects.new(name, me)

        for coll in parent.users_collection:
            coll.objects.link(ob)

        if use_local_view:
            ob.local_view_set(space_data, True)

        ob.location = parent.location
        ob.rotation_euler = parent.rotation_euler
        ob.scale *= parent.dimensions.y / size
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_basis.inverted()

        add_material(ob, name=name, color=color)


def ob_copy_and_parent(ob: Object, parents: list[Object]) -> None:
    is_orig = True
    space_data = bpy.context.space_data
    use_local_view = bool(space_data.local_view)

    for parent in parents:
        if is_orig:
            ob_copy = ob
            is_orig = False
        else:
            ob_copy = ob.copy()

        for coll in parent.users_collection:
            coll.objects.link(ob_copy)

        if use_local_view:
            ob_copy.local_view_set(space_data, True)

        ob_copy.select_set(True)
        ob.location = parent.location
        ob.rotation_euler = parent.rotation_euler
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_basis.inverted()


def ob_copy_to_faces(ob: Object) -> None:
    mats = mesh.face_pos()

    if mats:
        ob.matrix_world = mats.pop()
        collection = bpy.context.collection
        space_data = bpy.context.space_data
        use_local_view = bool(space_data.local_view)

        for mat in mats:
            ob_copy = ob.copy()
            collection.objects.link(ob_copy)
            ob_copy.matrix_world = mat
            ob_copy.select_set(True)

            if use_local_view:
                ob_copy.local_view_set(space_data, True)


def apply_scale(ob: Object) -> None:
    mat = Matrix.Diagonal(ob.scale).to_4x4()
    ob.data.transform(mat)
    ob.scale = (1.0, 1.0, 1.0)


def mod_curve_off(ob: Object, mat: Matrix = None) -> tuple[Object | None, BoundBox]:
    curve = None

    for mod in ob.modifiers:
        if mod.type == "CURVE" and mod.object:

            if mod.show_viewport:
                mod.show_viewport = False
                bpy.context.view_layer.update()
                mod.show_viewport = True

            curve = mod.object
            break

    if mat is None:
        return curve

    return curve, [mat @ Vector(x) for x in ob.bound_box]


class ObjectsBoundBox:
    __slots__ = "min", "max", "location", "dimensions"

    def __init__(self, obs: list[Object]) -> None:
        bbox = []

        for ob in obs:
            bbox += [ob.matrix_world @ Vector(x) for x in ob.bound_box]

        self.min = Vector((
            min(x[0] for x in bbox),
            min(x[1] for x in bbox),
            min(x[2] for x in bbox),
        ))
        self.max = Vector((
            max(x[0] for x in bbox),
            max(x[1] for x in bbox),
            max(x[2] for x in bbox),
        ))
        self.location = (self.max + self.min) / 2
        self.dimensions = self.max - self.min
