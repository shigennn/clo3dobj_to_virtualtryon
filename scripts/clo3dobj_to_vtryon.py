import bpy
import json, os, sys
from logging import DEBUG, INFO

# load external module
from sys import path
path.append(os.path.basename(bpy.data.filepath))
from utils import get_root_logger, get_ext
from editor import initialize
from importer import import_model
from exporter import export_model
from clothes import get_model_dirs, ClothesId, Clo3dItemObj


def main() -> None:
    logger = get_root_logger(__file__, INFO)
    logger.info("Process start.")

    context = bpy.context
    data = bpy.data

    # read settings file
    with open('../settings/settings.json', mode='r') as f :
        settings = json.load(f)
    overwrite_fbx = settings["overwrite_fbx"]
    delete_obj_mtl = settings["delete_obj_mtl"]

    # get clothes and coord parent directory from command line args
    if len(sys.argv) != 5:
        logger.error(f'Need to input parent directory.')
        return
    
    parent = sys.argv[4]

    if not os.path.exists(parent):
        logger.error(f'Parent dir does not exist. | dir: {os.path.abspath(parent)}')
        return

    clothes_model_dirs = get_model_dirs(parent)

    if not clothes_model_dirs:
        logger.error(f'Cannot find clothes model directory. Check parent directory and file naminig convention, etc.')
        return


    # get clothes obj file list
    for clothes_model_dir in clothes_model_dirs:
        clothes_obj_files = [file for file in os.listdir(clothes_model_dir) if get_ext(file) == 'obj']
        for clothes_obj_file in clothes_obj_files:
            clothes_id = ClothesId(clothes_obj_file)
            # skip if not match clothesId
            if not clothes_id.match:
                logger.info(f'Skip convertion. Naming convention does not match. | file: {clothes_obj_file}')
                continue
            
            # check fbx exists
            fbx_exists = False
            if os.path.isfile(os.path.join(clothes_model_dir, clothes_id.id + '.fbx')):
                fbx_exists = True
                if not overwrite_fbx:
                    logger.info(f'Skip convertion. FBX already exists. | clothesId: {clothes_id.id}')
                    continue
            

            # convertion
            logger.info(f'Convert start. | clothesId: {clothes_id.id}')
            initialize(data)
            import_model(clothes_model_dir, clothes_id.id, 'obj')

            clo3d_obj = Clo3dItemObj()
            clo3d_obj.optimize_for_virtualtryon(clothes_id)

            export_model(clothes_model_dir, clothes_id.id, 'fbx')
            export_msgs = {'Convert completed.'}
            if fbx_exists:
                export_msgs.add('FBX was overwritten.')

            logger.info(f'{" ".join(export_msgs)} | clothesId: {clothes_id.id}')


            # delete obj
            if delete_obj_mtl:
                obj = os.path.join(clothes_model_dir, clothes_id.id + '.obj')
                mtl = os.path.join(clothes_model_dir, clothes_id.id + '.mtl')
                deleted_files = set()
                if os.path.isfile(obj):
                    os.remove(obj)
                    deleted_files.add("OBJ")
                if os.path.isfile(mtl):
                    os.remove(mtl)
                    deleted_files.add("MTL")

                if deleted_files:
                    logger.info(f'{", ".join(deleted_files)} file deleted. | clothesId: {clothes_id.id}')


    logger.info("Process completed.")
    return


if __name__ == '__main__':
    main()