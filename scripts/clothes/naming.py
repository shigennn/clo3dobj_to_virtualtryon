import os, re
from typing import Dict, List
from inspect import stack
from logging import getLogger

from utils import get_filename_without_ext

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.clothes.naming'
module_logger = getLogger(module_logger_name)

PATTERN_CLOHTES_ID = '[0-9]{4}[mfMF][tbodiTBODI]$'
PATTERN_COORD_ID = 'c[0-9]{4}$'
FBX_DIR = '1.result\\fbx'
CLOTHES_DIR_NAME = 'clothes'
COORD_DIR_NAME = 'coord'

class ClothesId:
    def __init__(self, string: str) -> None:
        self.match = is_clothes_id(string)
        if self.match:
            self.id = get_filename_without_ext(string)
            self.type  = get_clothes_type(self.id)
            self.gender = get_gender(self.id)

        return
       

def get_model_dirs(parent: str) -> List[str]:
    model_dirs = list()

    for child in os.listdir(parent):
        if child.lower() == CLOTHES_DIR_NAME:
            clothes_dir = os.path.join(parent, child)
            model_dirs += [
                os.path.join(clothes_dir, d, FBX_DIR) for d in os.listdir(clothes_dir) if os.path.isdir(os.path.join(clothes_dir, d)) and is_clothes_id(d)
            ]
        elif child.lower() == COORD_DIR_NAME:
            coord_dir = os.path.join(parent, child)
            model_dirs += [
                os.path.join(coord_dir, d, FBX_DIR) for d in os.listdir(coord_dir) if os.path.isdir(os.path.join(coord_dir, d)) and is_coord_id(d)
            ]

    return model_dirs


def is_clothes_id(string: str) -> bool:
    return re.fullmatch(PATTERN_CLOHTES_ID, get_filename_without_ext(string))

def is_coord_id(string: str) -> bool:
    return re.fullmatch(PATTERN_COORD_ID, get_filename_without_ext(string))


def get_gender(clothes_id: str) -> str:
    gender_code = clothes_id[-2]
    if gender_code == 'm' or gender_code == 'M':
        gender = 'male'
    elif gender_code == 'f' or gender_code == 'F':
        gender = 'female'
    else:
        gender = ''
        module_logger.error(f'Gender code does not match. | clothesId: {clothes_id}')
    return gender

def get_clothes_type(clothes_id: str) -> str:
    type_code = clothes_id[-1]
    if type_code == 't' or type_code == 'T' or type_code == 'i' or type_code == 'I':
        clothes_type = 'top'
    elif type_code == 'b' or type_code == 'B':
        clothes_type = 'bottom'
    elif type_code == 'd' or type_code == 'D':
        clothes_type = 'dress'
    elif type_code == 'o' or type_code == 'O':
        clothes_type = 'outer'
    else:
        clothes_type = ''
        module_logger.error(f'Clothes type code does not match. | clothesId: {clothes_id}')
    return clothes_type