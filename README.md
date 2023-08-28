# blender_server

1. blenderのPythonとリモートともPip install  numpysocket

2. サーバー側のnumpysocket.pyの[sendall()関数のif not isinstance(frame, np.ndarray)]([url](https://github.com/hironoriyh/blender_server/blob/5c8e9c0880028c51ba6d6feacce153ea672663c7/numpysocket.py#L11-L12))
をコメントにする.

3. サーバー側でpython npserver.pyでサーバーをたてる

4. Blender側で**Editモード**で対象オブジェクトのFacesを選択し、npclient.pyでServerにデータ送信. <img width="373" alt="image" src="https://github.com/hironoriyh/blender_server/assets/11435308/98d4f2c2-c699-4c96-b3d6-2788ba65c71d">
<!-- 5. sample_points.pyで点群生成する。 --> 
<!-- 6. Blender側でEditモードで、生成した複数オブジェクトの点群を選択し、command+shift+P -> run script でnpclient.py -->

7. Blender上にConmeshが生成される

--------(optional) -----------
1. skeletonize.pyで選択したオブジェクトのスケルトンを生成する。
2. スケルトンの端点同士をEdit modeで選択し、connect_lines.pyでスケルトンをつなげる。
3. (ToDo) 生成したスケルトンで点群を生成する
4. (ToDo) 点群からメッシュ生成



