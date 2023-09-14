# blender_server

1. blenderのPythonとリモートともnumpysocket.pyをコピペしておく。 (3DOAEはnumpysocket.py)

2. (optional もし1.を実行しておくと必要なし) サーバー側のnumpysocket.pyの[sendall()関数のif not isinstance(frame, np.ndarray)]([url](https://github.com/hironoriyh/blender_server/blob/5c8e9c0880028c51ba6d6feacce153ea672663c7/numpysocket.py#L11-L12))
をコメントにする.

3. サーバー側でserver/**/npserver**.py を追加し、python npserver**.pyでサーバーをたてる

4. サーバー側のlocalhost 9999をポートフォワードしておく。これがないとSocket通信できないので注意。

## Pynif3Dの使い方
1. Blender側で対象オブジェクトを選択し、client/remote_pynif3d.pyでServerにデータ(点群)を送信. 
<!-- 5. sample_points.pyで点群生成する。 --> 
<!-- 6. Blender側でEditモードで、生成した複数オブジェクトの点群を選択し、command+shift+P -> run script でnpclient.py -->
2. Blender上にConmeshが生成される

## pc-skeletorの使いかた
1. Blender側で対象オブジェクトを選択(**複数可**)し、client/remote_pc_skeletor.pyでServerにデータ(点群)を送信. 
2. Blender上にSkeletonが生成される
3. Blender側で対象スケルトンの端の複数点、および複数スケルトンを選択し、client/connect_lines.pyを実行すると、ジョイントスケルトンができる。

## 3D-OAEの使い方
1. Blender側で対象オブジェクトを選択(**複数可**)し、client/remote_pc_skeletor.pyでServerにデータ(点群)を送信. 
2. Blender上にskel(点群のみ), sparse点群が生成される

--------(optional) -----------
1. skeletonize.pyで選択したオブジェクトのスケルトンを生成する。
2. スケルトンの端点同士をEdit modeで選択し、connect_lines.pyでスケルトンをつなげる。
3. (ToDo) 生成したスケルトンで点群を生成する
4. (ToDo) 点群からメッシュ生成



