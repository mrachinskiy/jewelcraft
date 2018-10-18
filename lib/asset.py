# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
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
import random

import bpy
from mathutils import Matrix, Vector

from . import mesh
from .. import var


# Gem
# ------------------------------------


def get_gem(self, context):
    ob = context.active_object

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


# Material
# ------------------------------------


def color_rnd():
    seq = (0.0, 0.5, 1.0)
    return random.choice(seq), random.choice(seq), random.choice(seq)


def add_material(ob, mat_name="New Material", color=(0.8, 0.8, 0.8), is_gem=False):
    mat = bpy.data.materials.get(mat_name)

    if not mat:
        mat = bpy.data.materials.new(mat_name)
        mat.diffuse_color = color

        if not is_gem:
            mat.specular_color = (0.0, 0.0, 0.0)

        if bpy.context.scene.render.engine == "CYCLES":
            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            for node in nodes:
                nodes.remove(node)

            if is_gem:
                node = nodes.new("ShaderNodeBsdfGlass")
            else:
                node = nodes.new("ShaderNodeBsdfGlossy")

            node.inputs["Color"].default_value = color + (1.0,)
            node.location = (0.0, 200.0)

            node_out = nodes.new("ShaderNodeOutputMaterial")
            node_out.location = (200.0, 200.0)

            mat.node_tree.links.new(node.outputs["BSDF"], node_out.inputs["Surface"])

    if ob.material_slots:
        ob.material_slots[0].material = mat
    else:
        ob.data.materials.append(mat)


# Asset
# ------------------------------------


def user_asset_library_folder_object():
    prefs = bpy.context.user_preferences.addons[var.ADDON_ID].preferences

    if prefs.use_custom_asset_dir:
        return bpy.path.abspath(prefs.custom_asset_dir)

    return var.USER_ASSET_DIR_OBJECT


def user_asset_library_folder_weighting():
    prefs = bpy.context.user_preferences.addons[var.ADDON_ID].preferences

    if prefs.weighting_set_use_custom_dir:
        return bpy.path.abspath(prefs.weighting_set_custom_dir)

    return var.USER_ASSET_DIR_WEIGHTING


def asset_import(filepath="", ob_name=False, me_name=False):

    with bpy.data.libraries.load(filepath) as (data_from, data_to):

        if ob_name:
            data_to.objects = [ob_name]

        if me_name:
            data_to.meshes = [me_name]

    return data_to


def asset_import_batch(filepath=""):

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.objects = data_from.objects

    return data_to


def asset_export(folder="", filename=""):
    filepath = os.path.join(folder, filename)
    data_blocks = set(bpy.context.selected_objects)

    if not os.path.exists(folder):
        os.makedirs(folder)

    bpy.data.libraries.write(filepath, data_blocks, compress=True)


def render_preview(filepath="//"):
    render = bpy.context.scene.render
    image = render.image_settings

    # Apply settings
    # ---------------------------

    settings_render = {
        "filepath": filepath,
        "resolution_x": 256,
        "resolution_y": 256,
        "resolution_percentage": 100,
        "alpha_mode": "TRANSPARENT",
    }

    settings_image = {
        "file_format": "PNG",
        "color_mode": "RGBA",
        "compression": 100,
    }

    for k, v in settings_render.items():
        x = getattr(render, k)
        setattr(render, k, v)
        settings_render[k] = x

    for k, v in settings_image.items():
        x = getattr(image, k)
        setattr(image, k, v)
        settings_image[k] = x

    # Render and save
    # ---------------------------

    bpy.ops.render.opengl(write_still=True)

    # Revert settings
    # ---------------------------

    for k, v in settings_render.items():
        setattr(render, k, v)

    for k, v in settings_image.items():
        setattr(image, k, v)


# Object
# ------------------------------------


def bm_to_scene(bm, name="New object", color=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()

    scene = bpy.context.scene

    for parent in bpy.context.selected_objects:

        ob = bpy.data.objects.new(name, me)
        scene.objects.link(ob)

        ob.layers = parent.layers
        ob.show_all_edges = True
        ob.location = parent.location
        ob.rotation_euler = parent.rotation_euler

        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_basis.inverted()

        add_material(ob, mat_name=name, color=color)


def apply_scale(ob):
    mat = Matrix()
    mat[0][0] = ob.scale[0]
    mat[1][1] = ob.scale[1]
    mat[2][2] = ob.scale[2]

    ob.data.transform(mat)

    ob.scale = (1.0, 1.0, 1.0)


def ob_copy_to_pos(ob):
    scene = bpy.context.scene
    mats = mesh.face_pos()

    if mats:
        ob.matrix_world = mats.pop()

        for mat in mats:
            ob_copy = ob.copy()
            scene.objects.link(ob_copy)
            ob_copy.layers = ob.layers
            ob_copy.matrix_world = mat


def mod_curve_off(ob, reverse=False):
    """return -> bound box, curve object"""

    mods = reversed(ob.modifiers) if reverse else ob.modifiers

    for mod in mods:
        if mod.type == "CURVE" and mod.object:
            if mod.show_viewport:
                mod.show_viewport = False
                bpy.context.scene.update()
                mod.show_viewport = True

            return ob.bound_box, mod.object

    return ob.bound_box, None


def calc_bbox(obs):
    bbox = []

    for ob in obs:
        bbox += [ob.matrix_world * Vector(x) for x in ob.bound_box]

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
