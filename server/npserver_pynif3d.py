#!/usr/bin/python3
import torch
import numpy as np
import logging
from numpysocket import NumpySocket
import socket
from types import SimpleNamespace
from test import const_model, calc_occu, mesh_export

logger = logging.getLogger('numpy server')
logger.setLevel(logging.INFO)

def calc_mesh(frame):
    args = SimpleNamespace(grid_dims=32, 
                        n_levels=4, outfilename=None, 
                        pointcloud_filename='plys/20230714/testjointedge_4parts.ply', 
                        steps=100, threshold=0.2)
    if frame.shape[-1] == 6:
        print("normal!")
        args.normal = True
        args.model_file='experiment/trees_raysampled_match_normal/model90000_32.pt'

    else:
        args.normal = False
        # args.model_file='experiment/trees_raysampled_match/model50000_32.pt'
        # args.model_file='experiment/trees_raysampled_match/model30000_32.pt'
        args.model_file='experiment/trees_raysampled_match/model90000_32.pt'
        # args.model_file='experiment/trees_raysampled_match/model290000_32.pt'


    print("normal", args.normal)

    data = torch.load(args.model_file)
    state_dict = data["model_state"]
    device = None
    if torch.cuda.is_available():
        device = torch.cuda.current_device()
    model = const_model(state_dict, args).to(device)
    model.train(False)

    # import ipdb; ipdb.set_trace()
    frame = frame[np.newaxis, :, :]
    frame = torch.tensor(frame, dtype=torch.float32)
    if(args.normal):
        in_points = frame[:,:, :3].to(device)
        in_normals = frame[:,:, 3:6].to(device)
        print(in_points.shape, in_normals.shape)
    else:
        in_points = frame.to(device)
        in_normals = None

    try:
        prediction, steps, scale, middle = calc_occu(in_points, in_normals, model, device, args)
        mesh, filename_mesh  = mesh_export(prediction, steps, scale, middle, args)
        print(mesh)

    except Exception as e:
        print(e)
        mesh = None
    
    return mesh 


with NumpySocket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 9999))
    s.listen()

    try:
        while True :
            print('Wait tcp accepting...')
            conn, addr = s.accept()
            with conn:
                logger.info(f"connected: {addr}")
                frame = conn.recv()

                logger.info("array received")
                # logger.info(frame)
                
                mesh = calc_mesh(frame)
                # import ipdb; ipdb.set_trace()
                print(mesh.vertices.shape, mesh.faces.shape)
                # conn.sendall([mesh.vertices, mesh.faces])
                if mesh is not None:
                    conn.sendall(mesh)

                conn.close()

    except: # KeyboardInterrupt:
        s.close()
        print('socket is closed')

    logger.info(f"disconnected: {addr}")
