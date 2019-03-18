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


from functools import lru_cache
from math import sin, cos, tau

import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from .. import var


_handler = None
shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")


def handler_add(self, context):
    global _handler

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(draw, (self, context), "WINDOW", "POST_VIEW")


def handler_del():
    global _handler

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        _handler = None


def handler_toggle(self, context):

    if context.area.type == "VIEW_3D":

        if self.widget_toggle:
            handler_add(self, context)
        else:
            handler_del()

        context.area.tag_redraw()


def draw(self, context):

    if not context.window_manager.jewelcraft.widget_toggle or not context.space_data.overlay.show_overlays:
        return

    depsgraph = context.depsgraph
    prefs = context.preferences.addons[var.ADDON_ID].preferences
    use_ovrd = prefs.widget_use_overrides
    use_ovrd_only = use_ovrd and prefs.widget_overrides_only
    use_sel_only = prefs.widget_selection_only

    default_settings = {
        "color": prefs.widget_color,
        "linewidth": prefs.widget_linewidth,
        "distance": prefs.widget_distance,
    }

    shader.bind()
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    bgl.glDepthMask(bgl.GL_FALSE)

    if prefs.widget_show_in_front:
        bgl.glDisable(bgl.GL_DEPTH_TEST)

    for dup in depsgraph.object_instances:

        if dup.is_instance:
            ob = dup.instance_object.original
        else:
            ob = dup.object.original

        if (
            ("gem" not in ob) or
            (use_ovrd_only and "jewelcraft_widget" not in ob) or
            (use_sel_only and not ob.select_get())
        ):
            continue

        if dup.is_instance:
            mat = dup.matrix_world
        else:
            mat_loc = Matrix.Translation(ob.matrix_world.translation)
            mat_rot = ob.matrix_world.to_quaternion().to_matrix().to_4x4()
            mat = mat_loc @ mat_rot

        settings = default_settings.copy()

        if use_ovrd and "jewelcraft_widget" in ob:
            settings.update(ob["jewelcraft_widget"])

        radius = max(ob.dimensions[:2]) / 2 + settings["distance"]
        coords = [mat @ co for co in circle_coords(radius)]

        bgl.glLineWidth(settings["linewidth"])
        shader.uniform_float("color", settings["color"])
        batch = batch_for_shader(shader, "LINE_LOOP", {"pos": coords})
        batch.draw(shader)

    # Restore OpenGL defaults
    # ----------------------------

    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    bgl.glDepthMask(bgl.GL_TRUE)
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glLineWidth(1)


@lru_cache(maxsize=128)
def circle_coords(radius):
    coords = []
    angle = tau / 64

    for i in range(64):
        x = sin(i * angle) * radius
        y = cos(i * angle) * radius
        coords.append(Vector((x, y, 0.0)))

    return coords
