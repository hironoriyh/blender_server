
import bpy
import trimesh
import bmesh
import numpy as np

def get_trimesh(selected_obj):
    
    depsgraph = bpy.context.evaluated_depsgraph_get()

    msh = bmesh.new() 
    msh.from_object(selected_obj, depsgraph)
    # print(msh.name)

    faces = []
    print("num of polygons:", len(msh.faces))
    for pl in msh.faces:     # for pl in msh.polygons:
        face = []
        faces.append(face)
        for vi in pl.verts:
            face.append(vi.index)
        
    faces = np.array(faces).astype(np.int32)
    print("faces", faces.shape, faces.max())

    verts_ind = [i.index for i in selected_obj.data.vertices]
    vertices = []
    for i in verts_ind :
        local_co = selected_obj.matrix_world @ selected_obj.data.vertices[i].co
        vertices.append(local_co[:])

    vertices = np.array(vertices)
    print(vertices.shape, len(verts_ind))
    msh.free()

    ### sampling points
    #mesh = trimesh.Trimesh(vertices=vertices, faces=faces) #, vertex_normals=vertex_normals) #face_normals=face_normals) #
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces) 
    # print(mesh)
    return mesh


def sample_points(mesh, objname):
    points, idxs = trimesh.sample.sample_surface(mesh, 1000)
    bm = bmesh.new()
    verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in points]

    me = bpy.data.meshes.new('sampled_points')
    mesh_obj = bpy.data.objects.new(objname + 'sampled_points', me)
    bpy.context.scene.collection.objects.link(mesh_obj)
    bm.to_mesh(me)
    bm.free()

    
selected_obj = bpy.context.view_layer.objects.active
print(selected_obj.name)
mesh = get_trimesh(selected_obj)
sample_points(mesh, selected_obj.name)
