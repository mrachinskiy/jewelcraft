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


import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix

from ... import var
from .. import unit
from ..asset import nearest_coords, girdle_coords, calc_gap
from .view3d_overlay import restore_gl


_handler = None
_handler_font = None
_font_loc = []
shader_3d = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
shader_2d = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


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


def handler_toggle(self, context):
    if context.area.type == "VIEW_3D":
        if self.show_spacing:
            handler_add(self, context)
        else:
            handler_del()


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
    is_df = context.mode == "EDIT_MESH" and context.edit_object.is_instancer
    diplay_thold = default_spacing + 0.5
    depsgraph = context.evaluated_depsgraph_get()

    if is_df:
        df = context.edit_object
        for ob1 in df.children:
            if "gem" in ob1:
                is_gem = True
                break
        else:
            is_gem = False
    else:
        ob1 = context.object
        if ob1:
            is_gem = "gem" in ob1
        else:
            is_gem = False

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
                poly = polys[polys.active]

                loc1 = df.matrix_world @ poly.center
                mat_rot = poly.normal.to_track_quat("Z", "Y").to_matrix().to_4x4()

                df_eval.to_mesh_clear()
            else:
                polys = df.data.polygons
                poly = polys[polys.active]

                loc1 = df.matrix_world @ poly.center
                mat_rot = poly.normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
        else:
            loc1 = ob1.matrix_world.to_translation()
            mat_rot = ob1.matrix_world.to_quaternion().to_matrix().to_4x4()

        rad1 = max(ob1.dimensions[:2]) / 2

        mat_loc = Matrix.Translation(loc1)
        mat1 = mat_loc @ mat_rot
        mat1.freeze()

    shader_3d.bind()
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    if not props.overlay_show_in_front:
        bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glDepthMask(bgl.GL_FALSE)

    for dup in depsgraph.object_instances:

        if dup.is_instance:
            ob2 = dup.instance_object.original
        else:
            ob2 = dup.object.original

        if "gem" not in ob2:
            continue

        rad2 = max(ob2.dimensions[:2]) / 2
        loc2 = dup.matrix_world.translation
        spacing_thold = False

        if is_gem:
            dis_obs = (loc1 - loc2).length
            dis_gap = from_scene_scale(dis_obs - (rad1 + rad2))
            dis_thold = dis_gap < diplay_thold

            if not (show_all or dis_thold):
                continue

            if is_df:
                if df_pass:
                    is_act = False
                else:
                    df_pass = is_act = dup.matrix_world.translation == loc1
            else:
                if dup.is_instance:
                    is_act = False
                else:
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

            bgl.glLineWidth(_linewidth)
            shader_3d.uniform_float("color", _color)

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
                    shader_3d.uniform_float("color", (1.0, 0.0, 0.0, 1.0))
                elif dis_gap < _spacing:
                    shader_3d.uniform_float("color", (1.0, 0.9, 0.0, 1.0))

                _font_loc.append((dis_gap, mid, from_scene_scale(max(ob1_spacing, _spacing))))

                batch = batch_for_shader(shader_3d, "LINES", {"pos": (co1, co2)})
                batch.draw(shader_3d)

        if show_all or spacing_thold:
            radius = rad2 + _spacing
            coords = girdle_coords(radius, mat2)
            batch = batch_for_shader(shader_3d, "LINE_LOOP", {"pos": coords})
            batch.draw(shader_3d)

    restore_gl()


def _draw_font(self, context):
    global _font_loc

    if not _font_loc:
        return

    region = context.region
    region_3d = context.space_data.region_3d
    prefs = context.preferences.addons[var.ADDON_ID].preferences
    font_size = prefs.view_font_size_distance
    fontid = 0
    blf.size(fontid, font_size, 72)
    blf.color(fontid, 1.0, 1.0, 1.0, 1.0)

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

        shader_2d.bind()
        shader_2d.uniform_float("color", color)
        batch_font = batch_for_shader(shader_2d, "TRI_FAN", {"pos": verts})
        batch_font.draw(shader_2d)

        blf.position(fontid, loc_x, loc_y, 0.0)
        blf.draw(fontid, dis_str)

    _font_loc.clear()

    # Restore OpenGL defaults
    # ----------------------------

    bgl.glDisable(bgl.GL_BLEND)
