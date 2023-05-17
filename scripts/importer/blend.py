import bpy
import os, sys
from inspect import stack
from logging import getLogger

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.importer.blend'
module_logger = getLogger(module_logger_name)


def append(data: bpy.types.BlendData, scene: bpy.types.Scene, blend_file_path: str) -> None:
    if not os.path.exists(blend_file_path):
        module_logger.error(f'Path does not exist. | blend_file_path: {blend_file_path}')
        sys.exit()

    # append object from .blend file
    with data.libraries.load(blend_file_path) as (data_from, data_to):
        data_to.objects = data_from.objects

    # link object to current scene
    for ob in data_to.objects:
        if ob is not None:
            scene.collection.objects.link(ob)

    return 