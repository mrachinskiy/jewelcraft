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
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, IntProperty
from bpy.app.translations import pgettext_iface as _

from .. import var
from ..lib import view3d_lib
from ..op_design_report import report_get
from . import draw_handler, onrender
from .offscreen import Offscreen
from .onscreen_text import OnscreenText
from .report_proc import ReportProc


class VIEW3D_OT_gem_map(Offscreen, OnscreenText, ReportProc, Operator):
    bl_label = "Gem Map"
    bl_description = "Compose gem table and map it to gems in the scene"
    bl_idname = "view3d.jewelcraft_gem_map"

    use_select: BoolProperty()
    lang: EnumProperty(
        name="Report Language",
        description="Report language",
        items=(
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
            ("en_US", "English (English)", ""),
            ("es", "Spanish (Español)", ""),
            ("fr_FR", "French (Français)", ""),
            ("it_IT", "Italian (Italiano)", ""),
            ("ru_RU", "Russian (Русский)", ""),
            ("zh_CN", "Simplified Chinese (简体中文)", ""),
        ),
    )
    use_save: BoolProperty(
        name="Save To File",
        description="Save to file in project folder",
        default=True,
    )
    warn_hidden_gems: BoolProperty(
        name="Hidden Gems",
        description="Enable or disable given warning",
        default=True,
    )
    warn_gem_overlap: BoolProperty(
        name="Overlapping Gems",
        description="Enable or disable given warning",
        default=True,
    )
    width: IntProperty(
        name="Width",
        description="Number of horizontal pixels in the rendered image",
        default=1200,
        min=4,
        subtype="PIXEL",
    )
    height: IntProperty(
        name="Height",
        description="Number of vertical pixels in the rendered image",
        default=750,
        min=4,
        subtype="PIXEL",
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "use_save")
        layout.prop(self, "lang")

        col = layout.column(align=True)
        col.prop(self, "width", text="Resolution X")
        col.prop(self, "height", text="Y")

        col = layout.column(heading="Warnings")
        col.prop(self, "warn_hidden_gems")
        col.prop(self, "warn_gem_overlap")

    def modal(self, context, event):
        import time

        self.region.tag_redraw()

        inbound = (
            0 < event.mouse_region_x < self.region.width and
            0 < event.mouse_region_y < self.region.height
        )

        if self.is_rendering:
            onrender.render_map(self, context)
            self.is_rendering = False

        elif self.use_navigate:
            self.use_navigate = False
            self.view_mat = self.region_3d.perspective_matrix.copy()
            self.offscreen_refresh(context)

        elif event.type in {"ESC", "RET", "SPACE"}:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, "WINDOW")
            self.offscreen.free()
            context.workspace.status_text_set(None)
            return {"FINISHED"}

        elif event.type == "S" and event.value == "PRESS":
            self.use_select = not self.use_select
            self.offscreen_refresh(context)
            return {"RUNNING_MODAL"}

        elif event.type == "F12" and event.value == "PRESS":
            self.is_rendering = True
            return {"RUNNING_MODAL"}

        elif inbound and ((event.type in {
            "MIDDLEMOUSE",
            "WHEELUPMOUSE",
            "WHEELDOWNMOUSE",
            "NUMPAD_5",
            "NUMPAD_MINUS",
            "NUMPAD_PLUS",
        } and event.value == "PRESS") or event.type == "EVT_TWEAK_L"):
            self.use_navigate = True

        elif time.time() - self.time_tag > 1.0:
            self.time_tag = time.time()

            if self.view_mat != self.region_3d.perspective_matrix:
                self.view_mat = self.region_3d.perspective_matrix.copy()
                self.offscreen_refresh(context)

        return {"PASS_THROUGH"}

    def execute(self, context):
        ReportData = report_get.data_collect(self, context, gem_map=True)

        if not ReportData.gems:
            self.report({"ERROR"}, "No gems in the scene")
            return {"CANCELLED"}

        import time

        self.region = context.region
        self.region_3d = context.space_data.region_3d
        self.view_mat = self.region_3d.perspective_matrix.copy()
        self.offscreen = None
        self.handler = None
        self.use_navigate = False
        self.is_rendering = False
        self.time_tag = time.time()

        # 3D View
        # ----------------------------

        self.view_padding_left, self.view_padding_top = view3d_lib.padding_init(context)
        self.view_margin = 40

        view3d_lib.options_init(
            self,
            (
                (_("Limit By Selection"), "(S)", "use_select", view3d_lib.TYPE_BOOL),
                (_("Save To Image"), "(F12)", "is_rendering", view3d_lib.TYPE_PROC),
            ),
        )

        # Gem report
        # ----------------------------

        self.data_process(ReportData)

        # Warnings
        # ----------------------------

        self.show_warn = bool(ReportData.warnings)

        if self.show_warn:
            self.warn = [_("WARNING")] + [f"* {_(x)}" for x in ReportData.warnings]

        # Handlers
        # ----------------------------

        self.offscreen_refresh(context)
        self.handler = bpy.types.SpaceView3D.draw_handler_add(draw_handler.draw, (self, context), "WINDOW", "POST_PIXEL")

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set("ESC/↵/␣: Exit")

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Area type is not 3D View")
            return {"CANCELLED"}

        self.prefs = context.preferences.addons[var.ADDON_ID].preferences
        self.lang = self.prefs.design_report_lang
        self.warn_hidden_gems = self.prefs.warn_hidden_gems
        self.warn_gem_overlap = self.prefs.warn_gem_overlap
        self.width = self.prefs.gem_map_width
        self.height = self.prefs.gem_map_height

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)

    @staticmethod
    def rect_coords(x, y, dim_x, dim_y):
        return (
            (x,         y),
            (x + dim_x, y),
            (x + dim_x, y + dim_y),
            (x,         y + dim_y),
        )

    @staticmethod
    def gamma_correction(color):
        return [x ** 2.2 for x in color]  # NOTE T74139
