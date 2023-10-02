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
    # import ipdb;ipdb.set_trace()

    msh.free()

    vertices = np.array(vertices)
    # if(vertices.shape[0] > 2200*6):
    #     randidx = np.random.choice(vertices.shape[0], 2200*6, replace=False)
    #     vertices =  vertices[randidx, :]

    randidx = np.random.choice(vertices.shape[0], 2000, replace=False)
    vertices =  vertices[randidx, :]
    # normals = np.array(normals)
    # points_normals = np.hstack((vertices, normals))
    # print("vertices orginal ", vertices.shape , "reduced:", randidx.shape)
    return vertices

def normalize_pcd(input_pcd):
    #center
    center = input_pcd.mean(axis=0)
    input_pcd_trans = input_pcd - center

    scale = 1/(input_pcd_trans.max(axis=0) - input_pcd_trans.min(axis=0)).max()
    input_pcd_trans = input_pcd_trans * scale
    # input_mesh.apply_scale(scale)
    # center = input_mesh.centroid
    # input_mesh.apply_translation(-center)
    # input_pc = torch.tensor(input_mesh.vertices).cuda().float().unsqueeze(axis=0)
    return input_pcd_trans, center, scale

def retrans_rescale(input_pcd, center, scale):
    input_pcd *= 1/scale
    input_pcd += center
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


def polyline(skels, A_final, objname, mat, center, scale):
    bm = bmesh.new()
    for i in range(skels.shape[0]):
        ## adding polyline
        skel = retrans_rescale(skels[i], center, scale)
        verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in skel]

        # for i in range(batch_size):
        for j in range(skels.shape[1]):
            for k in range(j + 1, skels.shape[1]):
                if A_final[i][j][k] == 1:
                    bm.edges.new([verts[j], verts[k]])


    me = bpy.data.meshes.new('polyskel')
    mesh_obj = bpy.data.objects.new(objname + '_polyskel', me)
    # scene.collection.objects.link(mesh_obj)
    mesh_obj.matrix_world = mat
    bpy.data.collections["skeletons"].objects.link(mesh_obj)

    bm.to_mesh(me)
    bm.free()

    print("new skels were created")

logger = logging.getLogger('numpy client')
logger.setLevel(logging.INFO)


selected_objs = bpy.context.selected_objects
if selected_objs is not None:
    print(len(selected_objs), "are selected")
    if  bpy.data.collections.find("skelpts") is -1:
        skel_coll = bpy.data.collections.new("skelpts")
        bpy.context.scene.collection.children.link(skel_coll)
    else:
        logger.warn("skelpts coll was found!")

    
    for obj in selected_objs:
        with NumpySocket() as sock:
            try:
                # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect(("", 9999)) ### address should be "" which is 0.0.0.0 
                
                objname = obj.name
                mat = obj.matrix_world

                print("name", objname)
                vertices = get_nppoints(obj)
                vertices_normalized, center, scale = normalize_pcd(vertices)
                print("get nppoints", vertices_normalized.shape, "center", center, "scale", scale)
                # import ipdb; ipdb.set_trace()

                
                logger.info("sending numpy array:", vertices_normalized.shape)
                # frame = np.arange(5000)

                sock.sendall(vertices_normalized) #
                # s.sendall(vertices[:, :3]) #

                res = sock.recv()
                print("shape of res", res.shape)

                # skel = res.reshape(-1,3) #res[0]
                # import ipdb;ipdb.set_trace()

                skels = res[:,:,:3]
                A_final = res[:,:,3:]

                print(skels.shape, A_final.shape)
                if A_final is not None:
                    polyline(skels, A_final, objname, mat, center, scale)
                # else:
                # points(skel, objname, mat)
                sock.close()

            except: #KeyboardInterrupt:
                sock.close()
                print('socket is closed')
