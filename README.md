# CLO3DOBJ to VirtualTryOn


## 概要
CLO3D / MDから出力した服OBJに対して最適化処理をしてfbxとして出力する  
対象のobjをVRC規定のディレクトリ構造、命名規則で検索して一括で実行する

<br>

## ツール構成
`run_clo3dobj_to_vtryon.bat`を利用してツールを実行する。  
`settings.json`を変更することでツール実行動作を一部変更できる。  
logsフォルダ下には、実行log fileが日ごとに生成される。  

    clo3dobj_to_virtualtryon.  
    ├─logs ★  
    │  ├─yymmdd_hhmmss-clo3dobj_to_vtryon.log  
    │  ├─yymmdd_hhmmss-clo3dobj_to_vtryon.log  
    │  └─...  
    ├─resources  
    ├─scripts  
    ├─settings  
    │  └─settings.json ★  
    ├─Readme.html  
    └─run_clo3dobj_to_vtryon.bat ★  

<br>

## 使用方法
1. `run_clo3dobj_to_vtryon.bat` を起動する
2. ポップアップしたコマンドラインに対象の親ディレクトリ（ClothesとCoordが格納されたディレクトリ）を入力 or ドラッグ＆ドロップする
3. Enterで実行すると、ディレクトリ内の対象objに対して設定及びfbx出力を一括でおこなう

<br>

## input objの条件
- `ClothesId_master.zpac`から出力されたデータであること
- 生地ごとにmaterialが設定されており、material数が23以下である
- CLO/MD出力設定：obj, cm(DAZ)100%, UnifiedUVLayout
- objファイル名はClothesId.obj（ex. 0001ft）であること
- VRC規定のディレクトリ構造でデータが格納されていること

<br>

## 処理の内容
- `Clothes/*ClothesId*/1.result/fbx/` 内の`ClohtesId.obj`を全て処理する
- `Coord/*CoordId*/1.result/fbx/` 内の`ClohtesId.obj`を全て処理する
- Object名、Meshdata名をClothesIdに設定する
- Materialを1つに統合し、ClothesType（M_top, M_bottom, M_dress, M_outer）に設定する
- CLO3D出力時のMaterialごとにvertex colorを設定する
- scaleを0.01倍に調整する
- 男性服の場合は女性服の大きさに統一するためscaleを変更する（* 女性標準アバター身長 / 男性標準アバター身長）
- 重複頂点を削除して法線を再計算する
- fbxとしてexportする
- 元のobj及びmtlファイルを削除することも可能（setting.json / delete_obj_mtl=trueの場合）

<br>

## 設定（settings.jsonで変更）
| key               | item          | desc |
| ----              | ----          | ---- |
| overwrite_fbx     | true or false | fbxがすでに存在する場合に上書き更新するか / true → 上書きする, false → 処理をスキップする |
| delete_obj_mtl    | true or false | objとmtlファイルを削除するか / true → 削除する, false → 削除しないで残す |

<br>

## 動作環境
windows10 / 11


<br>
<br>

> clo3d_to_virtualtryon_v2.0.1  
2023/01/29  
VRC Inc.    
Naoto SHIGENOBU  
naoto.shigenobu@vrcjp.com