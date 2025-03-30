# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.app.translations import pgettext_iface as _
from bpy.props import BoolProperty
from bpy.types import Operator

from .. import preferences, var


class VIEW3D_OT_gem_map(preferences.ReportLangEnum, Operator):
    bl_label = "Gem Map"
    bl_description = "Compose gem table and map it to gems in the scene"
    bl_idname = "view3d.jewelcraft_gem_map"

    use_select: BoolProperty()
    use_mat_color: BoolProperty()
    use_background: BoolProperty()
    use_save: BoolProperty(
        name="Save to File",
        description="Save to file in project folder",
        default=True,
    )
    first_run: BoolProperty(default=True, options={"HIDDEN"})

    is_running = False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "report_lang")
        layout.prop(self, "use_save")

    def modal(self, context, event):
        if self.is_rendering:
            from . import onrender
            onrender.render_map(self)
            self.is_rendering = False

        elif self.is_mouse_inbound(event):
            from ..lib import overlays

            if event.type in {"ESC", "RET", "SPACE", "NUMPAD_ENTER"}:
                from . import onscreen
                self.__class__.is_running = False
                context.workspace.status_text_set(None)
                overlays.gem_map.handler_del()
                onscreen.handler_del()
                self.region.tag_redraw()
                return {"FINISHED"}

            elif event.type == "S" and event.value == "PRESS":
                self.use_select = not self.use_select
                overlays.gem_map.handler_del()
                overlays.gem_map.handler_add(self, context, is_overlay=False, use_select=self.use_select, use_mat_color=self.use_mat_color)
                self.region.tag_redraw()
                return {"RUNNING_MODAL"}

            elif event.type == "M" and event.value == "PRESS":
                self.use_mat_color = not self.use_mat_color
                overlays.gem_map.handler_del()
                overlays.gem_map.handler_add(self, context, is_overlay=False, use_select=self.use_select, use_mat_color=self.use_mat_color)
                self.region.tag_redraw()
                return {"RUNNING_MODAL"}

            elif event.type == "B" and event.value == "PRESS":
                self.use_background = not self.use_background
                self.region.tag_redraw()
                return {"RUNNING_MODAL"}

            elif event.type == "F12" and event.value == "PRESS":
                self.is_rendering = True
                self.region.tag_redraw()
                return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def execute(self, context):
        from ..lib import overlays, view3d_lib
        from ..op_design_report import report_get
        from . import onscreen, report_proc

        ReportData = report_get.data_collect(gem_map=True)

        if not ReportData.gems:
            self.report({"ERROR"}, "No gems in the scene")
            return {"CANCELLED"}

        self.__class__.is_running = True
        self.region = context.region
        self.region_3d = context.space_data.region_3d
        self.is_rendering = False

        # 3D View Options
        # ----------------------------

        lay = view3d_lib.Layout()
        lay.bool(_("Limit by Selection"), "(S)", "use_select")
        lay.bool(_("Material Color"), "(M)", "use_mat_color")
        lay.bool(_("Viewport Background"), "(B)", "use_background")
        lay.proc(_("Save to Image"), "(F12)", "is_rendering")

        # Gem report
        # ----------------------------

        self.table_data = report_proc.data_process(ReportData, self.report_lang)

        # Warnings
        # ----------------------------

        self.show_warn = bool(ReportData.warnings)

        if self.show_warn:
            self.warn = [_("WARNING")] + [f"* {_(x)}" for x in ReportData.warnings]

        # Handlers
        # ----------------------------

        context.window_manager.jewelcraft.show_gem_map = False
        overlays.gem_map.handler_add(self, context, is_overlay=False, use_select=self.use_select, use_mat_color=self.use_mat_color)
        onscreen.handler_add(self, context, lay)

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set("ESC/↵/␣: Exit")

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if self.__class__.is_running:
            self.report({"ERROR"}, "Operator already running")
            return {"CANCELLED"}

        if context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Area type is not 3D View")
            return {"CANCELLED"}

        self.prefs = context.preferences.addons[var.ADDON_ID].preferences
        if self.first_run:
            self.first_run = False
            self.report_lang = self.prefs.report_lang

        if event.ctrl:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        return self.execute(context)

    def is_mouse_inbound(self, event) -> bool:
        return (0 < event.mouse_region_x < self.region.width) and (0 < event.mouse_region_y < self.region.height)
