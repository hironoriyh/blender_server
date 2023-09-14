### two points are selected in edit mode

import numpy as np
import bpy
import bmesh
import copy
from mathutils import Vector


# dic_v = {}

def create_curve(coords_list):
    crv = bpy.data.curves.new('crv', 'CURVE')
    crv.dimensions = '3D'
    spline = crv.splines.new(type='NURBS')
    spline.points.add(len(coords_list) - 1) 
    for p, new_co in zip(spline.points, coords_list):
        p.co = (new_co + [1.0])  # (add nurbs 
    obj = bpy.data.objects.new('object_name', crv)
    bpy.data.scenes[0].collection.objects.link(obj)

def collect_verts():
    verts = []
    bm_joint = bmesh.new()
    if(bpy.context.mode != "EDIT_MESH"):
        print("not edit mode!")
        exit()

    for o in bpy.context.objects_in_mode:
        print(o.name)
        bm = bmesh.from_edit_mesh(o.data)
        for v in bm.verts:

            if v.select and len(v.link_edges) is 1: ### check it's selected and edge node
                new_v = bm_joint.verts.new(v.co)
                verts.append(new_v)

                # get the other verts
                print("selected vert", v.index, len(v.link_edges))
                for e in v.link_edges:
                    v_other = bm_joint.verts.new(e.other_vert(v).co)
                    # print("bmedge other vert", v_other.index, )
                    bm_joint.edges.new([new_v, v_other]) #v.link_edges)
    return verts, bm_joint


def connect_verts(verts, bm_joint):
    ### create new point
    verts_sel = [v.co for v in verts]
    # print("loc", loc)
    # if loc:
    pivot = sum(verts_sel, Vector()) / len(verts_sel)
    print("average", pivot)
    center_v = bm_joint.verts.new(pivot)

    ### create new edgen

    # bm_joint.edges.new([verts[0], verts[1]])

    # # print(verts)
    for v in verts:
        bm_joint.edges.new([v, center_v])
        bm_joint.edges.ensure_lookup_table()
        bm_joint.edges[-1].index = 1
    # import ipdb; ipdb.set_trace()

    bmesh.ops.subdivide_edges(bm_joint,
                            edges= [edge for edge in bm_joint.edges if edge.index==1], #[bm_joint.edges[-1]], ## select only the last edge
                            smooth=10,
                            cuts=10,   
                            # use_smooth_even = True, 
                            )

    me = bpy.data.meshes.new("joint")
    mesh_obj = bpy.data.objects.new("jointobj", me)
    
    bpy.context.scene.collection.objects.link(mesh_obj)

    bm_joint.to_mesh(me)   
    bm_joint.free()
    # return True


verts, bm_joint = collect_verts()
#print(verts)   
connect_verts(verts, bm_joint)
print("done")

# then later on
# for o in bms:
#     for v in bms[o].verts:
#         print(f"{o.name} - {v.index}, {v.co}")