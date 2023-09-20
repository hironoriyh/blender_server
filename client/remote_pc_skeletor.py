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
    # mat = selected_obj.matrix_world
    for i in verts_ind :
        local_co = selected_obj.data.vertices[i].co
                # local_co = selected_obj.matrix_world @ selected_obj.data.vertices[i].co
        vertices.append(local_co[:])
    
    print(selected_obj.matrix_world)

    msh.free()

    vertices = np.array(vertices)
    randidx = np.random.choice(vertices.shape[0], 2000, replace=False)
    # normals = np.array(normals)

    # points_normals = np.hstack((vertices, normals))

    print("vertices orginal ", vertices.shape , "reduced:", randidx.shape)
    return vertices[randidx, :]
    # return vertices

def polyline(skel, edges, objname):
    ## adding polyline
    bm = bmesh.new()
    verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in skel]
    
    for edge_idxs in edges:
        bm.edges.new([verts[edge_idxs[0]], verts[edge_idxs[1]]])

    me = bpy.data.meshes.new('polyskel')
    mesh_obj = bpy.data.objects.new(objname + '_polyskel', me)
    # scene.collection.objects.link(mesh_obj)
    bpy.data.collections["skeletons"].objects.link(mesh_obj)

    bm.to_mesh(me)
    bm.free()

def normalize_pcd(input_pcd):
    #center
    center = input_pcd.mean(axis=0)
    input_pcd_trans = input_pcd - center

    scale = 2/(input_pcd_trans.max(axis=0) - input_pcd_trans.min(axis=0)).max()
    input_pcd_trans = input_pcd_trans * scale
    # input_mesh.apply_scale(scale)
    # center = input_mesh.centroid
    # input_mesh.apply_translation(-center)
    # input_pc = torch.tensor(input_mesh.vertices).cuda().float().unsqueeze(axis=0)
    return input_pcd_trans, center, scale

def retrans_rescale(input_pcd, center, scale):
    input_pcd += center
    input_pcd *= 1/scale
    return input_pcd

def points(skel, objname, mat):
    ## adding polyline
    bm = bmesh.new()
    verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in skel]

    me = bpy.data.meshes.new('skelpts')
    mesh_obj = bpy.data.objects.new(objname + '_skelpts', me)
    mesh_obj.matrix_world = mat
    # scene.collection.objects.link(mesh_obj)
    bpy.data.collections["skelpts"].objects.link(mesh_obj)

    bm.to_mesh(me)
    bm.free()

    print("new points were created")




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
                mat = obj.matrix_world

                print("name", objname, mat)
                vertices = get_nppoints(obj)
                vertices_normalized, center, scale = normalize_pcd(vertices)
                print("get nppoints", vertices_normalized.shape, "center", center, "scale", scale)
                # import ipdb; ipdb.set_trace()

                
                logger.info("sending numpy array:")
                # frame = np.arange(5000)
                s.sendall(vertices_normalized) #
                # s.sendall(vertices[:, :3]) #

                res = s.recv()
                # import ipdb;ipdb.set_trace()

                skel = res[0]
                edges = res[1]
                print(skel.max(axis=0)-skel.max(axis=0))
                # print(skel.shape, edges.shape)
                # skel = res.tolist()
                skel = retrans_rescale(skel, center, scale)
                if edges is not None:
                    polyline(skel, edges, objname)
                else:
                    points(skel, objname, mat)
                s.close()

            except: #KeyboardInterrupt:
                s.close()
                print('socket is closed')
