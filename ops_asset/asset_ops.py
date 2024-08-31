# SPDX-FileCopyrightText: 2015-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator

from .. import var
from ..lib import dynamic_list


def _asset_menu_lock():
    bpy.context.window_manager.jewelcraft.asset_menu_ui_lock = True


def upd_asset_name(self, context):
    if self.type == "COLLECTION":
        self.asset_name = self.collection_name
    else:
        self.asset_name = self.object_name


class AssetAdd:
    type: EnumProperty(
        name="Type",
        description="",
        items=(
            ("COLLECTION", "Collection", ""),
            ("OBJECT", "Object", ""),
        ),
        update=upd_asset_name,
    )
    collection_name: StringProperty(name="Collection", options={"SKIP_SAVE"})
    object_name: StringProperty(name="Object", options={"SKIP_SAVE"})
    asset_name: StringProperty(name="Asset Name", options={"SKIP_SAVE"})
    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    @classmethod
    def poll(cls, context):
        return bool(context.window_manager.jewelcraft.asset_folder)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        if self.is_add:
            col = layout.column()
            col.alert = not self.asset_name
            col.prop(self, "asset_name")

        layout.prop(self, "type")

        col = layout.column()

        if self.type == "COLLECTION":
            col.alert = not self.collection_name
            col.prop_search(self, "collection_name", bpy.data, "collections")
        else:
            col.alert = not self.object_name
            col.prop_search(self, "object_name", bpy.data, "objects")

        layout.separator()

    def execute(self, context):
        from ..lib import asset

        if not self.asset_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        if self.type == "COLLECTION":
            if not self.collection_name:
                self.report({"ERROR"}, "Collection must be specified")
                return {"CANCELLED"}
        else:
            if not self.object_name:
                self.report({"ERROR"}, "Object must be specified")
                return {"CANCELLED"}

        if self.is_add:
            wm_props = context.window_manager.jewelcraft
            filepath = wm_props.asset_libs.path() / wm_props.asset_folder / (self.asset_name + ".blend")
        else:
            filepath = Path(self.filepath)

        data_blocks = self.asset_dbs_get()
        asset.asset_export(data_blocks, filepath)

        if self.is_add:
            prefs = context.preferences.addons[var.ADDON_ID].preferences
            resolution = prefs.asset_preview_resolution

            asset.render_preview(resolution, resolution, filepath.with_suffix(".png"))
            dynamic_list.assets_refresh()
            context.area.tag_redraw()
        else:
            _asset_menu_lock()

        return {"FINISHED"}

    def invoke(self, context, event):
        if context.collection and context.collection is not context.scene.collection:
            self.collection_name = context.collection.name
        if context.object:
            self.object_name = context.object.name

        if self.is_add:
            upd_asset_name(self, context)
        elif self.filepath:
            self.asset_name = Path(self.filepath).stem

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def asset_dbs_get(self) -> set:
        if self.type == "COLLECTION":
            collection = bpy.data.collections[self.collection_name]
            return {collection}
        else:
            ob = bpy.data.objects[self.object_name]
            return {ob}


class WM_OT_asset_add(AssetAdd, Operator):
    bl_label = "Add to Library"
    bl_description = "Add selected objects to asset library"
    bl_idname = "wm.jewelcraft_asset_add"
    bl_options = {"INTERNAL"}

    is_add = True


class WM_OT_asset_replace(AssetAdd, Operator):
    bl_label = "Replace Asset"
    bl_description = "Replace current asset with selected objects"
    bl_idname = "wm.jewelcraft_asset_replace"
    bl_options = {"INTERNAL"}

    is_add = False


class WM_OT_asset_remove(Operator):
    bl_label = "Remove"
    bl_description = "Remove from library"
    bl_idname = "wm.jewelcraft_asset_remove"
    bl_options = {"INTERNAL"}

    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        path = Path(self.filepath)
        path.unlink(missing_ok=True)
        path.with_suffix(".png").unlink(missing_ok=True)

        dynamic_list.assets_refresh(self.filepath, favs=True)
        _asset_menu_lock()
        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_asset_rename(Operator):
    bl_label = "Rename"
    bl_description = "Rename asset"
    bl_idname = "wm.jewelcraft_asset_rename"
    bl_options = {"INTERNAL"}

    asset_name: StringProperty(name="Asset Name", options={"SKIP_SAVE"})
    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        layout.alert = not self.asset_name
        layout.prop(self, "asset_name")
        layout.separator()

    def execute(self, context):
        if not self.asset_name:
            self.report({"ERROR"}, "Name must be specified")
            return {"CANCELLED"}

        if self.asset_name == self.name_current:
            return {"CANCELLED"}

        path = Path(self.filepath)
        path_new = path.with_stem(self.asset_name)

        if not path.exists():
            self.report({"ERROR"}, "File not found")
            return {"CANCELLED"}

        path.rename(path_new)

        preview = path.with_suffix(".png")
        preview_new = path_new.with_suffix(".png")

        if preview.exists():
            preview.rename(preview_new)

        dynamic_list.assets_refresh(favs=True)
        _asset_menu_lock()
        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        self.name_current = self.asset_name = Path(self.filepath).stem
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class WM_OT_asset_preview_replace(Operator):
    bl_label = "Replace Preview"
    bl_description = "Replace asset preview image"
    bl_idname = "wm.jewelcraft_asset_preview_replace"
    bl_options = {"INTERNAL"}

    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        from ..lib import asset

        prefs = context.preferences.addons[var.ADDON_ID].preferences
        resolution = prefs.asset_preview_resolution

        asset.render_preview(resolution, resolution, Path(self.filepath).with_suffix(".png"))

        dynamic_list.assets_refresh(self.filepath)
        _asset_menu_lock()
        context.area.tag_redraw()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class WM_OT_asset_import(Operator):
    bl_label = "Import Asset"
    bl_description = "Import selected asset"
    bl_idname = "wm.jewelcraft_asset_import"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    use_parent: BoolProperty(
        name="Parent to selected",
        description="Parent imported asset to selected objects (Shortcut: hold Alt when using the tool)",
        options={"SKIP_SAVE"},
    )
    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        from ..lib import asset

        space_data = context.space_data
        use_local_view = bool(space_data.local_view)
        collection = context.collection
        selected = list(context.selected_objects)

        for ob in selected:
            ob.select_set(False)

        imported = asset.asset_import_batch(self.filepath)

        if imported.collections:
            for coll in imported.collections:
                if not coll.users or coll.users == len(coll.users_dupli_group):
                    context.scene.collection.children.link(coll)

        for ob in imported.objects:
            if not ob.users:
                collection.objects.link(ob)

            if use_local_view:
                ob.local_view_set(space_data, True)

            ob.select_set(True)

        if len(imported.objects) == 1:
            ob.location = context.scene.cursor.location

            if context.mode == "EDIT_MESH":
                asset.ob_copy_to_faces(ob)
                bpy.ops.object.mode_set(mode="OBJECT")
            elif self.use_parent and selected:
                collection.objects.unlink(ob)
                asset.ob_copy_and_parent(ob, selected)

        context.view_layer.objects.active = ob

        return {"FINISHED"}

    def invoke(self, context, event):
        self.use_parent = event.alt
        return self.execute(context)


class WM_OT_asset_menu(Operator):
    bl_label = "Asset Menu"
    bl_description = "Asset menu"
    bl_idname = "wm.jewelcraft_asset_menu"
    bl_options = {"INTERNAL"}

    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        if context.window_manager.jewelcraft.asset_menu_ui_lock:
            layout.label(text="Action completed", icon="INFO")
            return

        layout.emboss = "PULLDOWN_MENU"

        row = layout.row()
        row.operator("wm.jewelcraft_asset_rename", text="", icon="OUTLINER_DATA_GP_LAYER").filepath = self.filepath
        row.operator("wm.jewelcraft_asset_preview_replace", text="", icon="IMAGE_DATA").filepath = self.filepath
        row.operator("wm.jewelcraft_asset_replace", text="", icon="FILE_TICK").filepath = self.filepath
        row.operator("wm.jewelcraft_asset_remove", text="", icon="TRASH").filepath = self.filepath

    def invoke(self, context, event):
        context.window_manager.jewelcraft.asset_menu_ui_lock = False
        wm = context.window_manager
        return wm.invoke_popup(self)


class Favorite:

    def execute(self, context):
        import json

        prefs = bpy.context.preferences.addons[var.ADDON_ID].preferences
        favs_filepath = prefs.asset_favs_filepath()

        # Deserialize

        if favs_filepath.exists():
            with open(favs_filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = []

        # Process

        if self.is_add:
            data.append(self.filepath)
            data.sort()
        elif self.filepath in data:
            data.remove(self.filepath)

        # Serialize

        favs_filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(favs_filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        dynamic_list.assets_refresh(favs=True)
        context.area.tag_redraw()

        return {"FINISHED"}


class WM_OT_asset_favorite_add(Favorite, Operator):
    bl_label = "Favorite"
    bl_description = "Add to favorites"
    bl_idname = "wm.jewelcraft_asset_favorite_add"
    bl_options = {"INTERNAL"}

    is_add = True

    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})


class WM_OT_asset_favorite_del(Favorite, Operator):
    bl_label = "Remove"
    bl_description = "Remove from favorites"
    bl_idname = "wm.jewelcraft_asset_favorite_del"
    bl_options = {"INTERNAL"}

    is_add = False

    filepath: StringProperty(options={"SKIP_SAVE", "HIDDEN"})
