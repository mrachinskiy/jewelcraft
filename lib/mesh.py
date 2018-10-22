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


import bpy
import bmesh
from mathutils import Matrix


# Primitives
# ---------------------------


def make_rect(bm, x, y, h):
    coords = (
        ( x,  y, h),
        (-x,  y, h),
        (-x, -y, h),
        ( x, -y, h),
    )

    return [bm.verts.new(co) for co in coords]


def make_tri(bm, x, y, h):
    coords = (
        (  x,  y / 3.0, h),
        ( -x,  y / 3.0, h),
        (0.0, -y / 1.5, h),
    )

    return [bm.verts.new(co) for co in coords]


# Tools
# ---------------------------


def est_volume(obs):
    scene = bpy.context.scene
    bm = bmesh.new()

    for ob in obs:
        me = ob.to_mesh(scene, True, "PREVIEW", calc_tessface=False)
        me.transform(ob.matrix_world)

        bm.from_mesh(me)

        bpy.data.meshes.remove(me)

    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=3)

    vol = bm.calc_volume()
    bm.free()

    return vol


def curve_length(ob):
    me = ob.to_mesh(bpy.context.scene, True, "PREVIEW", calc_tessface=False)

    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)

    bpy.data.meshes.remove(me)

    length = 0.0

    for edge in bm.edges:
        length += edge.calc_length()

    bm.free()

    return length


def make_edges(bm, verts):
    edges = []

    for i in range(len(verts) - 1):
        edges.append(bm.edges.new((verts[i], verts[i + 1])))

    edges.append(bm.edges.new((verts[-1], verts[0])))

    return edges


def bridge_verts(bm, v1, v2):
    faces = []
    edges = []

    for i in range(len(v1) - 1):
        f = bm.faces.new([v1[i + 1], v1[i], v2[i], v2[i + 1]])
        faces.append(f)
        edges.append(f.edges[1])

    f = bm.faces.new([v1[0], v1[i + 1], v2[i + 1], v2[0]])
    faces.append(f)
    edges.append(f.edges[1])

    return {"faces": faces, "edges": edges}


def duplicate_verts(bm, verts, z=False):
    dup = bmesh.ops.duplicate(bm, geom=verts)
    verts = [x for x in dup["geom"] if isinstance(x, bmesh.types.BMVert)]

    if z is not False:
        for v in verts:
            v.co[2] = z

    return verts


def duplicate_edges(bm, edges, z=False):
    dup = bmesh.ops.duplicate(bm, geom=edges)
    edges = [x for x in dup["geom"] if isinstance(x, bmesh.types.BMEdge)]

    if z is not False:
        verts = [x for x in dup["geom"] if isinstance(x, bmesh.types.BMVert)]
        for v in verts:
            v.co[2] = z

    return edges


def edge_loop_expand(e, limit=0):
    edges = []
    app = edges.append

    loop = e.link_loops[0]
    loop_next = loop
    loop_prev = loop
    app(e)

    for i in range(1, limit):
        loop_next = loop_next.link_loop_next.link_loop_radial_next.link_loop_next
        loop_prev = loop_prev.link_loop_prev.link_loop_radial_prev.link_loop_prev
        app(loop_next.edge)
        app(loop_prev.edge)

    return edges


def edge_loop_walk(verts):
    v = verts[0]
    e = v.link_edges[1]

    coords = []
    app = coords.append
    app(v.co.copy())

    for i in range(len(verts) - 1):

        ov = e.other_vert(v)
        app(ov.co.copy())
        v = ov

        for oe in ov.link_edges:
            if oe != e:
                e = oe
                break

    return coords


def face_pos():
    scene = bpy.context.scene
    ob = bpy.context.active_object

    # Prepare bmesh
    # --------------------------------

    mods_ignore = [(x, x.show_viewport) for x in ob.modifiers if x.type == "SUBSURF"]

    if mods_ignore:
        for mod, mod_show in mods_ignore:
            mod.show_viewport = False
        scene.update()

    ob.update_from_editmode()
    me = ob.to_mesh(scene, True, "PREVIEW", calc_tessface=False)

    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)

    bpy.data.meshes.remove(me)

    if mods_ignore:
        for mod, mod_show in mods_ignore:
            mod.show_viewport = mod_show

    # Collect transform matrices
    # --------------------------------

    mats = []

    for f in bm.faces:
        if f.select:
            mat_loc = Matrix.Translation(f.calc_center_median())
            mat_rot = f.normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
            mat = mat_loc * mat_rot

            mats.append(mat)

    bm.free()

    return mats
