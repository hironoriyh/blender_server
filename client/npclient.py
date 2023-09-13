import logging
import numpy as np
from numpysocket import NumpySocket
import socket
import bpy, bmesh
# from sample_points import sample_points
import trimesh


def get_nppoints_normals():
    vertices = []
    normals = []
    faces = []
    # obj = bpy.context.objects_in_mode
    # if obj.mode == 'EDIT':
    print("mode:", bpy.context.objects_in_mode)
    for o in bpy.context.objects_in_mode:
        bm =  bmesh.from_edit_mesh(o.data)
        print(bm)
 
        ### ToDo (select mesh -> trimesh -> sample.points)
        # for f in bm.faces:
        #     if f.select:
        #         face = []
        #         faces.append(face)
        #         for vi in f.verts:
        #             face.append(vi.index)

        for v in bm.verts:
            if v.select:
                #vertices.append(o.matrix_world @ v.co)
                vertices.append(o.matrix_world @ v.co)
                normals.append(o.matrix_world @ v.normal)
                # print(v.co)


    faces = np.array(faces) #.astype(np.int32)
    vertices = np.array(vertices)
    normals = np.array(normals)

    ### ToDo (select mesh -> trimesh -> sample.points)
    # mesh = trimesh.Trimesh(vertices=vertices, faces=faces) 
    # points, fids = trimesh.sample.sample_surface(mesh, 1000)
    # normals = my_mesh.face_normals[fids]

    points_normals = np.hstack((vertices, normals))

    print("vertices", points_normals.shape)
    return points_normals

def obj_from_trimesh(mesh):
    # # add placeholder
    verts = mesh.vertices.tolist()
    edges = mesh.edges.tolist()
    faces = mesh.faces.tolist()
    
    me = bpy.data.meshes.new('conmesh')
    # me.from_pydata(verts, edges, faces)
    me.from_pydata(verts, [], faces)


    me.update()
    mesh_obj = bpy.data.objects.new('conmesh', me)
    bpy.context.scene.collection.objects.link(mesh_obj)
    # bm.to_mesh(me)
    # bm.free()



logger = logging.getLogger('numpy client')
logger.setLevel(logging.INFO)

vertices = get_nppoints_normals()

with NumpySocket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect(("", 9999)) ### address should be "" which is 0.0.0.0 
    
    logger.info("sending numpy array:")
    # frame = np.arange(5000)
    s.sendall(vertices) #
    # s.sendall(vertices[:, :3]) #

    res = s.recv()
    mesh = res.tolist()
    print("received", mesh)
    obj_from_trimesh(mesh)
    s.close()



