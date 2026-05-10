# SPDX-FileCopyrightText: 2015-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import math
import tempfile
from pathlib import Path

import blf
import bpy
import gpu
import imbuf
import numpy as np
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from ... import var
from .. import gemlib, unit
from ..asset import gem_dimensions, gem_transform, iter_gems
from ..colorlib import linear_to_srgb, luma

_handler = None
_handler_font = None
_font_loc = []
_font_dim_cache = {}
_font_atlas_key = None
_font_atlas_entries = {}
_font_atlas_texture = None
_font_atlas_image = None
_font_atlas_path = None
_shader_combined = None
_shader_combined_batch_cache_key = None
_shader_combined_batch_cache = None
_transparent_image = None
_transparent_texture = None
_FONT_ATLAS_PADDING = 4
_FONT_ATLAS_MIN_SIZE = 64


def handler_add(self, context, is_overlay=True, use_select=False, use_mat_color=False):
    global _handler
    global _handler_font

    _depsgraph_handler_add()

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(_draw, (self, context, is_overlay, use_select, use_mat_color), "WINDOW", "POST_VIEW")
        _handler_font = bpy.types.SpaceView3D.draw_handler_add(_draw_font, (self, context, is_overlay), "WINDOW", "POST_PIXEL")


def handler_del():
    global _handler
    global _handler_font

    _depsgraph_handler_del()

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(_handler_font, "WINDOW")
        _handler = None
        _handler_font = None

    _cache_clear()


def resources_clear() -> None:
    _font_atlas_clear()
    _transparent_texture_clear()
    _cache_clear()


def handler_toggle(self, context):
    if context.area.type == "VIEW_3D":
        if self.show_gem_map_2:
            handler_add(self, context)
        else:
            handler_del()


def _to_int(x: float) -> int | float:
    if x.is_integer():
        return int(x)
    return x


def _gem_map_create(gems, palette_iter, use_mat_color: bool, opacity: float) -> dict:
    gem_map = {}

    for gem in sorted(gems, key=lambda x: (x[1], -x[2][1], -x[2][0], x[0])):

        if use_mat_color:
            if gem[3]:
                color = (*[linear_to_srgb(x) for x in bpy.data.materials[gem[3]].diffuse_color[:3]], opacity)
            else:
                color = (1.0, 1.0, 1.0, 0.0)
        else:
            color = (*next(palette_iter), opacity)

        color_font = (1.0, 1.0, 1.0) if luma(color) < 0.4 else (0.0, 0.0, 0.0)

        w, l = tuple(_to_int(x) for x in gem[2][:2])

        try:
            trait = gemlib.CUTS[gem[1]].trait
        except KeyError:
            trait = None

        if trait is gemlib.TRAIT_XY_SYMMETRY:
            size = str(l)
        elif trait is gemlib.TRAIT_X_SIZE:
            size = f"{w}×{l}"
        else:
            size = f"{l}×{w}"

        gem_map[gem] = size, color, color_font

    return gem_map


def _font_dim_get(fontid: int, font_size: int, text: str) -> tuple[float, float]:
    cache_key = fontid, font_size, text

    if cache_key not in _font_dim_cache:
        _font_dim_cache[cache_key] = blf.dimensions(fontid, text)

    return _font_dim_cache[cache_key]


def _font_label_add(region, region_3d, text: str, loc, color, size: float) -> None:
    loc_2d = location_3d_to_region_2d(region, region_3d, loc)

    if loc_2d is None or not (0 < loc_2d.x < region.width and 0 < loc_2d.y < region.height):
        return

    _font_loc.append((text, (loc_2d.x, loc_2d.y), loc, color, size))


def _font_labels_prepare(labels: list, fontid: int, font_size: int) -> list:
    return [(*label, *_font_dim_get(fontid, font_size, label[0])) for label in labels]


def _font_screen_pos_get(screen_pos, region, region_3d, loc, to_2d=None):
    if to_2d is None:
        return screen_pos

    loc_2d = to_2d(region, region_3d, loc)

    if loc_2d is None:
        return None

    if hasattr(loc_2d, "x"):
        return loc_2d.x, loc_2d.y

    return loc_2d[0], loc_2d[1]


def _font_atlas_clear() -> None:
    global _font_atlas_key
    global _font_atlas_texture
    global _font_atlas_image
    global _font_atlas_path
    global _shader_combined_batch_cache_key
    global _shader_combined_batch_cache

    _font_atlas_key = None
    _font_atlas_entries.clear()
    _font_atlas_texture = None
    _shader_combined_batch_cache_key = None
    _shader_combined_batch_cache = None

    image = _font_atlas_image
    atlas_path = _font_atlas_path
    _font_atlas_image = None
    _font_atlas_path = None
    _font_atlas_release(image, atlas_path)


def _font_atlas_release(image, atlas_path) -> None:
    if image is not None:
        try:
            image.gl_free()
        except (AttributeError, ReferenceError, RuntimeError):
            pass

        try:
            bpy.data.images.remove(image)
        except (ReferenceError, RuntimeError):
            pass

    if atlas_path is not None:
        atlas_path.unlink(missing_ok=True)


def _font_atlas_texts_get(labels: list) -> tuple[str, ...]:
    return tuple(sorted({label[0] for label in labels}))


def _font_atlas_layout(fontid: int, font_size: int, texts: tuple[str, ...]) -> tuple[dict, int, int]:
    padding = _FONT_ATLAS_PADDING
    items = []
    total_area = 0
    max_width = _FONT_ATLAS_MIN_SIZE

    for text in texts:
        dim_x, dim_y = _font_dim_get(fontid, font_size, text)
        sprite_w = max(1, math.ceil(dim_x)) + padding * 2
        sprite_h = max(1, math.ceil(dim_y)) + padding * 2
        items.append((text, sprite_w, sprite_h))
        total_area += sprite_w * sprite_h
        max_width = max(max_width, sprite_w)

    items.sort(key=lambda item: (item[2], item[1], item[0]), reverse=True)

    atlas_width = max(max_width, math.ceil(math.sqrt(total_area) * 1.25))
    atlas_width = max(_FONT_ATLAS_MIN_SIZE, atlas_width)
    row_height = 0
    x = 0
    y = 0
    entries = {}

    for text, sprite_w, sprite_h in items:
        if x and x + sprite_w > atlas_width:
            x = 0
            y += row_height
            row_height = 0

        entries[text] = (x, y, sprite_w, sprite_h, padding, padding)
        x += sprite_w
        row_height = max(row_height, sprite_h)

    atlas_height = max(y + row_height, _FONT_ATLAS_MIN_SIZE)
    return entries, atlas_width, atlas_height


def _font_atlas_rebuild(fontid: int, font_size: int, texts: tuple[str, ...]) -> bool:
    global _font_atlas_key
    global _font_atlas_texture
    global _font_atlas_image
    global _font_atlas_path
    global _shader_combined_batch_cache_key
    global _shader_combined_batch_cache

    if not texts:
        return False

    blf.size(fontid, font_size)
    entries, atlas_width, atlas_height = _font_atlas_layout(fontid, font_size, texts)
    atlas = imbuf.new((atlas_width, atlas_height))
    atlas_path = None

    try:
        try:
            blf.color(fontid, 1.0, 1.0, 1.0, 1.0)

            with blf.bind_imbuf(fontid, atlas, display_name="sRGB"):
                for text, (x, y, _sprite_w, _sprite_h, offset_x, offset_y) in entries.items():
                    blf.position(fontid, x + offset_x, y + offset_y, 0)
                    blf.draw_buffer(fontid, text)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
                atlas_path = Path(handle.name)

            imbuf.write(atlas, filepath=str(atlas_path))
        except (OSError, RuntimeError, TypeError, ValueError):
            if atlas_path is not None:
                atlas_path.unlink(missing_ok=True)
            return False
    finally:
        atlas.free()

    image = None

    try:
        image = bpy.data.images.load(str(atlas_path), check_existing=False)
        image.alpha_mode = "STRAIGHT"

        try:
            image.colorspace_settings.name = "Non-Color"
        except (AttributeError, TypeError, ValueError):
            pass

        image.use_view_as_render = False
        image.gl_load()
    except (OSError, RuntimeError, TypeError, ValueError):
        _font_atlas_release(image, atlas_path)
        return False

    inv_width = 1.0 / atlas_width
    inv_height = 1.0 / atlas_height
    atlas_entries = {}

    for text, (x, y, sprite_w, sprite_h, offset_x, offset_y) in entries.items():
        u0 = (x + 0.5) * inv_width
        v0 = (y + 0.5) * inv_height
        u1 = (x + sprite_w - 0.5) * inv_width
        v1 = (y + sprite_h - 0.5) * inv_height
        atlas_entries[text] = (
            sprite_w,
            sprite_h,
            offset_x,
            offset_y,
            ((u0, v0), (u1, v0), (u1, v1), (u0, v1)),
        )

    try:
        texture = gpu.texture.from_image(image)

        try:
            texture.filter_mode(True)
            texture.extend_mode("CLAMP_TO_BORDER")
        except (AttributeError, RuntimeError):
            pass
    except (AttributeError, RuntimeError, TypeError, ValueError):
        _font_atlas_release(image, atlas_path)
        return False

    old_image = _font_atlas_image
    old_path = _font_atlas_path

    _font_atlas_entries.clear()
    _font_atlas_entries.update(atlas_entries)
    _font_atlas_image = image
    _font_atlas_texture = texture
    _font_atlas_path = atlas_path
    _shader_combined_batch_cache_key = None
    _shader_combined_batch_cache = None

    _font_atlas_key = fontid, font_size
    _font_atlas_release(old_image, old_path)
    return True


def _font_atlas_ensure(fontid: int, font_size: int, labels: list) -> bool:
    texts = _font_atlas_texts_get(labels)
    cache_key = fontid, font_size

    if not texts:
        return False

    if _font_atlas_texture is not None and _font_atlas_key == cache_key:
        missing_texts = tuple(text for text in texts if text not in _font_atlas_entries)

        if not missing_texts:
            return True

        texts = tuple(sorted((*_font_atlas_entries.keys(), *missing_texts)))

    return _font_atlas_rebuild(fontid, font_size, texts)


def _get_combined_shader():
    global _shader_combined

    if _shader_combined is None:
        interface = gpu.types.GPUStageInterfaceInfo("gem_map_2_font_view_iface")
        interface.smooth("VEC2", "uvInterp")
        interface.smooth("VEC4", "colorInterp")
        interface.smooth("FLOAT", "textInterp")

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant("MAT4", "viewProjectionMatrix")
        shader_info.push_constant("VEC2", "viewportSize")
        shader_info.push_constant("VEC3", "viewOrigin")
        shader_info.push_constant("VEC3", "viewDirection")
        shader_info.push_constant("FLOAT", "perspectiveMix")
        shader_info.push_constant("FLOAT", "depthOffset")
        shader_info.sampler(0, "FLOAT_2D", "image")
        shader_info.vertex_in(0, "VEC3", "anchor")
        shader_info.vertex_in(1, "VEC2", "posOffset")
        shader_info.vertex_in(2, "VEC2", "texCoord")
        shader_info.vertex_in(3, "VEC4", "color")
        shader_info.vertex_in(4, "FLOAT", "radius")
        shader_info.vertex_in(5, "FLOAT", "isText")
        shader_info.vertex_out(interface)
        shader_info.fragment_out(0, "VEC4", "fragColor")
        shader_info.vertex_source(
            """
            void main()
            {
                vec4 clip = viewProjectionMatrix * vec4(anchor, 1.0);

                if (isText > 0.5) {
                    vec3 dirPersp = normalize(anchor - viewOrigin);
                    vec3 dir = normalize(mix(viewDirection, dirPersp, perspectiveMix));
                    clip = viewProjectionMatrix * vec4(anchor - dir * radius, 1.0);
                    clip.xy += (posOffset / viewportSize) * 2.0 * clip.w;
                }

                clip.z -= depthOffset * clip.w;
                uvInterp = texCoord;
                colorInterp = color;
                textInterp = isText;
                gl_Position = clip;
            }
            """
        )
        shader_info.fragment_source(
            """
            void main()
            {
                float alpha = 1.0;

                if (textInterp > 0.5) {
                    alpha = texture(image, uvInterp).a;
                }

                fragColor = vec4(colorInterp.rgb, colorInterp.a * alpha);
            }
            """
        )
        _shader_combined = gpu.shader.create_from_info(shader_info)

    return _shader_combined


def _get_transparent_texture():
    global _transparent_image
    global _transparent_texture

    if _transparent_texture is None:
        image = bpy.data.images.new(".jewelcraft_gem_map_2_empty_atlas", 1, 1, alpha=True)
        image.alpha_mode = "STRAIGHT"
        image.pixels = (0.0, 0.0, 0.0, 0.0)

        try:
            image.colorspace_settings.name = "Non-Color"
        except (AttributeError, TypeError, ValueError):
            pass

        image.use_view_as_render = False
        image.gl_load()
        _transparent_image = image
        _transparent_texture = gpu.texture.from_image(image)

    return _transparent_texture


def _transparent_texture_clear() -> None:
    global _transparent_image
    global _transparent_texture

    image = _transparent_image
    _transparent_image = None
    _transparent_texture = None
    _font_atlas_release(image, None)


def _font_view_state_get(context, region_3d) -> tuple[Vector, Vector, float]:
    inv_view = region_3d.view_matrix.inverted()
    view_origin = inv_view.translation
    view_direction = (inv_view.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    perspective_mix = 1.0

    if region_3d.view_perspective == "ORTHO":
        perspective_mix = 0.0
    elif region_3d.view_perspective == "CAMERA":
        camera = context.scene.camera

        if camera is not None:
            view_origin = camera.matrix_world.translation

            if camera.data.type == "ORTHO":
                perspective_mix = 0.0
                view_direction = (camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()

    return view_origin, view_direction, perspective_mix


def _combined_shader_batch_ensure(shader, depsgraph, records, labels: list, fontid: int, font_size: int, signature: int):
    global _shader_combined_batch_cache_key
    global _shader_combined_batch_cache

    cache_key = _shader_cache_revision, _font_atlas_key, len(records), len(labels), signature

    if _shader_combined_batch_cache_key == cache_key:
        return _shader_combined_batch_cache

    mesh_anchors = []
    mesh_colors = []
    mesh_indices = []
    mesh_vertex_count = 0

    for ob, matrix_key, color in records:
        mesh_data = _mesh_data_get(depsgraph, ob)

        if mesh_data is None:
            continue

        points_h, indices = mesh_data
        matrix = np.array(matrix_key, dtype=np.float32).reshape((4, 4))
        anchors = (points_h @ matrix.T)[:, :3]
        mesh_anchors.append(anchors)
        mesh_colors.append(np.full((len(anchors), 4), color, np.float32))
        mesh_indices.append(indices + mesh_vertex_count)
        mesh_vertex_count += len(anchors)

    text_anchors = []
    text_offsets = []
    text_tex_coords = []
    text_colors = []
    text_radii = []
    text_flags = []
    text_indices = []
    vertex_index = mesh_vertex_count

    for text, loc, color, size in labels:
        entry = _font_atlas_entries.get(text)

        if entry is None:
            continue

        dim_x, dim_y = _font_dim_get(fontid, font_size, text)
        sprite_w, sprite_h, offset_x, offset_y, uv = entry
        left = -dim_x / 2.0 - offset_x
        bottom = -dim_y / 2.0 - offset_y
        corners = np.array(
            (
                (left, bottom),
                (left + sprite_w, bottom),
                (left + sprite_w, bottom + sprite_h),
                (left, bottom + sprite_h),
            ),
            dtype=np.float32,
        )
        text_anchors.append(np.full((4, 3), loc, np.float32))
        text_offsets.append(corners)
        text_tex_coords.append(np.array(uv, np.float32))
        text_colors.append(np.full((4, 4), (*color, 1.0), np.float32))
        text_radii.append(np.full(4, size * 0.5, np.float32))
        text_flags.append(np.ones(4, np.float32))
        text_indices.append(np.array(((vertex_index, vertex_index + 1, vertex_index + 2), (vertex_index, vertex_index + 2, vertex_index + 3)), np.int32))
        vertex_index += 4

    if mesh_anchors:
        mesh_anchors = np.concatenate(mesh_anchors)
        mesh_colors = np.concatenate(mesh_colors)
        mesh_indices = np.concatenate(mesh_indices)
    else:
        mesh_anchors = np.empty((0, 3), np.float32)
        mesh_colors = np.empty((0, 4), np.float32)
        mesh_indices = np.empty((0, 3), np.int32)

    if text_anchors:
        text_anchors = np.concatenate(text_anchors)
        text_offsets = np.concatenate(text_offsets)
        text_tex_coords = np.concatenate(text_tex_coords)
        text_colors = np.concatenate(text_colors)
        text_radii = np.concatenate(text_radii)
        text_flags = np.concatenate(text_flags)
        text_indices = np.concatenate(text_indices)
    else:
        text_anchors = np.empty((0, 3), np.float32)
        text_offsets = np.empty((0, 2), np.float32)
        text_tex_coords = np.empty((0, 2), np.float32)
        text_colors = np.empty((0, 4), np.float32)
        text_radii = np.empty(0, np.float32)
        text_flags = np.empty(0, np.float32)
        text_indices = np.empty((0, 3), np.int32)

    total_vertex_count = len(mesh_anchors) + len(text_anchors)

    if not total_vertex_count:
        _shader_combined_batch_cache = None
        _shader_combined_batch_cache_key = cache_key
        return None

    anchors = np.concatenate((mesh_anchors, text_anchors))
    offsets = np.concatenate((np.zeros((len(mesh_anchors), 2), np.float32), text_offsets))
    tex_coords = np.concatenate((np.zeros((len(mesh_anchors), 2), np.float32), text_tex_coords))
    colors = np.concatenate((mesh_colors, text_colors))
    radii = np.concatenate((np.zeros(len(mesh_anchors), np.float32), text_radii))
    text_flags = np.concatenate((np.zeros(len(mesh_anchors), np.float32), text_flags))
    indices = np.concatenate((mesh_indices, text_indices))

    _shader_combined_batch_cache = batch_for_shader(
        shader,
        "TRIS",
        {"anchor": anchors, "posOffset": offsets, "texCoord": tex_coords, "color": colors, "radius": radii, "isText": text_flags},
        indices=indices,
    )
    _shader_combined_batch_cache_key = cache_key
    return _shader_combined_batch_cache


def _font_labels_3d_to_pixel(region, region_3d, labels: list) -> None:
    for text, loc, color, size in labels:
        _font_label_add(region, region_3d, text, Vector(loc), color, size)


def _draw(self, context, is_overlay=True, use_select=False, use_mat_color=False, display_mode_override=None) -> None:
    region = context.region
    region_3d = context.space_data.region_3d
    depsgraph = context.evaluated_depsgraph_get()
    palette_iter = context.window_manager.jewelcraft.gem_map_palette.iterate()
    from_scene = unit.Scale().from_scene
    font_size = context.preferences.addons[var.ADDON_ID].preferences.gem_map_fontsize_gem_size

    if is_overlay:
        props = context.scene.jewelcraft
        show_all = props.overlay_gem_map_2_show_all
        in_front = props.overlay_gem_map_2_show_in_front
        use_mat_color = props.overlay_gem_map_2_use_material_color
        opacity = props.overlay_gem_map_2_opacity
    else:
        show_all = not use_select
        in_front = True
        opacity = 1.0

    display_mode = "SHADER" if display_mode_override is None else display_mode_override

    is_gem = False
    loc1 = None
    rad1 = 0.0
    ob = context.object

    if ob is not None and (is_gem := ob.select_get() and "gem" in ob):
        loc1 = ob.matrix_world.translation
        rad1 = max(ob.dimensions.xy) / 2.0

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_mask_set(True)

    if not in_front:
        gpu.state.depth_test_set("LESS_EQUAL")

    if display_mode == "SHADER":
        labels = _draw_shader_mode(
            context,
            depsgraph,
            region,
            region_3d,
            palette_iter,
            from_scene,
            show_all,
            in_front,
            is_overlay,
            is_gem,
            loc1,
            rad1,
            use_mat_color,
            opacity,
            font_size,
            context.mode == "EDIT_MESH" and ob is not None and "gem" in ob,
        )

        if labels:
            _font_labels_3d_to_pixel(region, region_3d, labels)
    else:
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        shader.bind()
        _draw_solid_mode(
            shader,
            depsgraph,
            region,
            region_3d,
            palette_iter,
            from_scene,
            show_all,
            is_overlay,
            is_gem,
            loc1,
            rad1,
            use_mat_color,
            opacity,
        )

    gpu.state.blend_set("NONE")
    gpu.state.depth_test_set("NONE")
    gpu.state.depth_mask_set(False)


def _draw_solid_mode(
    shader,
    depsgraph,
    region,
    region_3d,
    palette_iter,
    from_scene,
    show_all,
    is_overlay,
    is_gem,
    loc1,
    rad1,
    use_mat_color,
    opacity,
) -> None:
    mat_sca = Matrix.Diagonal((1.003, 1.003, 1.003)).to_4x4()
    gems = set()

    for dup, ob, _ in iter_gems(depsgraph):
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in from_scene(gem_dimensions(dup)))
        color_name = ob.material_slots[0].name if ob.material_slots else ""
        gems.add((stone, cut, size, color_name))

    gem_map = _gem_map_create(gems, palette_iter, use_mat_color, opacity)

    for dup, ob, instancer in iter_gems(depsgraph):
        loc2, rad2, _ = gem_transform(dup)

        if not show_all:
            show = instancer.select_get()

            if is_overlay and not show and is_gem:
                show = from_scene((loc1 - loc2).length - (rad1 + rad2)) < 0.7

            if not show:
                continue

        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        size = tuple(round(x, 2) for x in from_scene(gem_dimensions(dup)))
        color_name = ob.material_slots[0].name if ob.material_slots else ""
        size, color, font_color = gem_map[(stone, cut, size, color_name)]

        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()

        if me is None:
            continue

        try:
            me.transform(dup.matrix_world @ mat_sca)
            me.calc_loop_triangles()

            points = np.empty((len(me.vertices), 3), np.float32)
            indices = np.empty((len(me.loop_triangles), 3), np.int32)

            me.vertices.foreach_get("co", np.reshape(points, len(me.vertices) * 3))
            me.loop_triangles.foreach_get("vertices", np.reshape(indices, len(me.loop_triangles) * 3))
        finally:
            ob_eval.to_mesh_clear()

        shader.uniform_float("color", color)

        batch = batch_for_shader(shader, "TRIS", {"pos": points}, indices=indices)
        batch.draw(shader)
        _font_label_add(region, region_3d, size, loc2, font_color, rad2 * 2.0)


def _draw_font(self, context, is_overlay=True, to_2d=None, display_mode_override=None):
    global _font_loc

    if not _font_loc:
        return

    region = context.region
    region_3d = context.space_data.region_3d
    prefs = context.preferences.addons[var.ADDON_ID].preferences
    fontid = 0
    font_size = prefs.gem_map_fontsize_gem_size
    blf.size(fontid, font_size)

    labels = _font_labels_prepare(_font_loc, fontid, font_size)

    for text, screen_pos, loc, color, size, dim_x, dim_y in labels:
        actual_screen_pos = _font_screen_pos_get(screen_pos, region, region_3d, loc, to_2d)

        if actual_screen_pos is None:
            continue

        blf.color(fontid, *color, 1.0)
        pos_x, pos_y = actual_screen_pos
        blf.position(fontid, pos_x - dim_x / 2.0, pos_y - dim_y / 2.0, 0)
        blf.draw(fontid, text)

    _font_loc.clear()


_shader_cache_revision = 0
_mesh_data_cache = {}
_SHADER_DEPTH_OFFSET = 1e-4
_GEOMETRY_UPDATE_IDS = {"MESH", "CURVE", "SURFACE", "META", "FONT", "CURVES", "POINTCLOUD", "VOLUME", "LATTICE", "KEY", "NODETREE"}
_BATCH_UPDATE_IDS = _GEOMETRY_UPDATE_IDS | {"OBJECT", "COLLECTION", "MATERIAL"}


def _cache_clear(mesh_data=True):
    global _shader_combined_batch_cache_key
    global _shader_combined_batch_cache

    _shader_combined_batch_cache_key = None
    _shader_combined_batch_cache = None
    _font_loc.clear()

    if mesh_data:
        _mesh_data_cache.clear()


def _cache_invalidate(mesh_data=True) -> None:
    global _shader_cache_revision

    _shader_cache_revision += 1
    _cache_clear(mesh_data=mesh_data)


def _id_key(id_data) -> int:
    return getattr(id_data, "session_uid", id_data.as_pointer())


def _depsgraph_id_type_updated(depsgraph, id_type: str) -> bool:
    try:
        return depsgraph.id_type_updated(id_type)
    except (AttributeError, TypeError):
        return False


def _depsgraph_update_flags(depsgraph) -> tuple[bool, bool]:
    update_batch = False
    update_mesh_data = False

    try:
        for update in depsgraph.updates:
            id_type = getattr(update.id, "id_type", "")

            if update.is_updated_geometry or id_type in _GEOMETRY_UPDATE_IDS:
                update_mesh_data = True
                update_batch = True
                break

            if update.is_updated_transform or update.is_updated_shading or id_type in _BATCH_UPDATE_IDS:
                update_batch = True
    except (AttributeError, ReferenceError):
        return True, True

    if update_batch or update_mesh_data:
        return update_batch, update_mesh_data

    update_mesh_data = any(
        _depsgraph_id_type_updated(depsgraph, id_type)
        for id_type in ("MESH", "CURVE", "SURFACE", "META", "FONT", "CURVES", "LATTICE", "KEY", "NODETREE")
    )
    update_batch = update_mesh_data or any(
        _depsgraph_id_type_updated(depsgraph, id_type)
        for id_type in ("OBJECT", "COLLECTION", "MATERIAL")
    )

    if not update_batch and not update_mesh_data:
        update_batch = True
        update_mesh_data = True

    return update_batch, update_mesh_data


def _depsgraph_changed(_scene, depsgraph=None) -> None:
    if _handler is None:
        return

    if depsgraph is None:
        _cache_invalidate(mesh_data=True)
        return

    update_batch, update_mesh_data = _depsgraph_update_flags(depsgraph)

    if update_mesh_data:
        _cache_invalidate(mesh_data=True)
    elif update_batch:
        _cache_invalidate(mesh_data=False)


def _depsgraph_handler_add() -> None:
    handlers = bpy.app.handlers.depsgraph_update_post

    if _depsgraph_changed not in handlers:
        handlers.append(_depsgraph_changed)


def _depsgraph_handler_del() -> None:
    handlers = bpy.app.handlers.depsgraph_update_post

    if _depsgraph_changed in handlers:
        handlers.remove(_depsgraph_changed)


def _matrix_key(matrix: Matrix) -> tuple[float, ...]:
    return tuple(value for row in matrix for value in row)


def _instance_key(dup, ob, instancer) -> tuple:
    if dup.is_instance:
        persistent_id = tuple(dup.persistent_id)
    else:
        persistent_id = ()

    return _id_key(ob), _id_key(instancer), persistent_id


def _mesh_cache_key(ob) -> tuple:
    me = getattr(ob, "data", None)
    modifier_key = tuple(
        (
            md.type,
            md.name,
            md.show_viewport,
            getattr(md, "show_in_editmode", False),
            getattr(md, "show_on_cage", False),
        )
        for md in ob.modifiers
    )

    if ob.modifiers:
        return ob.type, _id_key(ob), _id_key(me) if me is not None else 0, modifier_key

    if me is None:
        return ob.type, _id_key(ob)

    return ob.type, _id_key(me)


def _mesh_data_get(depsgraph, ob):
    cache_key = None if ob.modifiers else _mesh_cache_key(ob)

    if cache_key is not None and cache_key in _mesh_data_cache:
        return _mesh_data_cache[cache_key]

    ob_eval = ob.evaluated_get(depsgraph)
    me_eval = ob_eval.to_mesh()

    if me_eval is None:
        return None

    try:
        me_eval.calc_loop_triangles()

        if not len(me_eval.vertices) or not len(me_eval.loop_triangles):
            return None

        points = np.empty((len(me_eval.vertices), 3), np.float32)
        indices = np.empty((len(me_eval.loop_triangles), 3), np.int32)

        me_eval.vertices.foreach_get("co", np.reshape(points, len(me_eval.vertices) * 3))
        me_eval.loop_triangles.foreach_get("vertices", np.reshape(indices, len(me_eval.loop_triangles) * 3))

        points_h = np.empty((len(me_eval.vertices), 4), np.float32)
        points_h[:, :3] = points
        points_h[:, 3] = 1.0

        data = points_h, indices

        if cache_key is not None:
            _mesh_data_cache[cache_key] = data

        return data
    finally:
        ob_eval.to_mesh_clear()


def _draw_shader_mode(
    context,
    depsgraph,
    region,
    region_3d,
    palette_iter,
    from_scene,
    show_all,
    in_front,
    is_overlay,
    is_gem,
    loc1,
    rad1,
    use_mat_color,
    opacity,
    font_size,
    force_geometry_update,
) -> list:
    if force_geometry_update:
        _cache_invalidate(mesh_data=True)

    records = []
    gems = set()

    for dup, ob, instancer in iter_gems(depsgraph):
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        gem_size = tuple(round(x, 2) for x in from_scene(gem_dimensions(dup)))
        color_name = ob.material_slots[0].name if ob.material_slots else ""
        gem = stone, cut, gem_size, color_name
        gems.add(gem)

        loc2, rad2, _ = gem_transform(dup)

        if not show_all:
            show = instancer.select_get()

            if is_overlay and not show and is_gem:
                show = from_scene((loc1 - loc2).length - (rad1 + rad2)) < 0.7

            if not show:
                continue

        records.append((ob, _instance_key(dup, ob, instancer), _mesh_cache_key(ob), _matrix_key(dup.matrix_world), gem, loc2, rad2))

    gem_map = _gem_map_create(gems, palette_iter, use_mat_color, opacity)
    batch_records = []
    labels = []
    signature = 0

    for ob, instance_key, mesh_key, matrix_key, gem, loc2, rad2 in records:
        size, color, font_color = gem_map[gem]
        record_key = (instance_key, mesh_key, matrix_key, color)
        label = (size, tuple(loc2), font_color, rad2 * 2.0)
        signature = hash((signature, record_key, label))
        batch_records.append((ob, matrix_key, color))
        labels.append(label)

    fontid = 0
    font_ready = bool(labels and _font_atlas_ensure(fontid, font_size, labels))
    shader = _get_combined_shader()
    batch = _combined_shader_batch_ensure(shader, depsgraph, batch_records, labels if font_ready else (), fontid, font_size, signature)

    if batch is None:
        return []

    view_origin, view_direction, perspective_mix = _font_view_state_get(context, region_3d)
    depth_mode = "NONE" if (not show_all or in_front) else "LESS_EQUAL"

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_mask_set(False)
    gpu.state.depth_test_set(depth_mode)
    shader.bind()
    shader.uniform_float("viewProjectionMatrix", region_3d.perspective_matrix)
    shader.uniform_float("viewportSize", (region.width, region.height))
    shader.uniform_float("viewOrigin", view_origin)
    shader.uniform_float("viewDirection", view_direction)
    shader.uniform_float("perspectiveMix", perspective_mix)
    shader.uniform_float("depthOffset", _SHADER_DEPTH_OFFSET)

    shader.uniform_sampler("image", _font_atlas_texture if font_ready else _get_transparent_texture())

    batch.draw(shader)
    return [] if font_ready else labels
