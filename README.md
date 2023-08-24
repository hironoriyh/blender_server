# blender_server

1. blenderのPythonとリモートともPip install  numpysocket

2. サーバー側のnumpysocket.pyのsendall()関数のif not isinstance(frame, np.ndarray)
をコメントにする.

3. サーバー側でpython npserver.pyでサーバーをたてる

4. Blender側でEditモードで、複数オブジェクトの点群を選択し、command+shift+P -> run script でnpclient.py

5. Blender上にConmeshが生成される
