# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
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
from math import tau, sin, cos
from functools import lru_cache

import bpy
from bpy.app.translations import pgettext_iface as _
from mathutils import Matrix, Vector, kdtree

from . import mesh, unit
from .. import var


# Gem
# ------------------------------------


def get_gem(self, context):
    ob = context.object

    self.gem_w = ob.dimensions[0]
    self.gem_l = ob.dimensions[1]
    self.gem_h = ob.dimensions[2]

    self.cut = ob["gem"]["cut"] if "gem" in ob else ""

    self.shape_rnd = self.shape_sq = self.shape_rect = self.shape_tri = self.shape_fant = False

    if self.cut in {"SQUARE", "ASSCHER", "PRINCESS", "CUSHION", "RADIANT", "FLANDERS", "OCTAGON"}:
        self.shape_sq = True
    elif self.cut in {"BAGUETTE", "EMERALD"}:
        self.shape_rect = True
    elif self.cut in {"TRILLION", "TRILLIANT", "TRIANGLE"}:
        self.shape_tri = True
    elif self.cut in {"PEAR", "MARQUISE", "HEART", "OVAL"}:
        self.shape_fant = True
    else:
        self.shape_rnd = True


def get_name(x):
    return x.replace("_", " ").title()


@lru_cache(maxsize=128)
def girdle_coords(radius, mat):
    coords = []
    app = coords.append
    angle = tau / 64

    for i in range(64):
        x = sin(i * angle) * radius
        y = cos(i * angle) * radius
        app(Vector((x, y, 0.0)))

    return tuple((mat @ co).freeze() for co in coords)


@lru_cache(maxsize=128)
def find_nearest(loc1, rad1, coords1, coords2):
    proximity = []
    app = proximity.append

    for co2 in coords2:
        app(((co2 - loc1).length, co2))
    dis, co2 = min(proximity, key=lambda x: x[0])

    if dis < rad1:
        return dis - rad1, co2, co2

    proximity.clear()

    for co1 in coords1:
        app(((co1 - co2).length, co1))
    dis, co1 = min(proximity, key=lambda x: x[0])

    return dis, co1, co2


def gem_overlap(context, data, threshold, first_match=False):
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

        girdle1 = girdle_coords(rad1, mat1)

        for loc2, i2, dis_ob in kd.find_range(loc1, seek_range):

            _, rad2, mat2 = data[i2]
            dis_gap = dis_ob - (rad1 + rad2)

            if dis_gap > threshold or i1 == i2:
                continue

            girdle2 = girdle_coords(rad2, mat2)
            dis_gap, _, _ = find_nearest(loc1, rad1, girdle1, girdle2)
            dis_gap = from_scene_scale(dis_gap)

            if dis_gap < threshold:
                if first_match:
                    return True
                overlap_indices.add(i1)
                break

    if first_match:
        return False

    return overlap_indices


def to_int(x):
    if x.is_integer():
        return int(x)
    return x


# Material
# ------------------------------------


def color_rnd():
    import random
    seq = (0.0, 0.5, 1.0)
    return random.choice(seq), random.choice(seq), random.choice(seq), 1.0


def add_material(ob, name="New Material", color=None, is_gem=False):
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


def user_asset_library_folder_object():
    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences

    if prefs.use_custom_asset_dir:
        return bpy.path.abspath(prefs.custom_asset_dir)

    return var.USER_ASSET_OBJECT_DIR


def user_asset_library_folder_weighting():
    prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences

    if prefs.weighting_set_use_custom_dir:
        return bpy.path.abspath(prefs.weighting_set_custom_dir)

    return var.USER_ASSET_WEIGHTING_DIR


def asset_import(filepath, ob_name=False, me_name=False):

    with bpy.data.libraries.load(filepath) as (data_from, data_to):

        if ob_name:
            data_to.objects = [ob_name]

        if me_name:
            data_to.meshes = [me_name]

    return data_to


def asset_import_batch(filepath):

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.objects = data_from.objects
        data_to.collections = data_from.collections

    return data_to


def asset_export(data_blocks, filepath):
    folder = os.path.dirname(filepath)

    if not os.path.exists(folder):
        os.makedirs(folder)

    bpy.data.libraries.write(filepath, data_blocks, compress=True)


def render_preview(width, height, filepath, compression=100, gamma=None):
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


def show_window(width, height, area_type=None, space_data=None):
    version_281 = bpy.app.version >= (2, 81, 12)
    render = bpy.context.scene.render

    render_config = {
        "resolution_x": width,
        "resolution_y": height,
        "resolution_percentage": 100,
    }

    if version_281:
        prefs = bpy.context.preferences
        _is_dirty = prefs.is_dirty
        display_type = "WINDOW"
    else:
        render_config["display_mode"] = "WINDOW"

    # Apply settings
    # ---------------------------

    for k, v in render_config.items():
        x = getattr(render, k)
        setattr(render, k, v)
        render_config[k] = x

    if version_281:
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

    if version_281:
        prefs.view.render_display_type = display_type
        prefs.is_dirty = _is_dirty


def weighting_set_export(materials, filepath):
    import json

    with open(filepath, "w", encoding="utf-8") as file:
        data = []
        mat_fmt = {
            "name": "",
            "composition": "",
            "density": 0.0,
        }

        for mat in materials.values():
            mat_dict = {k: v for k, v in mat.items() if k in mat_fmt.keys()}

            mat_exp = mat_fmt.copy()
            mat_exp.update(mat_dict)
            mat_exp["density"] = round(mat_exp["density"], 2)

            data.append(mat_exp)

        json.dump(data, file, indent=4, ensure_ascii=False)


def weighting_set_import(materials, filename, filepath):
    import json

    if filename.startswith("JCASSET"):
        for name, dens, comp in var.DEFAULT_WEIGHTING_SETS[filename]:
            item = materials.add()
            item.name = _(name)
            item.composition = comp
            item.density = dens
    else:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

            for mat in data:
                item = materials.add()
                if mat["name"]:
                    item.name = mat["name"]
                if mat["composition"]:
                    item.composition = mat["composition"]
                item.density = mat["density"]


# Object
# ------------------------------------


def bm_to_scene(bm, name="New object", color=None):
    space_data = bpy.context.space_data
    use_local_view = bool(space_data.local_view)

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
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_basis.inverted()

        add_material(ob, name=name, color=color)


def ob_copy_and_parent(ob, parents):
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


def ob_copy_to_faces(ob):
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


def apply_scale(ob):
    mat = Matrix.Diagonal(ob.scale).to_4x4()
    ob.data.transform(mat)
    ob.scale = (1.0, 1.0, 1.0)


def mod_curve_off(ob, reverse=False):
    """return -> bound box, curve object"""

    mods = reversed(ob.modifiers) if reverse else ob.modifiers

    for mod in mods:
        if mod.type == "CURVE" and mod.object:
            if mod.show_viewport:
                mod.show_viewport = False
                bpy.context.view_layer.update()
                mod.show_viewport = True

            return ob.bound_box, mod.object

    return ob.bound_box, None


def calc_bbox(obs):
    bbox = []

    for ob in obs:
        bbox += [ob.matrix_world @ Vector(x) for x in ob.bound_box]

    x_min = min(x[0] for x in bbox)
    x_max = max(x[0] for x in bbox)
    y_min = min(x[1] for x in bbox)
    y_max = max(x[1] for x in bbox)
    z_min = min(x[2] for x in bbox)
    z_max = max(x[2] for x in bbox)

    x_loc = (x_max + x_min) / 2
    y_loc = (y_max + y_min) / 2
    z_loc = (z_max + z_min) / 2

    x_dim = x_max - x_min
    y_dim = y_max - y_min
    z_dim = z_max - z_min

    return (
        (x_loc, y_loc, z_loc),  # location
        (x_dim, y_dim, z_dim),  # dimensions
        (x_min, y_min, z_min),  # bbox min
        (x_max, y_max, z_max),  # bbox max
    )
