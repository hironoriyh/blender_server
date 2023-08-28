import logging
import numpy as np
from numpysocket import NumpySocket
import socket
import bpy, bmesh

def get_nppoints():
    vertices = []
    # obj = bpy.context.objects_in_mode
    # if obj.mode == 'EDIT':
    print(bpy.context.objects_in_mode)
    for o in bpy.context.objects_in_mode:
        bm=bmesh.from_edit_mesh(o.data)
        print(bm)
        for v in bm.verts:
            if v.select:
                vertices.append(v.co)
                # print(v.co)

    vertices = np.array(vertices)
    print("vertices", vertices.shape)
    return vertices

def obj_from_trimesh(mesh):
    # bm = bmesh.new()
    # verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in mesh.vertices]
    # for edge_idxs in skel.edges:
    #     bm.edges.new([verts[edge_idxs[0]], verts[edge_idxs[1]]])

    # # add placeholder
    verts = mesh.vertices.tolist()
    edges = mesh.edges.tolist()
    faces = mesh.faces.tolist()
    me = bpy.data.meshes.new('conmesh')
    me.from_pydata(verts, edges, faces)
    me.update()
    mesh_obj = bpy.data.objects.new('conmesh', me)
    bpy.context.scene.collection.objects.link(mesh_obj)
    # bm.to_mesh(me)
    # bm.free()



logger = logging.getLogger('simple client')
logger.setLevel(logging.INFO)

vertices = get_nppoints()

print("simple np client")
with NumpySocket() as s:
    s.connect(("", 9999)) #it should be "" 
    
    logger.info("sending numpy array:")
    # frame = np.arange(5000)
    s.sendall(vertices)
    res = s.recv()
    mesh = res.tolist()
    print("received", mesh)
    obj_from_trimesh(mesh)
    s.close()



