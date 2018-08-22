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


from functools import lru_cache
from math import sin, cos, pi

import bpy
import bgl
from mathutils import Matrix, Vector

from .. import var


tau = 2 * pi

_handler = None


def handler_add(self, context):
    global _handler

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), "WINDOW", "POST_VIEW")


def handler_del():
    global _handler

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        _handler = None


def handler_toggle(self, context):

    if context.area.type == "VIEW_3D":

        if context.window_manager.jewelcraft.widget_toggle:
            handler_add(self, context)
        else:
            handler_del()

        context.area.tag_redraw()


def draw_callback_px(self, context):

    if not context.window_manager.jewelcraft.widget_toggle or context.space_data.show_only_render:
        return

    prefs = context.user_preferences.addons[var.ADDON_ID].preferences
    use_ovrd = prefs.widget_use_overrides
    default_settings = {
        "color": prefs.widget_color,
        "linewidth": prefs.widget_linewidth,
        "distance": prefs.widget_distance,
    }
    obs = context.selected_objects if prefs.widget_selection_only else context.visible_objects
    key = "jewelcraft_widget" if use_ovrd and prefs.widget_overrides_only else "gem"

    bgl.glEnable(bgl.GL_BLEND)

    if prefs.widget_x_ray:
        bgl.glDisable(bgl.GL_DEPTH_TEST)

    for ob in obs:
        if key in ob:
            settings = default_settings.copy()

            if use_ovrd and "jewelcraft_widget" in ob:
                settings.update(ob["jewelcraft_widget"])

            bgl.glLineWidth(settings["linewidth"])
            bgl.glColor4f(*settings["color"])
            radius = max(ob.dimensions[:2]) / 2 + settings["distance"]

            mat_loc = Matrix.Translation(ob.matrix_world.translation)
            mat_rot = ob.matrix_world.to_euler().to_matrix().to_4x4()
            mat = mat_loc * mat_rot

            coords = circle_coords(radius)

            bgl.glBegin(bgl.GL_LINE_LOOP)
            for co in coords:
                bgl.glVertex3f(*(mat * co))
            bgl.glEnd()

            # Duplifaces
            # ----------------------------

            if ob.parent and ob.parent.dupli_type == "FACES":

                ob.parent.dupli_list_create(context.scene)

                for dup in ob.parent.dupli_list:
                    if dup.object == ob:
                        mat = dup.matrix
                        bgl.glBegin(bgl.GL_LINE_LOOP)
                        for co in coords:
                            bgl.glVertex3f(*(mat * co))
                        bgl.glEnd()

                ob.parent.dupli_list_clear()

    # Restore OpenGL defaults
    # ----------------------------

    bgl.glLineWidth(1)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_DEPTH_TEST)


@lru_cache(maxsize=128)
def circle_coords(radius):
    coords = []
    angle = tau / 64

    for i in range(64):
        x = sin(i * angle) * radius
        y = cos(i * angle) * radius
        coords.append(Vector((x, y, 0.0)))

    return coords
