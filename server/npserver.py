#!/usr/bin/python3
import torch
import numpy as np
import logging
from numpysocket import NumpySocket
from types import SimpleNamespace
from test import const_model, calc_occu, mesh_export

logger = logging.getLogger('simple server')
logger.setLevel(logging.INFO)

def calc_mesh(frame):
    args = SimpleNamespace(grid_dims=32, 
                        model_file='experiment/trees_raysampled_match/model50000_32.pt', 
                        n_levels=4, outfilename=None, 
                        pointcloud_filename='plys/20230714/testjointedge_4parts.ply', 
                        steps=100, threshold=0.2)

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
    in_points = frame.to(device)
    prediction, steps, scale, middle = calc_occu(in_points, model, device, args)
    mesh, filename_mesh  = mesh_export(prediction, steps, scale, middle, args)
    print(mesh)
    return mesh


with NumpySocket() as s:
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
                conn.sendall(mesh)

                conn.close()

    except KeyboardInterrupt:
        print('Finished!')

    logger.info(f"disconnected: {addr}")
