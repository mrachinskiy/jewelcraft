# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2023 Mikhail Rachinskiy

from functools import lru_cache
from math import cos, sin, tau

import blf
import bpy
import gpu
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Quaternion, Vector

from ... import var
from .. import unit
from ..asset import calc_gap, gem_transform, iter_gems, nearest_coords


_handler = None
_handler_font = None
_font_loc = []


def handler_add(self, context):
    global _handler
    global _handler_font

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(_draw, (self, context), "WINDOW", "POST_VIEW")
        _handler_font = bpy.types.SpaceView3D.draw_handler_add(_draw_font, (self, context), "WINDOW", "POST_PIXEL")


def handler_del():
    global _handler
    global _handler_font

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(_handler_font, "WINDOW")
        _handler = None
        _handler_font = None
        _circle_cos.cache_clear()


def handler_toggle(self, context):
    if context.area.type == "VIEW_3D":
        if self.show_spacing:
            handler_add(self, context)
        else:
            handler_del()


# Cache control
# -------------------------------------


class CacheControl:
    __slots__ = "cache_size"

    def __init__(self) -> None:
        self.cache_size = 64

    def set(self, show_all: bool, num: int) -> None:
        if not show_all:
            if self.cache_size != 64:
                self.cache_size = 64
                self.wrap(64)
            return

        if num > self.cache_size:
            self.cache_size = num + 50
            self.wrap(self.cache_size)

    @staticmethod
    def wrap(size: int) -> None:
        global _circle_cos

        _circle_cos.cache_clear()
        _circle_cos = lru_cache(maxsize=size)(_circle_cos.__wrapped__)


_CC = CacheControl()


# -------------------------------------


@lru_cache(maxsize=64)
def _circle_cos(radius: float, mat: Matrix) -> tuple[Vector, ...]:
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


def _get_df_transform(ob, context, depsgraph) -> tuple[Vector, Quaternion]:
    ob.update_from_editmode()

    if ob.modifiers and ob.is_deform_modified(context.scene, "PREVIEW"):
        ob_eval = ob.evaluated_get(depsgraph)
        polys = ob_eval.to_mesh().polygons
    else:
        ob_eval = ob
        polys = ob.data.polygons

    poly = polys[ob.data.polygons.active]
    loc = ob.matrix_world @ poly.center
    rot = poly.normal.to_track_quat("Z", "Y")
    ob_eval.to_mesh_clear()

    return loc, rot


def _draw(self, context):
    if not context.space_data.overlay.show_overlays:
        return

    props = context.scene.jewelcraft
    show_all = props.overlay_show_all
    use_ovrd = props.overlay_use_overrides
    default_spacing = props.overlay_spacing

    is_gem = False
    is_df = context.mode == "EDIT_MESH" and context.edit_object.is_instancer

    if is_df:
        df = context.edit_object
        for ob1 in df.children:
            if "gem" in ob1:
                is_gem = True
                break
    else:
        ob1 = context.object
        if ob1:
            is_gem = "gem" in ob1 and ob1.select_get()

    if not (show_all or is_gem):
        return

    global _font_loc

    prefs = context.preferences.addons[var.ADDON_ID].preferences
    default_color = prefs.overlay_color
    default_linewidth = prefs.overlay_linewidth

    diplay_thold = default_spacing + 0.5
    gems_count = 0
    depsgraph = context.evaluated_depsgraph_get()

    # Gem 1 transform
    # -----------------------------------

    if is_gem:

        if use_ovrd and "gem_overlay" in ob1:
            spacing1 = ob1["gem_overlay"].get("spacing", default_spacing)
        else:
            spacing1 = default_spacing

        from_scene_scale = unit.Scale().from_scene

        if is_df:
            df_pass = False
            loc1, _rot = _get_df_transform(df, context, depsgraph)
        else:
            loc1 = ob1.matrix_world.to_translation()
            _rot = ob1.matrix_world.to_quaternion()

        rad1 = max(ob1.dimensions.xy) / 2
        mat1 = Matrix.LocRotScale(loc1, _rot, (1.0, 1.0, 1.0))
        mat1.freeze()

    # Shader
    # -----------------------------------

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_mask_set(True)
    if not props.overlay_show_in_front:
        gpu.state.depth_test_set("LESS_EQUAL")

    shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
    shader.uniform_float("viewportSize", (context.area.width, context.area.height))

    # Main loop
    # -----------------------------------

    for dup, ob2, _ in iter_gems(depsgraph):
        gems_count += 1
        loc2, rad2, mat2 = gem_transform(dup)

        # Filter out by distance
        # -----------------------------------

        use_diplay_dis = False

        if is_gem:
            dis_obs = (loc1 - loc2).length
            proximity_dis = from_scene_scale(dis_obs - (rad1 + rad2))
            proximity_thold = proximity_dis < diplay_thold

            if not (show_all or proximity_thold):
                continue

            is_act = False

            if is_df:
                if not df_pass:
                    df_pass = is_act = dup.matrix_world.translation == loc1
            else:
                if not dup.is_instance:
                    is_act = ob2 is ob1

            use_diplay_dis = not is_act and proximity_thold

        # Gem 2 shader and spacing overrride
        # -----------------------------------

        if show_all or use_diplay_dis:

            if use_ovrd and "gem_overlay" in ob2:
                _color = ob2["gem_overlay"].get("color", default_color)
                _linewidth = ob2["gem_overlay"].get("linewidth", default_linewidth)
                spacing2 = ob2["gem_overlay"].get("spacing", default_spacing)
            else:
                _color = default_color
                _linewidth = default_linewidth
                spacing2 = default_spacing

            shader.uniform_float("color", _color)
            shader.uniform_float("lineWidth", _linewidth)

        # Show distance
        # -----------------------------------

        spacing_thold = False

        if use_diplay_dis:

            if dis_obs:
                co1, co2 = nearest_coords(rad1, rad2, mat1, mat2)
                dis_gap = from_scene_scale(calc_gap(co1, co2, loc1, dis_obs, rad1))
                gap_thold = dis_gap < diplay_thold

                if not (show_all or gap_thold):
                    continue

                spacing_thold = dis_gap < (spacing2 + 0.3)
                mid = co1.lerp(co2, 0.5)
            else:
                co1 = co2 = mid = loc2
                dis_gap = proximity_dis
                gap_thold = spacing_thold = True

            if gap_thold:

                if dis_gap < 0.1:
                    shader.uniform_float("color", (1.0, 0.0, 0.0, 1.0))
                elif dis_gap < spacing2:
                    shader.uniform_float("color", (1.0, 0.9, 0.0, 1.0))

                _font_loc.append((dis_gap, mid, from_scene_scale(max(spacing1, spacing2))))

                batch = batch_for_shader(shader, "LINES", {"pos": (co1, co2)})
                batch.draw(shader)

        # Show spacing
        # -----------------------------------

        if show_all or spacing_thold:
            batch = batch_for_shader(shader, "LINE_LOOP", {"pos": _circle_cos(rad2 + spacing2, mat2)})
            batch.draw(shader)

    _CC.set(show_all, gems_count)

    gpu.state.blend_set("NONE")
    gpu.state.depth_test_set("NONE")
    gpu.state.depth_mask_set(False)


def _draw_font(self, context):
    global _font_loc

    if not _font_loc:
        return

    region = context.region
    region_3d = context.space_data.region_3d
    prefs = context.preferences.addons[var.ADDON_ID].preferences
    font_size = prefs.overlay_fontsize_distance
    fontid = 0
    blf.size(fontid, font_size)
    blf.color(fontid, 1.0, 1.0, 1.0, 1.0)
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    indices = ((0, 1, 2), (0, 2, 3))

    for dist, loc, spacing in _font_loc:
        gpu.state.blend_set("ALPHA")

        if dist < 0.1:
            color = (0.9, 0.0, 0.0, 1.0)
        elif dist < spacing:
            color = (0.9, 0.7, 0.0, 1.0)
        else:
            color = (0.0, 0.0, 0.0, 0.3)

        dis_str = f"{dist:.2f}"
        dim_x, dim_y = blf.dimensions(fontid, dis_str)
        pos_x, pos_y = location_3d_to_region_2d(region, region_3d, loc).to_tuple(0)
        points = (
            (pos_x - 3,         pos_y - 4),
            (pos_x + 3 + dim_x, pos_y - 4),
            (pos_x + 3 + dim_x, pos_y + 4 + dim_y),
            (pos_x - 3,         pos_y + 4 + dim_y),
        )

        shader.bind()
        shader.uniform_float("color", color)
        batch_font = batch_for_shader(shader, "TRIS", {"pos": points}, indices=indices)
        batch_font.draw(shader)

        blf.position(fontid, pos_x, pos_y, 0.0)
        blf.draw(fontid, dis_str)

    _font_loc.clear()
    gpu.state.blend_set("NONE")
