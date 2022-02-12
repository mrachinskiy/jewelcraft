# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import gpu
from gpu_extras.presets import draw_texture_2d

from ..lib import view3d_lib
from . import onscreen_text


def draw(self, context):
    width = self.region.width
    height = self.region.height
    x = self.view_padding_left
    y = self.view_padding_top

    # Gem map
    # -----------------------------

    if not self.use_navigate:
        gpu.state.blend_set("ALPHA")
        draw_texture_2d(self.offscreen.texture_color, (0, 0), width, height)

    # Onscreen text
    # -----------------------------

    y = onscreen_text.onscreen_gem_table(self, x, y)
    y -= self.view_margin

    if self.show_warn:
        y = onscreen_text.onscreen_warning(self, x, y)
        y -= self.view_margin

    view3d_lib.options_display(self, context, x, y)

    # Reset state
    # ----------------------------

    gpu.state.blend_set("NONE")
