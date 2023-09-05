# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from collections.abc import Callable

import blf
import bpy
import gpu
import numpy as np
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from mathutils import Color, Matrix

from ... import var
from .. import gemlib, unit
from ..asset import gem_transform, iter_gems

_handler = None
_handler_font = None
_font_loc = []


def handler_add(self, context, is_overlay: bool = True, use_select: bool = False):
    global _handler
    global _handler_font

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(_draw, (self, context, is_overlay, use_select), "WINDOW", "POST_VIEW")
        _handler_font = bpy.types.SpaceView3D.draw_handler_add(_draw_font, (self, context), "WINDOW", "POST_PIXEL")


def handler_del():
    global _handler
    global _handler_font

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(_handler_font, "WINDOW")
        _handler = None
        _handler_font = None


def handler_toggle(self, context):
    if context.area.type == "VIEW_3D":
        if self.show_gem_map:
            handler_add(self, context)
        else:
            handler_del()


def _to_int(x: float) -> int | float:
    if x.is_integer():
        return int(x)
    return x


def _draw(self, context, is_overlay: bool = True, use_select: bool = False):
    global _font_loc

    depsgraph = context.evaluated_depsgraph_get()
    Scale = unit.Scale()
    from_scene_scale = Scale.from_scene
    from_scene_vec = Scale.from_scene_vec
    mat_sca = Matrix.Diagonal((1.003, 1.003, 1.003)).to_4x4()
    color_var = Color((0.85, 0.35, 0.35))
    gems = set()
    gem_map = {}

    if is_overlay:
        props = context.scene.jewelcraft
        show_all = props.overlay_gem_map_show_all
        opacity = props.overlay_gem_map_opacity
        in_front = props.overlay_gem_map_show_in_front
    else:
        show_all = not use_select
        opacity = 1.0
        in_front = True

    ob = context.object

    if (is_gem := ob.select_get() and "gem" in ob):
        loc1 = ob.matrix_world.translation
        rad1 = max(ob.dimensions.xy) / 2

    # Shader
    # -----------------------------------

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_mask_set(True)
    if not in_front:
        gpu.state.depth_test_set("LESS_EQUAL")
    gpu.state.face_culling_set("BACK")

    shader = gpu.shader.from_builtin("UNIFORM_COLOR")

    # Collect dictionary
    # -----------------------------------

    for dup, ob, _ in iter_gems(depsgraph):
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in from_scene_vec(ob.dimensions))
        gems.add((stone, cut, size))

    # Sort and assign colors
    # -----------------------------------

    for gem in sorted(gems, key=lambda x: (x[1], -x[2][1], -x[2][0], x[0])):

        # Color
        # ---------------------------

        color = (*color_var, opacity)
        color_var.h += 0.15

        if color_var.h == 0.0:
            color_var.s += 0.1
            color_var.v -= 0.15

        # Size
        # ---------------------------

        w, l = tuple(_to_int(x) for x in gem[2][:2])

        try:
            trait = gemlib.CUTS[gem[1]].trait
        except KeyError:
            trait = None

        if trait is gemlib.TRAIT_XY_SYMMETRY:
            size = str(l)
        elif trait is gemlib.TRAIT_X_SIZE:
            size = f"{w}×{l}"
        else:
            size = f"{l}×{w}"

        gem_map[gem] = size, color

    # Display
    # -----------------------------------

    for dup, ob, _ in iter_gems(depsgraph):
        loc2, rad2, _ = gem_transform(dup)

        if not show_all:
            show = ob.select_get()

            if is_overlay and not show and is_gem:
                show = from_scene_scale((loc1 - loc2).length - (rad1 + rad2)) < 0.7

            if not show:
                continue

        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in from_scene_vec(ob.dimensions))
        size, color = gem_map[(stone, cut, size)]

        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(dup.matrix_world @ mat_sca)
        me.calc_loop_triangles()

        points = np.empty((len(me.vertices), 3), np.float32)
        indices = np.empty((len(me.loop_triangles), 3), np.int32)

        me.vertices.foreach_get("co", np.reshape(points, len(me.vertices) * 3))
        me.loop_triangles.foreach_get("vertices", np.reshape(indices, len(me.loop_triangles) * 3))

        ob_eval.to_mesh_clear()

        shader.uniform_float("color", color)
        batch = batch_for_shader(shader, "TRIS", {"pos": points}, indices=indices)
        batch.draw(shader)

        _font_loc.append((size, loc2.to_tuple()))

    gpu.state.blend_set("NONE")
    gpu.state.depth_test_set("NONE")
    gpu.state.depth_mask_set(False)
    gpu.state.face_culling_set("NONE")


def _draw_font(self, context, to_2d: Callable = location_3d_to_region_2d):
    global _font_loc

    if not _font_loc:
        return

    region = context.region
    region_3d = context.space_data.region_3d
    prefs = context.preferences.addons[var.ADDON_ID].preferences
    fontid = 0
    blf.size(fontid, prefs.gem_map_fontsize_gem_size)
    blf.color(fontid, 0.0, 0.0, 0.0, 1.0)

    for text, loc in _font_loc:
        dim_x, dim_y = blf.dimensions(fontid, text)
        pos_x, pos_y = to_2d(region, region_3d, loc)
        blf.position(fontid, pos_x - dim_x // 2, pos_y - dim_y // 2, 0.0)
        blf.draw(fontid, text)

    _font_loc.clear()
