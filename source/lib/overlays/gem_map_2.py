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
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ... import var
from .. import gemlib, unit
from ..asset import gem_dimensions, gem_transform, iter_gems
from ..colorlib import linear_to_srgb, luma

_FONT_ID = 0
_FONT_ATLAS_PADDING = 4
_FONT_ATLAS_MIN_SIZE = 64
_UPDATE_IDS_GEOMETRY = {"MESH"}
_UPDATE_IDS_BATCH = _UPDATE_IDS_GEOMETRY | {"OBJECT", "COLLECTION", "MATERIAL"}

_handler = None
_shader_combined = None
_cache = {
    "mesh_data": {},
    "draw": {
        "revision": 0,
        "batch_key": None,
        "batch": None,
        "atlas_key": None,
        "atlas_entries": {},
        "atlas_texture": None,
        "atlas_image": None,
        "atlas_path": None,
        "empty_image": None,
        "empty_texture": None,
    },
}


def handler_add(self, context, is_overlay=True, use_select=False, use_mat_color=False):
    global _handler

    handlers = bpy.app.handlers.depsgraph_update_post

    if _depsgraph_changed not in handlers:
        handlers.append(_depsgraph_changed)

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(_draw, (self, context, is_overlay, use_select, use_mat_color), "WINDOW", "POST_VIEW")


def handler_del():
    global _handler

    handlers = bpy.app.handlers.depsgraph_update_post

    if _depsgraph_changed in handlers:
        handlers.remove(_depsgraph_changed)

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, "WINDOW")
        _handler = None

    _cache_clear()


def resources_clear() -> None:
    _draw_cache_clear(atlas=True, empty=True)
    _cache["mesh_data"].clear()


def handler_toggle(self, context):
    if context.area.type == "VIEW_3D":
        if self.show_gem_map_2:
            handler_add(self, context)
        else:
            handler_del()


def _font_atlas_release(image, atlas_path) -> None:
    if image is not None:
        try:
            image.gl_free()
        except (ReferenceError, RuntimeError):
            pass

        try:
            bpy.data.images.remove(image)
        except (ReferenceError, RuntimeError):
            pass

    if atlas_path is not None:
        atlas_path.unlink(missing_ok=True)


def _draw_cache_clear(*, atlas=False, empty=False) -> None:
    draw_cache = _cache["draw"]
    draw_cache["batch_key"] = None
    draw_cache["batch"] = None

    if atlas:
        image = draw_cache["atlas_image"]
        path = draw_cache["atlas_path"]
        draw_cache["atlas_key"] = None
        draw_cache["atlas_entries"].clear()
        draw_cache["atlas_texture"] = None
        draw_cache["atlas_image"] = None
        draw_cache["atlas_path"] = None
        _font_atlas_release(image, path)

    if empty:
        image = draw_cache["empty_image"]
        draw_cache["empty_image"] = None
        draw_cache["empty_texture"] = None
        _font_atlas_release(image, None)


def _cache_clear(mesh_data=True):
    _draw_cache_clear()

    if mesh_data:
        _cache["mesh_data"].clear()


def _cache_invalidate(mesh_data=True) -> None:
    _cache["draw"]["revision"] += 1
    _cache_clear(mesh_data=mesh_data)


def _instance_key(dup, ob, instancer) -> tuple:
    random_id = int(dup.random_id) if dup.is_instance else 0
    return (
        None if ob is None else ob.session_uid,
        None if instancer is None else instancer.session_uid,
        random_id,
    )


def _depsgraph_update_flags(depsgraph) -> tuple[bool, bool]:
    update_batch = False
    update_mesh_data = False

    try:
        for update in depsgraph.updates:
            id_type = update.id.id_type

            if update.is_updated_geometry or id_type in _UPDATE_IDS_GEOMETRY:
                update_mesh_data = True
                update_batch = True
                break

            if update.is_updated_transform or update.is_updated_shading or id_type in _UPDATE_IDS_BATCH:
                update_batch = True
                
    except ReferenceError:
        return True, True

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


def _draw(
    self,
    context,
    is_overlay=True,
    use_select=False,
    use_mat_color=False,
    view_matrix_override=None,
    projection_matrix_override=None,
    viewport_size_override=None,
) -> None:
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

    ob = context.object
    is_gem = False
    loc1 = None
    rad1 = 0.0

    if ob is not None and (is_gem := ob.select_get() and "gem" in ob):
        loc1 = ob.matrix_world.translation
        rad1 = max(ob.dimensions.xy) / 2.0

    records, gems = _gem_records_collect(depsgraph, from_scene, show_all, is_overlay, is_gem, loc1, rad1)
    gem_map = _gem_map_create(gems, palette_iter, use_mat_color, opacity)

    _draw_shader_mode(
        context,
        depsgraph,
        region,
        region_3d,
        records,
        gem_map,
        in_front,
        font_size,
        context.mode == "EDIT_MESH" and ob is not None and "gem" in ob,
        view_matrix_override=view_matrix_override,
        projection_matrix_override=projection_matrix_override,
        viewport_size_override=viewport_size_override,
    )

    gpu.state.blend_set("NONE")
    gpu.state.depth_test_set("NONE")
    gpu.state.depth_mask_set(False)


def _gem_records_collect(depsgraph, from_scene, show_all, is_overlay, is_gem, loc1, rad1) -> tuple[list, set]:
    records = []
    gems = set()

    for dup, ob, instancer in iter_gems(depsgraph):
        stone = ob["gem"]["stone"]
        cut = ob["gem"]["cut"]
        gem_size = tuple(round(x, 2) for x in from_scene(gem_dimensions(dup)))
        material = ob.material_slots[0].material if ob.material_slots else None
        material_color = tuple(material.diffuse_color[:3]) if material is not None else None
        gem = stone, cut, gem_size, material_color
        gems.add(gem)

        loc2, rad2, _ = gem_transform(dup)

        if not show_all:
            show = instancer.select_get()

            if is_overlay and not show and is_gem:
                show = from_scene((loc1 - loc2).length - (rad1 + rad2)) < 0.7

            if not show:
                continue

        matrix_key = dup.matrix_world.copy()
        matrix_key.freeze()
        records.append((ob, gem, loc2, rad2, _instance_key(dup, ob, instancer), matrix_key))

    return records, gems


def _gem_map_create(gems, palette_iter, use_mat_color: bool, opacity: float) -> dict:
    gem_map = {}

    for gem in sorted(gems, key=lambda item: (item[1], -item[2][1], -item[2][0], item[0], item[3])):
        
        stone, cut, gem_size, material_color = gem
        
        if use_mat_color:
            if material_color is not None:
                color = (*(linear_to_srgb(x) for x in material_color), opacity)
            else:
                color = (1.0, 1.0, 1.0, 0.0)
        else:
            color = (*next(palette_iter), opacity)

        color_font = (1.0, 1.0, 1.0) if luma(color) < 0.4 else (0.0, 0.0, 0.0)
        w, l = tuple(int(value) if value.is_integer() else value for value in gem_size[:2])

        try:
            trait = gemlib.CUTS[cut].trait
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


def _draw_shader_mode(
    context,
    depsgraph,
    region,
    region_3d,
    records,
    gem_map,
    in_front,
    font_size,
    force_geometry_update,
    *,
    view_matrix_override=None,
    projection_matrix_override=None,
    viewport_size_override=None,
) -> None:
    global _shader_combined

    if force_geometry_update:
        _cache_invalidate(mesh_data=True)

    draw_cache = _cache["draw"]

    batch_records = []
    labels = []
    signature = 0

    for ob, gem, loc, radius, instance_key, matrix_key in records:
        size, color, font_color = gem_map[gem]
        record_key = (instance_key, matrix_key, color)
        label = (size, loc, font_color, radius * 2.0)
        signature = hash((signature, record_key, label))
        batch_records.append((ob, matrix_key, color))
        labels.append(label)

    font_ready = False

    if labels:
        texts = tuple(sorted({label[0] for label in labels}))
        cache_key = _FONT_ID, font_size

        if draw_cache["atlas_texture"] is not None and draw_cache["atlas_key"] == cache_key:
            missing_texts = tuple(text for text in texts if text not in draw_cache["atlas_entries"])

            if not missing_texts:
                font_ready = True
            else:
                texts = tuple(sorted((*draw_cache["atlas_entries"].keys(), *missing_texts)))

        if not font_ready:
            font_ready = _font_atlas_rebuild(font_size, texts)

    if _shader_combined is None:
        interface = gpu.types.GPUStageInterfaceInfo("gem_map_2_font_view_iface")
        interface.smooth("VEC2", "uvInterp")
        interface.smooth("VEC4", "colorInterp")
        interface.flat("FLOAT", "radiusInterp")

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant("MAT4", "viewProjectionMatrix")
        shader_info.push_constant("VEC2", "viewportSize")
        shader_info.push_constant("VEC4", "viewOriginAndMix")
        shader_info.push_constant("VEC3", "viewDirection")
        shader_info.sampler(0, "FLOAT_2D", "image")
        shader_info.vertex_in(0, "VEC3", "anchor")
        shader_info.vertex_in(1, "VEC4", "glyphData")
        shader_info.vertex_in(2, "VEC4", "color")
        shader_info.vertex_in(3, "FLOAT", "radius")
        shader_info.vertex_out(interface)
        shader_info.fragment_out(0, "VEC4", "fragColor")
        shader_info.vertex_source(
            """
            #define DEPTH_OFFSET 0.00005

            void main()
            {
                vec3 viewOrigin = viewOriginAndMix.xyz;
                float perspectiveMix = viewOriginAndMix.w;
                vec4 clip = viewProjectionMatrix * vec4(anchor, 1.0);
                vec2 posOffset = glyphData.xy;

                if (radius > 0.0) {
                    vec3 dirPersp = normalize(anchor - viewOrigin);
                    vec3 dir = normalize(mix(viewDirection, dirPersp, perspectiveMix));
                    clip = viewProjectionMatrix * vec4(anchor - dir * radius, 1.0);
                    clip.xy += (posOffset / viewportSize) * 2.0 * clip.w;
                }

                clip.z -= DEPTH_OFFSET;
                uvInterp = glyphData.zw;
                colorInterp = color;
                radiusInterp = radius;
                gl_Position = clip;
            }
            """
        )
        shader_info.fragment_source(
            """
            void main()
            {
                float alpha = 1.0;

                if (radiusInterp > 0.0) {
                    alpha = texture(image, uvInterp).a;
                }

                fragColor = vec4(colorInterp.rgb, colorInterp.a * alpha);
            }
            """
        )
        _shader_combined = gpu.shader.create_from_info(shader_info)

    batch = _combined_shader_batch_ensure(
        _shader_combined,
        depsgraph,
        batch_records,
        labels if font_ready else (),
        signature,
    )

    if batch is None:
        return

    if view_matrix_override is None and projection_matrix_override is None:
        view_matrix = region_3d.view_matrix
        view_projection_matrix = region_3d.perspective_matrix
    else:
        view_matrix = region_3d.view_matrix if view_matrix_override is None else view_matrix_override
        projection_matrix = region_3d.window_matrix if projection_matrix_override is None else projection_matrix_override
        view_projection_matrix = projection_matrix @ view_matrix

    inv_view = view_matrix.inverted()
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

    image_texture = draw_cache["atlas_texture"]

    if image_texture is None:
        if draw_cache["empty_texture"] is None:
            image = bpy.data.images.new(".jewelcraft_gem_map_2_empty_atlas", 1, 1, alpha=True, is_data=True)
            image.alpha_mode = "STRAIGHT"
            image.pixels = (0.0, 0.0, 0.0, 0.0)

            image.use_view_as_render = False
            image.gl_load()
            draw_cache["empty_image"] = image
            draw_cache["empty_texture"] = gpu.texture.from_image(image)

        image_texture = draw_cache["empty_texture"]

    viewport_size = (region.width, region.height) if viewport_size_override is None else viewport_size_override
    depth_mode = "NONE" if in_front else "LESS_EQUAL"

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_mask_set(False)
    gpu.state.depth_test_set(depth_mode)
    _shader_combined.bind()
    _shader_combined.uniform_float("viewProjectionMatrix", view_projection_matrix)
    _shader_combined.uniform_float("viewportSize", viewport_size)
    _shader_combined.uniform_float("viewOriginAndMix", (*view_origin, perspective_mix))
    _shader_combined.uniform_float("viewDirection", view_direction)
    _shader_combined.uniform_sampler("image", image_texture)
    batch.draw(_shader_combined)


def _font_atlas_rebuild(font_size: int, texts: tuple[str, ...]) -> bool:
    draw_cache = _cache["draw"]

    if not texts:
        return False

    blf.size(_FONT_ID, font_size)
    padding = _FONT_ATLAS_PADDING
    items = []
    total_area = 0
    max_width = _FONT_ATLAS_MIN_SIZE

    for text in texts:
        dim_x, dim_y = blf.dimensions(_FONT_ID, text)
        sprite_w = max(1, math.ceil(dim_x)) + padding * 2
        sprite_h = max(1, math.ceil(dim_y)) + padding * 2
        items.append((text, dim_x, dim_y, sprite_w, sprite_h))
        total_area += sprite_w * sprite_h
        max_width = max(max_width, sprite_w)

    items.sort(key=lambda item: (item[4], item[3], item[0]), reverse=True)

    atlas_width = max(max_width, math.ceil(math.sqrt(total_area) * 1.25))
    atlas_width = max(_FONT_ATLAS_MIN_SIZE, atlas_width)
    row_height = 0
    x = 0
    y = 0
    entries = {}

    for text, dim_x, dim_y, sprite_w, sprite_h in items:
        if x and x + sprite_w > atlas_width:
            x = 0
            y += row_height
            row_height = 0

        entries[text] = (dim_x, dim_y, x, y, sprite_w, sprite_h, padding, padding)
        x += sprite_w
        row_height = max(row_height, sprite_h)

    atlas_height = max(y + row_height, _FONT_ATLAS_MIN_SIZE)
    atlas = imbuf.new((atlas_width, atlas_height))
    atlas_path = None

    try:
        try:
            blf.color(_FONT_ID, 1.0, 1.0, 1.0, 1.0)

            with blf.bind_imbuf(_FONT_ID, atlas, display_name="sRGB"):
                for text, (_dim_x, _dim_y, x, y, _sprite_w, _sprite_h, offset_x, offset_y) in entries.items():
                    blf.position(_FONT_ID, x + offset_x, y + offset_y, 0)
                    blf.draw_buffer(_FONT_ID, text)

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
        except (TypeError, ValueError):
            pass

        image.use_view_as_render = False
        image.gl_load()
    except (OSError, RuntimeError, TypeError, ValueError):
        _font_atlas_release(image, atlas_path)
        return False

    inv_width = 1.0 / atlas_width
    inv_height = 1.0 / atlas_height
    atlas_entries = {}

    for text, (dim_x, dim_y, x, y, sprite_w, sprite_h, offset_x, offset_y) in entries.items():
        u0 = (x + 0.5) * inv_width
        v0 = (y + 0.5) * inv_height
        u1 = (x + sprite_w - 0.5) * inv_width
        v1 = (y + sprite_h - 0.5) * inv_height
        atlas_entries[text] = (
            dim_x,
            dim_y,
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

    old_image = draw_cache["atlas_image"]
    old_path = draw_cache["atlas_path"]

    draw_cache["atlas_entries"].clear()
    draw_cache["atlas_entries"].update(atlas_entries)
    draw_cache["atlas_image"] = image
    draw_cache["atlas_texture"] = texture
    draw_cache["atlas_path"] = atlas_path
    draw_cache["atlas_key"] = _FONT_ID, font_size
    _draw_cache_clear()
    _font_atlas_release(old_image, old_path)
    return True


def _combined_shader_batch_ensure(shader, depsgraph, records, labels: list, signature: int):
    draw_cache = _cache["draw"]

    cache_key = draw_cache["revision"], draw_cache["atlas_key"], len(records), len(labels), signature

    if draw_cache["batch_key"] == cache_key:
        return draw_cache["batch"]

    anchors = []
    glyph_data = []
    colors = []
    radii = []
    indices = []
    vertex_index = 0

    for ob, matrix_key, color in records:
        mesh_data = _mesh_data_get(depsgraph, ob)

        if mesh_data is None:
            continue

        points_h, mesh_indices = mesh_data
        matrix = np.asarray(matrix_key, dtype=np.float32)
        mesh_anchors = (points_h @ matrix.T)[:, :3]
        vertex_count = len(mesh_anchors)
        anchors.append(mesh_anchors)
        glyph_data.append(np.zeros((vertex_count, 4), np.float32))
        colors.append(np.full((vertex_count, 4), color, np.float32))
        radii.append(np.zeros(vertex_count, np.float32))
        indices.append(mesh_indices + vertex_index)
        vertex_index += vertex_count

    for text, loc, color, size in labels:
        entry = draw_cache["atlas_entries"].get(text)

        if entry is None:
            continue

        dim_x, dim_y, sprite_w, sprite_h, offset_x, offset_y, uv = entry
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
        anchors.append(np.full((4, 3), loc, np.float32))
        glyph_data.append(np.concatenate((corners, np.array(uv, np.float32)), axis=1))
        colors.append(np.full((4, 4), (*color, 1.0), np.float32))
        radii.append(np.full(4, size * 0.5, np.float32))
        indices.append(np.array(((vertex_index, vertex_index + 1, vertex_index + 2), (vertex_index, vertex_index + 2, vertex_index + 3)), np.int32))
        vertex_index += 4

    if not vertex_index:
        draw_cache["batch"] = None
        draw_cache["batch_key"] = cache_key
        return None

    draw_cache["batch"] = batch_for_shader(
        shader,
        "TRIS",
        {
            "anchor": np.concatenate(anchors),
            "glyphData": np.concatenate(glyph_data),
            "color": np.concatenate(colors),
            "radius": np.concatenate(radii),
        },
        indices=np.concatenate(indices),
    )
    draw_cache["batch_key"] = cache_key
    return draw_cache["batch"]


def _mesh_data_get(depsgraph, ob):
    mesh_data_cache = _cache["mesh_data"]

    if ob.type != "MESH":
        return None

    me = ob.data
    cache_key = None if ob.modifiers else me.session_uid

    if cache_key is not None and cache_key in mesh_data_cache:
        return mesh_data_cache[cache_key]

    ob_eval = ob.evaluated_get(depsgraph)
    me_eval = ob_eval.to_mesh()

    if me_eval is None:
        return None

    try:
        me_eval.calc_loop_triangles()

        if not len(me_eval.vertices) or not len(me_eval.loop_triangles):
            return None

        vertex_count = len(me_eval.vertices)
        triangle_count = len(me_eval.loop_triangles)
        points = np.empty(vertex_count * 3, np.float32)
        points_h = np.empty((vertex_count, 4), np.float32)
        indices = np.empty((triangle_count, 3), np.int32)

        me_eval.vertices.foreach_get("co", points)
        me_eval.loop_triangles.foreach_get("vertices", indices.reshape(triangle_count * 3))
        points_h[:, :3] = points.reshape((vertex_count, 3))
        points_h[:, 3] = 1.0

        data = points_h, indices

        if cache_key is not None:
            mesh_data_cache[cache_key] = data

        return data
    finally:
        ob_eval.to_mesh_clear()