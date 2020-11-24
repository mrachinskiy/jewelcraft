# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2020  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import os
from math import tau, pi, sin, cos, modf
from functools import lru_cache
from typing import Tuple, Set, Sequence, Union, Optional, List, Iterable

import bpy
from bpy.types import Object, BlendData, ID, Space
from bpy.app.translations import pgettext_iface as _
from mathutils import Matrix, Vector, kdtree

from . import mesh, unit
from .. import var


ObjectData = Tuple[Vector, float, Matrix]
Color = Tuple[float, float, float, float]
BoundBox = List[Vector]
Loc = Dim = BBoxMin = BBoxMax = Tuple[float, float, float]


# Gem
# ------------------------------------


def ct_calc(stone: str, cut: str, size: float) -> float:
    try:
        dens = unit.convert_cm3_mm3(var.STONES[stone].density)
        cut = var.CUTS[cut]
        vol_corr = cut.vol_correction
        shape = cut.vol_shape
    except KeyError:
        return 0

    w, l, h = size

    if shape is var.VOL_CONE:
        vol = pi * (l / 2) * (w / 2) * (h / 3)
    elif shape is var.VOL_PYRAMID:
        vol = l * w * h / 3
    elif shape is var.VOL_PRISM:
        vol = l * w * (h / 2)
    elif shape is var.VOL_TETRAHEDRON:
        vol = l * w * h / 6

    g = vol * vol_corr * dens
    ct = unit.convert_g_ct(g)

    return round(ct, 3)


def get_cut(self, ob: Object) -> None:
    self.gem_w, self.gem_l, self.gem_h = ob.dimensions
    self.cut = ob["gem"]["cut"] if "gem" in ob else None
    self.shape_rnd = self.shape_sq = self.shape_rect = self.shape_tri = self.shape_fant = False

    try:
        shape = var.CUTS[self.cut].shape
    except KeyError:
        shape = var.SHAPE_ROUND

    if shape is var.SHAPE_SQUARE:
        self.shape_sq = True
    elif shape is var.SHAPE_RECTANGLE:
        self.shape_rect = True
    elif shape is var.SHAPE_TRIANGLE:
        self.shape_tri = True
    elif shape is var.SHAPE_FANTASY:
        self.shape_fant = True
    else:
        self.shape_rnd = True


def nearest_coords(rad1: float, rad2: float, mat1: Matrix, mat2: Matrix) -> Tuple[Vector, Vector]:
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


@lru_cache(maxsize=128)
def girdle_coords(radius: float, mat: Matrix) -> Tuple[Vector, ...]:
    angle = tau / 64

    return tuple(
        (
            mat @ Vector(
                (
                    sin(i * angle) * radius,
                    cos(i * angle) * radius,
                    0.0,
                )
            )
        ).freeze()
        for i in range(64)
    )


def gem_overlap(context, data: Sequence[ObjectData], threshold: float, first_match=False) -> Union[Set[int], bool]:
    kd = kdtree.KDTree(len(data))

    for i, (loc, _, _) in enumerate(data):
        kd.insert(loc, i)

    kd.balance()

    UnitScale = unit.Scale(context)
    from_scene_scale = UnitScale.from_scene
    to_scene_scale = UnitScale.to_scene

    overlap_indices = set()
    seek_range = to_scene_scale(4.0)

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


def to_int(x: float) -> Union[int, float]:
    if x.is_integer():
        return int(x)
    return x


# Material
# ------------------------------------


def color_rnd() -> Color:
    import random
    seq = (0.0, 0.5, 1.0)
    return random.choice(seq), random.choice(seq), random.choice(seq), 1.0


def add_material(ob: Object, name="New Material", color: Optional[Color] = None, is_gem=False) -> None:
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


def asset_import(filepath: str, ob_name=False, me_name=False) -> BlendData:

    with bpy.data.libraries.load(filepath) as (data_from, data_to):

        if ob_name:
            data_to.objects = [ob_name]

        if me_name:
            data_to.meshes = [me_name]

    return data_to


def asset_import_batch(filepath: str) -> BlendData:

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.objects = data_from.objects
        data_to.collections = data_from.collections

    return data_to


def asset_export(data_blocks: Set[ID], filepath: str) -> None:
    folder = os.path.dirname(filepath)

    if not os.path.exists(folder):
        os.makedirs(folder)

    bpy.data.libraries.write(filepath, data_blocks, compress=True)


def render_preview(width: int, height: int, filepath: str, compression=100, gamma: Optional[float] = None) -> None:
    scene = bpy.context.scene
    render_props = scene.render
    image_props = render_props.image_settings
    view_props = scene.view_settings
    shading_type = bpy.context.space_data.shading.type

    render_config = {
        "filepath": filepath,
        "resolution_x": width,
        "resolution_y": height,
        "resolution_percentage": 100,
        "film_transparent": True,
    }

    image_config = {
        "file_format": "PNG",
        "color_mode": "RGBA",
        "compression": compression,
    }

    view_config = {}

    if shading_type in {"WIREFRAME", "SOLID"}:
        view_config["view_transform"] = "Standard"
        view_config["look"] = "None"

    if gamma is not None:
        view_config["gamma"] = gamma

    configs = [
        [render_props, render_config],
        [image_props, image_config],
        [view_props, view_config],
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


def show_window(width: int, height: int, area_type: Optional[str] = None, space_data: Optional[Space] = None) -> None:
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


def bm_to_scene(bm, name="New object", color: Optional[Color] = None) -> None:
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


def ob_copy_and_parent(ob: Object, parents: Iterable[Object]) -> None:
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


def mod_curve_off(ob: Object, mat: Matrix) -> Tuple[BoundBox, Optional[Object]]:
    curve = None

    for mod in ob.modifiers:
        if mod.type == "CURVE" and mod.object:

            if mod.show_viewport:
                mod.show_viewport = False
                bpy.context.view_layer.update()
                mod.show_viewport = True

            curve = mod.object
            break

    return [mat @ Vector(x) for x in ob.bound_box], curve


def calc_bbox(obs: Iterable[Object]) -> Tuple[Loc, Dim, BBoxMin, BBoxMax]:
    bbox = []

    for ob in obs:
        bbox += [ob.matrix_world @ Vector(x) for x in ob.bound_box]

    x_min = min(x[0] for x in bbox)
    y_min = min(x[1] for x in bbox)
    z_min = min(x[2] for x in bbox)

    x_max = max(x[0] for x in bbox)
    y_max = max(x[1] for x in bbox)
    z_max = max(x[2] for x in bbox)

    x_loc = (x_max + x_min) / 2
    y_loc = (y_max + y_min) / 2
    z_loc = (z_max + z_min) / 2

    x_dim = x_max - x_min
    y_dim = y_max - y_min
    z_dim = z_max - z_min

    return (
        (x_loc, y_loc, z_loc),
        (x_dim, y_dim, z_dim),
        (x_min, y_min, z_min),
        (x_max, y_max, z_max),
    )


def to_ring_size(cir: float, size_format: str) -> Union[float, int, str]:
    if size_format in {"US", "JP"}:
        size = round((cir - var.CIR_BASE_US) / var.CIR_STEP_US, 2)

        if size >= 0.0:

            if size_format == "US":
                return to_int(size)

            for size_jp, size_us in enumerate(var.MAP_SIZE_JP_TO_US, start=1):
                if size_us - 0.2 < size < size_us + 0.2:
                    return size_jp

    if size_format == "UK":
        import string

        size_raw = (cir - var.CIR_BASE_UK) / var.CIR_STEP_UK

        if size_raw >= 0.0:
            fraction, integer = modf(size_raw)
            half_size = 0.25 < fraction < 0.75
            if fraction > 0.75:
                integer += 1.0

            if integer < len(string.ascii_uppercase):
                size = string.ascii_uppercase[int(integer)]
                if half_size:
                    size += " 1/2"
                return size

    if size_format == "CH":
        size = round(cir - 40.0, 2)
        if size >= 0.0:
            return to_int(size)

    return "[NO CORRESPONDING SIZE]"
