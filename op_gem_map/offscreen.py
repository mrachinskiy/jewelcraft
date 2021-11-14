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


import operator

import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_origin_3d
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from ..lib import unit


class _LocAdapt:
    __slots__ = "region", "region_3d", "scale", "offset"

    def __init__(self, op) -> None:
        self.region = op.region
        self.region_3d = op.region_3d
        self.scale = Vector((1.0, 1.0))
        self.offset = Vector((0.0, 0.0))

        if op.is_rendering:
            if self.region_3d.view_perspective == "CAMERA":
                width, height = op.get_resolution()
                frame_width, frame_height, frame_offset = self._get_frame()

                self.scale.xy = width / frame_width, height / frame_height
                self.offset = frame_offset.xy
            else:
                self.scale.xy = op.render.resolution_percentage / 100

    def to_2d(self, loc: Vector) -> Vector:
        v = location_3d_to_region_2d(self.region, self.region_3d, loc)
        return (v - self.offset) * self.scale

    def _get_frame(self) -> tuple[float, float, Vector]:
        scene = bpy.context.scene
        cam = scene.camera
        frame = [
            location_3d_to_region_2d(self.region, self.region_3d, cam.matrix_world @ p)
            for p in cam.data.view_frame(scene=scene)
        ]
        return frame[1].x - frame[2].x, frame[0].y - frame[1].y, frame[2]


def linear_to_srgb(color) -> list:
    return [x ** 2.2 for x in color]  # NOTE T74139


def offscreen_refresh(self):
    if self.offscreen is not None:
        self.offscreen.free()

    width, height = self.get_resolution()
    self.offscreen = gpu.types.GPUOffScreen(width, height)

    mat_offscreen = Matrix()
    mat_offscreen[0][0] = 2 / width
    mat_offscreen[0][3] = -1
    mat_offscreen[1][1] = 2 / height
    mat_offscreen[1][3] = -1

    with self.offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 0.0))

        with gpu.matrix.push_pop():
            gpu.matrix.load_matrix(mat_offscreen)
            gpu.matrix.load_projection_matrix(Matrix())

            draw_gems(self, gamma_corr=True)


def draw_gems(self, gamma_corr=False):
    _c = linear_to_srgb if gamma_corr else lambda x: x

    if self.region_3d.is_perspective:
        view_loc = self.region_3d.view_matrix.inverted().translation
    else:
        _center_xy = (self.region.width / 2, self.region.height / 2)
        view_loc = region_2d_to_origin_3d(self.region, self.region_3d, _center_xy)

    from_scene_scale_vec = unit.Scale().from_scene_vec
    depsgraph = bpy.context.evaluated_depsgraph_get()
    gems = []
    _app = gems.append

    for dup in depsgraph.object_instances:

        if dup.is_instance:
            ob = dup.instance_object.original
        else:
            ob = dup.object.original

        if "gem" not in ob:
            continue

        ob_stone = ob["gem"]["stone"]
        ob_cut = ob["gem"]["cut"]
        ob_size = tuple(round(x, 2) for x in from_scene_scale_vec(ob.dimensions))

        size_fmt, color = self.view_data.get((ob_stone, ob_cut, ob_size), (None, None))

        if color is None:
            continue

        mat = dup.matrix_world.copy()
        dist_from_view = (mat.translation - view_loc).length
        _app((dist_from_view, ob, mat, size_fmt, color))

    fontid = 0
    blf.size(fontid, self.prefs.gem_map_fontsize_gem_size, 72)
    blf.color(fontid, 0.0, 0.0, 0.0, 1.0)
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    LocAdapt = _LocAdapt(self)
    _loc2d = LocAdapt.to_2d

    gems.sort(key=operator.itemgetter(0), reverse=True)

    for _, ob, mat, size_fmt, color in gems:

        # Shape
        # -----------------------------

        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(mat)
        me.calc_loop_triangles()

        points = [_loc2d(v.co) for v in me.vertices]
        indices = (tri.vertices for tri in me.loop_triangles)

        shader.bind()
        shader.uniform_float("color", _c(color))
        batch = batch_for_shader(shader, "TRIS", {"pos": points}, indices=indices)
        batch.draw(shader)

        ob_eval.to_mesh_clear()

        # Size
        # -----------------------------

        pos = _loc2d(mat.translation) - Vector(blf.dimensions(fontid, size_fmt)) / 2
        blf.position(fontid, round(pos.x), round(pos.y), 0.0)
        blf.draw(fontid, size_fmt)
