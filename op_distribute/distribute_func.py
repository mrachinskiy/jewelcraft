# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

import operator
from typing import Optional
from collections.abc import Iterator

import bpy
from bpy.types import Constraint, Object
from mathutils import Matrix, Vector

from ..lib import mesh, asset, iterutils


def _eq(a: float, b: float) -> bool:
    return abs(a - b) < 1e-6


def _get_obs() -> tuple[Optional[Object], Optional[Object]]:
    ob1, ob2 = bpy.context.selected_objects
    is_curve1 = ob1.type == "CURVE"
    is_curve2 = ob2.type == "CURVE"

    if is_curve1 and is_curve2:
        if ob1 is bpy.context.object:
            return ob1, ob2
        return ob2, ob1

    if is_curve1:
        return ob1, ob2
    if is_curve2:
        return ob2, ob1

    return None, None


def _get_cons() -> Iterator[Constraint]:
    for ob in bpy.context.selected_objects:
        for con in ob.constraints:
            if con.type == "FOLLOW_PATH":
                yield con
                break


def _flatten(iterable: list) -> Iterator[float]:
    for item in iterable:
        for _ in range(item.qty):
            yield item.size


def _hash(iterable: list) -> int:
    return hash(tuple(tuple(item.values()) for item in iterable))


def _deform_redstr(ob: Object, rot_x: float, rot_z: float, loc_z: float) -> None:
    if rot_x:
        ob_mat_rot = ob.matrix_basis.to_quaternion().to_matrix().to_4x4()
        mat_rot = Matrix.Rotation(rot_x, 4, "X")
        ob.matrix_basis @= ob_mat_rot.inverted() @ mat_rot @ ob_mat_rot

    if rot_z:
        mat_rot = Matrix.Rotation(rot_z, 4, "Z")
        ob.matrix_basis @= mat_rot

    if rot_x or loc_z:
        dist = ob.matrix_basis.translation.length
        mat_rot = ob.matrix_basis.to_quaternion().to_matrix()
        ob.matrix_basis.translation = mat_rot @ Vector((0.0, 0.0, dist + loc_z))


def _create_dstr(ob: Object, curve: Object, sizes: list, con_add=True) -> list[tuple[Constraint, float, float]]:
    space_data = bpy.context.space_data
    use_local_view = bool(space_data.local_view)
    ob_colls = ob.users_collection
    child_colls = [(child, child.users_collection) for child in ob.children]

    obs = []
    app = obs.append

    for is_last, size in iterutils.spot_last(_flatten(sizes)):

        if is_last:
            ob_copy = ob
        else:
            ob_copy = ob.copy()

            for coll in ob_colls:
                coll.objects.link(ob_copy)

            if use_local_view:
                ob_copy.local_view_set(space_data, True)

            for child, colls in child_colls:
                child_copy = child.copy()
                for coll in colls:
                    coll.objects.link(child_copy)
                child_copy.parent = ob_copy
                child_copy.matrix_parent_inverse = child.matrix_parent_inverse

        if con_add:
            con = ob_copy.constraints.new("FOLLOW_PATH")
            con.target = curve
            con.use_curve_follow = True
            con.forward_axis = "FORWARD_X"
        else:
            for con in ob_copy.constraints:
                if con.type == "FOLLOW_PATH":
                    break

        scaling = size / ob_copy.dimensions.y

        if not _eq(scaling, 1.0):
            ob_copy.scale *= scaling

        app((con, None, size))

    return obs


def execute(self, context):

    # Set objects
    # ---------------------------

    sizes_list = context.window_manager.jewelcraft.sizes.values()

    if self.is_distribute:

        if not sizes_list:
            return {"FINISHED"}

        curve, ob = _get_obs()

        curve.select_set(False)
        context.view_layer.objects.active = ob

        mat_sca = Matrix.Diagonal(ob.scale).to_4x4()
        ob.matrix_world = mat_sca

        if self.rot_x:
            mat_rot = Matrix.Rotation(self.rot_x, 4, "X")
            ob.matrix_world @= mat_rot

        if self.rot_z:
            mat_rot = Matrix.Rotation(self.rot_z, 4, "Z")
            ob.matrix_world @= mat_rot

        if self.loc_z:
            mat_loc = Matrix.Translation((0.0, 0.0, self.loc_z))
            ob.matrix_world @= mat_loc

        obs = _create_dstr(ob, curve, sizes_list)

    elif self.hash_sizes != _hash(sizes_list):

        for is_last, con in iterutils.spot_last(list(_get_cons())):
            ob = con.id_data

            if not is_last:

                for child in ob.children:
                    bpy.data.objects.remove(child)

                bpy.data.objects.remove(ob)

        context.view_layer.objects.active = ob
        curve = con.target

        _deform_redstr(ob, self.rot_x, self.rot_z, self.loc_z)
        obs = _create_dstr(ob, curve, sizes_list, con_add=False)

    else:

        obs = []
        app = obs.append

        for con in _get_cons():
            ob = con.id_data
            _deform_redstr(ob, self.rot_x, self.rot_z, self.loc_z)
            app((con, con.offset, ob.dimensions.y))

        obs.sort(key=operator.itemgetter(1), reverse=True)

        con = obs[0][0]
        curve = con.target

    curve.data.use_radius = False
    asset.apply_scale(curve)

    # Offset values
    # ---------------------------

    start = self.start
    end = self.end

    if not self.use_absolute_offset:
        ofst = 0.0
        num = len(obs)

        if num > 1:
            closed_distribution = round(end - start, 1) == 100.0

            if self.cyclic and closed_distribution:
                ofst = (end - start) / num
            else:
                if not self.cyclic:
                    start = max(start, 0.0)
                    end = min(end, 100.0)
                ofst = (end - start) / (num - 1)

    # Distribute
    # ---------------------------

    ofst_fac = start
    size_prev = 0.0
    consecutive_cycle = False

    for con, _, size in obs:

        if self.use_absolute_offset:
            ofst = self.base_unit * ((size + size_prev) / 2 + self.spacing)
            size_prev = size

        if consecutive_cycle:
            ofst_fac += ofst
        else:
            consecutive_cycle = True

        con.offset = -ofst_fac

    return {"FINISHED"}


def invoke(self, context, event):
    wm = context.window_manager
    sizes = wm.jewelcraft.sizes

    if self.is_distribute:

        if len(context.selected_objects) != 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}

        curve, ob = _get_obs()

        if curve is None:
            self.report({"ERROR"}, "Active object must be a curve")
            return {"CANCELLED"}

        self.cyclic = curve.data.splines[0].use_cyclic_u
        self.base_unit = 100.0 / mesh.est_curve_length(curve)

        if not event.ctrl or not sizes.length():
            sizes.clear()
            item = sizes.add()
            item.qty = 10
            item.size = ob.dimensions.y

        wm.invoke_props_popup(self, event)
        return self.execute(context)

    obs = []
    app = obs.append
    curve = None

    for con in _get_cons():
        ob = con.id_data
        curve = con.target
        app((-con.offset, ob.dimensions.y))

    if curve is None:
        self.report({"ERROR"}, "Selected objects do not have Follow Path constraint")
        return {"CANCELLED"}

    obs.sort(key=operator.itemgetter(0))
    prev_size = -1.0
    sizes.clear()

    for _, size in obs:

        if _eq(size, prev_size):
            item.qty += 1
        else:
            item = sizes.add()
            item.qty = 1
            item.size = size

        prev_size = size

    self.use_absolute_offset = sizes.length() > 1
    self.start = obs[0][0]
    self.end = obs[-1][0]
    self.cyclic = curve.data.splines[0].use_cyclic_u
    self.base_unit = 100.0 / mesh.est_curve_length(curve)
    self.hash_sizes = _hash(sizes.values())

    if len(obs) > 1:
        if self.use_absolute_offset:
            ofst1, size1 = obs[0]
            ofst2, size2 = obs[1]
            self.spacing = (ofst2 - ofst1) / self.base_unit - (size1 + size2) / 2
        elif self.cyclic:
            ofst_1 = obs[0][0]
            ofst_n1 = obs[-1][0]
            ofst_n2 = obs[-2][0]
            ofst_n = round(ofst_n1 + (ofst_n1 - ofst_n2), 2)
            if (ofst_n - 100.0) == ofst_1:
                self.end = ofst_n

    return wm.invoke_props_popup(self, event)
