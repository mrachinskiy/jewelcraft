# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2021  Mikhail Rachinskiy
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


from typing import Tuple
from math import tau, sin, cos
from functools import lru_cache

import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from ... import var
from .. import unit
from ..asset import nearest_coords, calc_gap
from .view3d_overlay import restore_gl


_handler = None
_handler_font = None
_font_loc = []
_CC = None


def handler_add(self, context):
    global _handler
    global _handler_font
    global _CC

    if _handler is None:
        _CC = CacheControl()
        _handler = bpy.types.SpaceView3D.draw_handler_add(_draw, (self, context), "WINDOW", "POST_VIEW")
        _handler_font = bpy.types.SpaceView3D.draw_handler_add(_draw_font, (self, context), "WINDOW", "POST_PIXEL")


def handler_del():
    global _handler
    global _handler_font
    global _CC

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(_handler_font, "WINDOW")
        _handler = None
        _handler_font = None
        _CC = None

        try:
            _circle_cos.cache_clear()
        except AttributeError:
            pass


def handler_toggle(self, context):
    if context.area.type == "VIEW_3D":
        if self.show_spacing:
            handler_add(self, context)
        else:
            handler_del()


@lru_cache(maxsize=64)
def _circle_cos(radius: float, mat: Matrix) -> Tuple[Vector, ...]:
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


class CacheControl:
    __slots__ = "current_threshold", "set"
    thresholds = (128, 256, 512)

    def __init__(self) -> None:
        self.current_threshold = 64
        self.set = self._set

    def _set(self, num: int) -> None:
        global _circle_cos

        if num > self.current_threshold:

            for thold in self.thresholds:
                if num <= thold:
                    self.current_threshold = thold

                    try:
                        _circle_cos.cache_clear()
                        _circle_cos = lru_cache(maxsize=self.current_threshold)(_circle_cos.__wrapped__)
                    except AttributeError:
                        _circle_cos = lru_cache(maxsize=self.current_threshold)(_circle_cos)

                    break
            else:
                try:
                    _circle_cos.cache_clear()
                    _circle_cos = _circle_cos.__wrapped__
                except AttributeError:
                    pass

                self.set = self._blank

    @staticmethod
    def _blank(x):
        pass


def _draw(self, context):
    if not context.space_data.overlay.show_overlays:
        return

    global _font_loc

    prefs = context.preferences.addons[var.ADDON_ID].preferences
    props = context.scene.jewelcraft
    show_all = props.overlay_show_all
    use_ovrd = props.overlay_use_overrides
    default_spacing = props.overlay_spacing
    default_color = prefs.overlay_color
    default_linewidth = prefs.overlay_linewidth
    diplay_thold = default_spacing + 0.5
    depsgraph = context.evaluated_depsgraph_get()
    gems_count = 0
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

    if is_gem:
        if use_ovrd and "gem_overlay" in ob1:
            ob1_spacing = ob1["gem_overlay"].get("spacing", default_spacing)
        else:
            ob1_spacing = default_spacing

        from_scene_scale = unit.Scale(context).from_scene

        if is_df:
            df_pass = False
            df.update_from_editmode()

            if df.modifiers and df.is_deform_modified(context.scene, "PREVIEW"):
                df_eval = df.evaluated_get(depsgraph)
                polys = df_eval.to_mesh().polygons
            else:
                df_eval = df
                polys = df.data.polygons

            poly = polys[df.data.polygons.active]
            loc1 = df.matrix_world @ poly.center
            mat_rot = poly.normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
            df_eval.to_mesh_clear()
        else:
            loc1 = ob1.matrix_world.to_translation()
            mat_rot = ob1.matrix_world.to_quaternion().to_matrix().to_4x4()

        rad1 = max(ob1.dimensions.xy) / 2
        mat_loc = Matrix.Translation(loc1)
        mat1 = mat_loc @ mat_rot
        mat1.freeze()

    bgl.glEnable(bgl.GL_BLEND)

    if var.USE_POLYLINE:
        shader = gpu.shader.from_builtin("3D_POLYLINE_UNIFORM_COLOR")
    else:
        shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glDepthMask(bgl.GL_FALSE)

    if not props.overlay_show_in_front:
        bgl.glEnable(bgl.GL_DEPTH_TEST)

    shader.bind()

    for dup in depsgraph.object_instances:

        if dup.is_instance:
            ob2 = dup.instance_object.original
        else:
            ob2 = dup.object.original

        if "gem" not in ob2:
            continue

        gems_count += 1

        rad2 = max(ob2.dimensions.xy) / 2
        loc2 = dup.matrix_world.translation
        spacing_thold = False

        if is_gem:
            dis_obs = (loc1 - loc2).length
            dis_gap = from_scene_scale(dis_obs - (rad1 + rad2))
            dis_thold = dis_gap < diplay_thold

            if not (show_all or dis_thold):
                continue

            is_act = False

            if is_df:
                if not df_pass:
                    df_pass = is_act = dup.matrix_world.translation == loc1
            else:
                if not dup.is_instance:
                    is_act = ob2 is ob1

            use_diplay_dis = not is_act and dis_thold
        else:
            use_diplay_dis = False

        if show_all or use_diplay_dis:
            if use_ovrd and "gem_overlay" in ob2:
                _color = ob2["gem_overlay"].get("color", default_color)
                _linewidth = ob2["gem_overlay"].get("linewidth", default_linewidth)
                _spacing = ob2["gem_overlay"].get("spacing", default_spacing)
            else:
                _color = default_color
                _linewidth = default_linewidth
                _spacing = default_spacing

            shader.uniform_float("color", _color)

            if var.USE_POLYLINE:
                shader.uniform_float("lineWidth", _linewidth)
            else:
                bgl.glLineWidth(_linewidth)

            if dup.is_instance:
                mat2 = dup.matrix_world.copy()
            else:
                mat_loc = Matrix.Translation(loc2)
                mat_rot = dup.matrix_world.to_quaternion().to_matrix().to_4x4()
                mat2 = mat_loc @ mat_rot

            mat2.freeze()

        if use_diplay_dis:
            if dis_obs:
                co1, co2 = nearest_coords(rad1, rad2, mat1, mat2)
                dis_gap = from_scene_scale(calc_gap(co1, co2, loc1, dis_obs, rad1))
                dis_thold = dis_gap < diplay_thold
                spacing_thold = dis_gap < (_spacing + 0.3)

                if not (show_all or dis_thold):
                    continue

                mid = co1.lerp(co2, 0.5)
            else:
                co1 = co2 = mid = loc2.copy()

            if dis_thold:
                if dis_gap < 0.1:
                    shader.uniform_float("color", (1.0, 0.0, 0.0, 1.0))
                elif dis_gap < _spacing:
                    shader.uniform_float("color", (1.0, 0.9, 0.0, 1.0))

                _font_loc.append((dis_gap, mid, from_scene_scale(max(ob1_spacing, _spacing))))

                batch = batch_for_shader(shader, "LINES", {"pos": (co1, co2)})
                batch.draw(shader)

        if show_all or spacing_thold:
            batch = batch_for_shader(shader, "LINE_LOOP", {"pos": _circle_cos(rad2 + _spacing, mat2)})
            batch.draw(shader)

    _CC.set(gems_count)
    restore_gl()


def _draw_font(self, context):
    global _font_loc

    if not _font_loc:
        return

    region = context.region
    region_3d = context.space_data.region_3d
    prefs = context.preferences.addons[var.ADDON_ID].preferences
    font_size = prefs.overlay_fontsize_distance
    fontid = 0
    blf.size(fontid, font_size, 72)
    blf.color(fontid, 1.0, 1.0, 1.0, 1.0)
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    for dist, loc, spacing in _font_loc:
        bgl.glEnable(bgl.GL_BLEND)

        if dist < 0.1:
            color = (0.9, 0.0, 0.0, 1.0)
        elif dist < spacing:
            color = (0.9, 0.7, 0.0, 1.0)
        else:
            color = (0.0, 0.0, 0.0, 0.3)

        dis_str = f"{dist:.2f}"
        dim_x, dim_y = blf.dimensions(fontid, dis_str)
        loc_x, loc_y = location_3d_to_region_2d(region, region_3d, loc)

        verts = (
            (loc_x - 3,         loc_y - 4),
            (loc_x + 3 + dim_x, loc_y - 4),
            (loc_x + 3 + dim_x, loc_y + 4 + dim_y),
            (loc_x - 3,         loc_y + 4 + dim_y),
        )

        shader.bind()
        shader.uniform_float("color", color)
        batch_font = batch_for_shader(shader, "TRI_FAN", {"pos": verts})
        batch_font.draw(shader)

        blf.position(fontid, loc_x, loc_y, 0.0)
        blf.draw(fontid, dis_str)

    _font_loc.clear()

    # Restore OpenGL defaults
    # ----------------------------

    bgl.glDisable(bgl.GL_BLEND)
