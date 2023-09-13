### two points are selected in edit mode

import numpy as np
import bpy
import bmesh
import copy


# dic_v = {}
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
            if v.select:
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
    ### create new edge

    # # print(verts)
    bm_joint.edges.new([verts[0], verts[1]])
    bm_joint.edges.ensure_lookup_table()
    bmesh.ops.subdivide_edges(bm_joint,
                            edges= [bm_joint.edges[-1]], ## select only the last edge
                            cuts=3,
                            use_smooth_even = True
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
