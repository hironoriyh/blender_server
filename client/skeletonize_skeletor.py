import numpy as np
import bpy
import trimesh
import skeletor as sk
import bmesh

# print(bpy.data.objects.keys())

def skeltonize(selected_obj, step_size=30, exportmesh=False, makesphere=False):

    depsgraph = bpy.context.evaluated_depsgraph_get()

    msh = bmesh.new() 
    msh.from_object(selected_obj, depsgraph)
    # msh.verts.ensure_lookup_table()
    # msh.faces.ensure_lookup_table()
    # print(msh.name)

    faces = []
    face_normals = []
    print("num of polygons:", len(msh.faces))
    for pl in msh.faces:     # for pl in msh.polygons:
        # print("polygon index:{0:2} ".format(pl.index), end="")
        # print("vertices:", end="")
        face = []
        faces.append(face)
        face_normals.append(pl.normal[:])
        for vi in pl.verts:
            #verprint("{0:2}, ".format(vi), end="")
            face.append(vi.index)
        
    faces = np.array(faces).astype(np.int32)
    face_normals = np.array(face_normals)
    print("faces", faces.shape, "face_normals", face_normals.shape)
    #print(faces)

    verts = msh.verts     # verts = msh.vertices
    verts_ind = [i.index for i in selected_obj.data.vertices if i.select]
    vertices = []
    vertex_normals = []
    for i in verts_ind :
        local_co = selected_obj.matrix_world @ selected_obj.data.vertices[i].co
        vertices.append(local_co[:])

    msh.free()
    #print(len(verticies))
    vertices = np.array(vertices)
    vertex_normals = np.array(vertex_normals)
    print(vertices.shape, vertex_normals.shape)

    ### skeletonize
    #mesh = trimesh.Trimesh(vertices=vertices, faces=faces) #, vertex_normals=vertex_normals) #face_normals=face_normals) #
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces) 
    print(mesh)

    fixed = sk.pre.fix_mesh(mesh, remove_disconnected=5, inplace=False)
    if( int(vertices.shape[0]/3800) < 10 ):
        step_size = 20
    else:
        step_size = int(vertices.shape[0]/3800)
    
    print("step size:", step_size)
    skel = sk.skeletonize.by_wavefront(fixed, waves=1, step_size=step_size)
    objname = bpy.context.view_layer.objects.active.name

    if(exportmesh):
        mesh.export("/Users/hyoshida/Library/CloudStorage/GoogleDrive-hironoriyh@gmail.com/My Drive/02_experiments/20230818_test_joint_2/test.obj")

    if(makesphere):
        # collection 
        # coll = bpy.ops.collection.create(name="skelton_"+bpy.context.view_layer.objects.active.name)
        coll = bpy.data.collections.new(objname + "_spheres")
        bpy.context.scene.collection.children.link(coll)

        ### adding spheres
        for loc in skel.vertices:
            bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, location = loc)
            obj = bpy.context.active_object
            bpy.ops.collection.objects_remove_all()
            coll.objects.link(obj)

    return skel, objname

def polyline(skel, objname):
    ## adding polyline
    bm = bmesh.new()
    verts = [bm.verts.new((vt[0], vt[1], vt[2])) for vt in skel.vertices]
    for edge_idxs in skel.edges:
        bm.edges.new([verts[edge_idxs[0]], verts[edge_idxs[1]]])

    # add placeholder
    scene = bpy.context.scene 
    meshes = bpy.data.meshes
    objects = bpy.data.objects

    me = meshes.new('polyskel')
    mesh_obj = objects.new(objname + 'polyskel', me)
    scene.collection.objects.link(mesh_obj)

    bm.to_mesh(me)
    bm.free()


try:
    selected_obj = bpy.context.view_layer.objects.active
    skel, objname = skeltonize(selected_obj)
    polyline(skel, objname)
    print(skel)
except:
    print("nothing is selected")
    




