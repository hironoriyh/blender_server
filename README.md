# blender_server

1. blenderのPythonとリモートともPip install  numpysocket

2. サーバー側のnumpysocket.pyの[sendall()関数のif not isinstance(frame, np.ndarray)]([url](https://github.com/hironoriyh/blender_server/blob/5c8e9c0880028c51ba6d6feacce153ea672663c7/numpysocket.py#L11-L12))
をコメントにする.

3. サーバー側でpython npserver.pyでサーバーをたてる

4. Blender側で対象オブジェクトを選択し、sample_points.pyで点群生成する。 

5. Blender側でEditモードで、生成した複数オブジェクトの点群を選択し、command+shift+P -> run script でnpclient.py

6. Blender上にConmeshが生成される

--------(optional) -----------
1. skeletonize.pyで選択したオブジェクトのスケルトンを生成する。
2. スケルトンの端点同士をEdit modeで選択し、connect_lines.pyでスケルトンをつなげる。
3. (ToDo) 生成したスケルトンで点群を生成する
4. (ToDo) 点群からメッシュ生成
