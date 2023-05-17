import bpy
import os, sys
from typing import List, Optional
from inspect import stack
from logging import getLogger

from clothes.naming import ClothesId
from editor import (
    reset_transform_all,
    remove_doubles,
    join_all_meshes,
    set_vertexcol_by_materials,
    recalculate_normals,
    reset_material,
    rescale,

)

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
# module_logger_name = f'{root_logger_name}.clothes.clo3dobj'
# module_logger = getLogger(module_logger_name)

CAPTURE_HEIGHT = 160
MALE_STD_HEIGHT = 170
FEMALE_STD_HEIGHT = 160
BASE_SCALE_FACTOR = 0.01

class Clo3dItemObj:
    def __init__(self) -> None:
        self._logger_name = f'{root_logger_name}.{self.__module__}'
        self._logger = getLogger(self._logger_name)

        return

    def optimize_for_virtualtryon(self, clothes_id: ClothesId) -> None:
        context = bpy.context
        data = bpy.data

        id = clothes_id.id
        type = clothes_id.type
        gender = clothes_id.gender

        material_name = 'M_' + type

        joined_mesh = join_all_meshes(context, data, id)
        set_vertexcol_by_materials(context, joined_mesh)
        joined_mesh = join_all_meshes(context, data, id)

        if gender == 'male':
            scale_factor = BASE_SCALE_FACTOR * int(FEMALE_STD_HEIGHT / MALE_STD_HEIGHT * 100) / 100
        elif gender == 'female':
            scale_factor = BASE_SCALE_FACTOR * int(FEMALE_STD_HEIGHT / FEMALE_STD_HEIGHT * 100) / 100
        rescale(context, joined_mesh, scale_factor)

        reset_transform_all(context)
        remove_doubles(context, joined_mesh)
        recalculate_normals(context, joined_mesh)
        reset_material(context, data, joined_mesh, material_name)

        return