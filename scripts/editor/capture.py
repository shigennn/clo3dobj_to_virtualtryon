import bpy
import os
from typing import Set, List, Dict, Optional
from inspect import stack
from importer import append
from logging import getLogger

from .world import World

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.editor.capture'
module_logger = getLogger(module_logger_name)


BLEND_FILE_PATH = "C:\\Users\\shige\\Downloads\\test.blend"

def create_avatar_thumbnail(data: bpy.types.BlendData, scene: bpy.types.Scene) -> None:
    append(data, scene, BLEND_FILE_PATH)

    render = scene.render

    render.engine = 'BLENDER_EEVEE'
    render.image_settings.file_format = 'PNG'
    render.film_transparent = True
    render.resolution_x = 1080
    render.resolution_y = 1080
    render.filepath = "C:\\Users\\shige\\Downloads\\"


    return
