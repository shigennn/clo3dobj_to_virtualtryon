import bpy
import os
from typing import Optional
from inspect import stack
from logging import getLogger

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.editor.armature'
module_logger = getLogger(module_logger_name)


def is_armature_obj(obj: bpy.types.Object) -> bool:
    return bool(obj.type == 'ARMATURE')


def armature_exists(context: bpy.types.Context) -> bool:
    return any(ob.type == "ARMATURE" and ob.data.users for ob in context.scene.objects)


def multiple_armatures_exist(context: bpy.types.Context) -> bool:
    first_amt_exists = False
    for obj in context.scene.objects:
        if obj.type != 'ARMATURE':
            continue

        if not obj.data.users:
            continue

        if not first_amt_exists:
            first_amt_exists = True
            continue
        
        return True

    return False


def root_bone(armature: bpy.types.Object) -> Optional[bpy.types.Bone]:
    if not is_armature_obj(armature):
        module_logger.error(f'Object type must be "ARMATURE". | object: {armature}, type: {armature.type}')
        return None

    for bone in armature.data.bones:
        if bone.parent is None and bone.children is not None:
            return bone

    return  armature.data.bones[0]