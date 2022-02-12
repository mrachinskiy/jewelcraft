# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty
from bpy.app.translations import pgettext_iface as _

from .. import var


class VIEW3D_OT_gem_map(Operator):
    bl_label = "Gem Map"
    bl_description = "Compose gem table and map it to gems in the scene"
    bl_idname = "view3d.jewelcraft_gem_map"

    use_select: BoolProperty()
    use_background: BoolProperty()
    lang: EnumProperty(
        name="Report Language",
        description="Report language",
        items=(
            ("AUTO", "Auto (Auto)", "Use user preferences language setting"),
            ("ar_EG", "Arabic (ﺔﻴﺑﺮﻌﻟﺍ)", ""),
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
    first_run: BoolProperty(default=True, options={"HIDDEN"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "lang")
        layout.prop(self, "use_save")

    def modal(self, context, event):
        self.region.tag_redraw()

        if self.is_rendering:
            from . import onrender
            onrender.render_map(self)
            self.is_rendering = False

        elif self.use_navigate:
            self.use_navigate = False
            self.view_state = self.region_3d.perspective_matrix.copy()
            self.offscreen_refresh()

        elif event.type in {"ESC", "RET", "SPACE", "NUMPAD_ENTER"}:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, "WINDOW")
            self.offscreen.free()
            context.workspace.status_text_set(None)
            return {"FINISHED"}

        elif event.type == "S" and event.value == "PRESS":
            self.use_select = not self.use_select
            self.offscreen_refresh()
            return {"RUNNING_MODAL"}

        elif event.type == "B" and event.value == "PRESS":
            self.use_background = not self.use_background
            return {"RUNNING_MODAL"}

        elif event.type == "F12" and event.value == "PRESS":
            self.is_rendering = True
            return {"RUNNING_MODAL"}

        elif self.is_mouse_inbound(event) and (self.is_navigate(event) or self.is_select(event)):
            self.use_navigate = True

        elif self.is_time_elapsed() and self.view_state != self.region_3d.perspective_matrix:
            self.view_state = self.region_3d.perspective_matrix.copy()
            self.offscreen_refresh()

        return {"PASS_THROUGH"}

    def execute(self, context):
        import time
        from ..lib import view3d_lib
        from ..op_design_report import report_get
        from . import draw_handler, report_proc

        ReportData = report_get.data_collect(gem_map=True)

        if not ReportData.gems:
            self.report({"ERROR"}, "No gems in the scene")
            return {"CANCELLED"}

        self.region = context.region
        self.region_3d = context.space_data.region_3d
        self.view_state = self.region_3d.perspective_matrix.copy()
        self.render = context.scene.render
        self.offscreen = None
        self.handler = None
        self.use_navigate = False
        self.is_rendering = False
        self.time_tag = time.time()

        # 3D View
        # ----------------------------

        self.view_padding_left, self.view_padding_top = view3d_lib.padding_init()
        self.view_margin = 40

        view3d_lib.options_init(
            self,
            (
                (_("Limit by Selection"), "(S)", "use_select", view3d_lib.TYPE_BOOL),
                (_("Viewport Background"), "(B)", "use_background", view3d_lib.TYPE_BOOL),
                (_("Save to Image"), "(F12)", "is_rendering", view3d_lib.TYPE_PROC),
            ),
        )

        # Gem report
        # ----------------------------

        self.view_data, self.table_data = report_proc.data_process(ReportData, self.lang)

        # Warnings
        # ----------------------------

        self.show_warn = bool(ReportData.warnings)

        if self.show_warn:
            self.warn = [_("WARNING")] + [f"* {_(x)}" for x in ReportData.warnings]

        # Handlers
        # ----------------------------

        self.offscreen_refresh()
        self.handler = bpy.types.SpaceView3D.draw_handler_add(draw_handler.draw, (self, context), "WINDOW", "POST_PIXEL")

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set("ESC/↵/␣: Exit")

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Area type is not 3D View")
            return {"CANCELLED"}

        self.prefs = context.preferences.addons[var.ADDON_ID].preferences
        if self.first_run:
            self.first_run = False
            self.lang = self.prefs.design_report_lang

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)

    def offscreen_refresh(self) -> None:
        from . import offscreen
        offscreen.offscreen_refresh(self)

    def get_resolution(self) -> tuple[int, int]:
        if self.is_rendering:
            resolution_scale = self.render.resolution_percentage / 100

            if self.region_3d.view_perspective == "CAMERA":
                return round(self.render.resolution_x * resolution_scale), round(self.render.resolution_y * resolution_scale)
            else:
                return round(self.region.width * resolution_scale), round(self.region.height * resolution_scale)

        return self.region.width, self.region.height

    def is_time_elapsed(self) -> bool:
        import time

        if (time.time() - self.time_tag) > 1.0:
            self.time_tag = time.time()
            return True

        return False

    def is_mouse_inbound(self, event) -> bool:
        return (0 < event.mouse_region_x < self.region.width) and (0 < event.mouse_region_y < self.region.height)

    def is_navigate(self, event) -> bool:
        return event.type in {
            "MIDDLEMOUSE",
            "WHEELUPMOUSE",
            "WHEELDOWNMOUSE",
            "NUMPAD_5",
            "NUMPAD_MINUS",
            "NUMPAD_PLUS",
        } and event.value == "PRESS"

    def is_select(self, event) -> bool:
        return self.use_select and (
            (event.type == "LEFTMOUSE" and event.value == "CLICK") or event.type == "EVT_TWEAK_L"
        )
