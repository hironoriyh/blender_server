import logging
import numpy as np
from numpysocket import NumpySocket
import socket
import bpy, bmesh
# from sample_points import sample_points
import trimesh


def get_nppoints(selected_obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    msh = bmesh.new() 

    msh.from_object(selected_obj, depsgraph)

    verts = msh.verts     # verts = msh.vertices
    verts_ind = [i.index for i in selected_obj.data.vertices]
    vertices = []
    # vertex_normals = []
    for i in verts_ind :
        local_co = selected_obj.matrix_world @ selected_obj.data.vertices[i].co
        vertices.append(local_co[:])

    msh.free()

    vertices = np.array(vertices)
    # normals = np.array(normals)

    # points_normals = np.hstack((vertices, normals))

    print("vertices", vertices.shape)
    return vertices

def polyline(skel, edges, objname):
    ## adding polyline
    bm = bmesh.new()
    verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in skel]
    for edge_idxs in edges:
        bm.edges.new([verts[edge_idxs[0]], verts[edge_idxs[1]]])

    # add placeholder
    scene = bpy.context.scene 
    meshes = bpy.data.meshes
    objects = bpy.data.objects

    me = meshes.new('polyskel')
    mesh_obj = objects.new(objname + '_polyskel', me)
    # scene.collection.objects.link(mesh_obj)
    bpy.data.collections["skeletons"].objects.link(mesh_obj)

    bm.to_mesh(me)
    bm.free()



logger = logging.getLogger('numpy client')
logger.setLevel(logging.INFO)

selected_objs = bpy.context.selected_objects
if selected_objs is not None:
    print(len(selected_objs), "are selected")
    if  bpy.data.collections.find("skeletons") is -1:
        skel_coll = bpy.data.collections.new("skeletons")
        bpy.context.scene.collection.children.link(skel_coll)
    else:
        logger.warn("skeletons coll was found!")


    for obj in selected_objs:
        with NumpySocket() as s:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect(("", 9999)) ### address should be "" which is 0.0.0.0 
                
                objname = obj.name
                print("name", objname)
                vertices = get_nppoints(obj)
                print("get nppoints", vertices.shape)

                
                logger.info("sending numpy array:")
                # frame = np.arange(5000)
                s.sendall(vertices) #
                # s.sendall(vertices[:, :3]) #

                res = s.recv()
                skel = res[0]
                edges = res[1]
                print(skel.shape, edges.shape)
                # skel = res.tolist()
                polyline(skel, edges, objname)
                s.close()

            except: #KeyboardInterrupt:
                s.close()
                print('socket is closed')
