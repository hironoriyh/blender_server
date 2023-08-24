# blender_server

1. blenderのPythonとリモートともPip install  numpysocket

2. サーバー側のnumpysocket.pyの[sendall()関数のif not isinstance(frame, np.ndarray)]([url](https://github.com/hironoriyh/blender_server/blob/5c8e9c0880028c51ba6d6feacce153ea672663c7/numpysocket.py#L11-L12))
をコメントにする.

3. サーバー側でpython npserver.pyでサーバーをたてる

4. Blender側でEditモードで、複数オブジェクトの点群を選択し、command+shift+P -> run script でnpclient.py

5. Blender上にConmeshが生成される
