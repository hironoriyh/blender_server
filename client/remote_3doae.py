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
        # local_co = selected_obj.matrix_world @ selected_obj.data.vertices[i].co
        local_co = selected_obj.data.vertices[i].co
        vertices.append(local_co[:])

    msh.free()

    vertices = np.array(vertices)
    # normals = np.array(normals)

    # points_normals = np.hstack((vertices, normals))

    return vertices

def nppts2obj(nppts, transmat, objname):
    bm = bmesh.new()
    verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in nppts]
    # for edge_idxs in skel.edges:
    #     bm.edges.new([verts[edge_idxs[0]], verts[edge_idxs[1]]])

    # add placeholder
    me = bpy.data.meshes.new('3doae_pts')
    mesh_obj = bpy.data.objects.new(objname + str(nppts.shape[0]), me)
    mesh_obj.matrix_world = transmat
    bpy.context.scene.collection.objects.link(mesh_obj)

    bm.to_mesh(me)
    bm.free()

def scale_trans(input_pcd):
    #center
    center = input_pcd.mean(axis=0)
    input_pcd_trans = input_pcd - center
    scale = 1/(input_pcd_trans.max(axis=0) - input_pcd_trans.min(axis=0)).max()
    input_pcd_trans = input_pcd * scale
    return input_pcd_trans, center, scale

logger = logging.getLogger('numpy client for 3doae')
logger.setLevel(logging.INFO)

selected_objs = bpy.context.selected_objects
bpy.ops.object.origin_set(
    type='ORIGIN_GEOMETRY',
    center='MEDIAN'
)

if selected_objs is not None:
    logger.info(len(selected_objs), "are selected")

    for obj in selected_objs:
        with NumpySocket() as s:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect(("", 9999)) ### address should be "" which is 0.0.0.0 
                
                objname = obj.name
                logger.info("name", objname)
                vertices = get_nppoints(obj)
                logger.info("sending vertices:", vertices.shape)

                trans_scale_vertices, center, scale = scale_trans(vertices)
                print("center:", center, "scale:", scale)
                # import ipdb; ipdb.set_trace()

                s.sendall(vertices) #
                # s.sendall(vertices[:, :3]) #

                ret = s.recv()
                coarse = ret[0]
                dense = ret[1]
                skel = ret[2]
                # logger.info(skel.shape, edges.shape)
                transmat = obj.matrix_world.copy()
                nppts2obj(skel, transmat, objname + "_skel")
                nppts2obj(dense, transmat, objname + "_dense")
                nppts2obj(coarse, transmat,  objname + "_coarse")

                s.close()
                logger.info("done")

            except: #KeyboardInterrupt:
                s.close()
                logger.warn('socket is closed')
