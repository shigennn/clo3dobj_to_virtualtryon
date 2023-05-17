import bpy
from typing import List
# from inspect import stack
# from logging import getLogger


""" root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.editor.scene'
module_logger = getLogger(module_logger_name) """


def initialize(data: bpy.types.BlendData) -> None:  
    for ob in data.objects:
        data.objects.remove(ob, do_unlink=True)
    for mat in data.materials:
        data.materials.remove(mat)
    for act in data.actions:
        data.actions.remove(act)
    for img in data.images:
        data.images.remove(img)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    return

def _controll_fake_user(datablocks: bpy.types.bpy_prop_collection, use_fake_user: bool) -> None:
    for datablock in datablocks:
        datablock.use_fake_user = use_fake_user
    return

def clean(data: bpy.types.BlendData) -> None:
    _controll_fake_user(data.materials, False)
    _controll_fake_user(data.images, False)
    _controll_fake_user(data.brushes, False)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    return


def select_all(context: bpy.types.Context) -> None:
    for ob in context.scene.objects:
        ob.select_set(True)
    return


def deselect_all(context: bpy.types.Context) -> None:
    for ob in context.scene.objects:
        ob.select_set(False)
    context.view_layer.objects.active = None
    return


RESET_TARGET = (
    'ARMATURE',
    'MESH',
)

def reset_transform_all(
    context: bpy.types.Context, 
    reset_location: bool = True, 
    reset_rotation: bool = True, 
    reset_scale: bool = True
) -> None:
    scale = 1.0
    is_first_obj = True
    for ob in context.scene.objects:
        if not ob.type in RESET_TARGET:
            ob.select_set(False)
            continue

        ob.select_set(True)

        if ob.type == 'ARMATURE':
            scale = ob.scale.x

        if is_first_obj:
            context.view_layer.objects.active = ob
            bpy.ops.object.mode_set(mode = "OBJECT")
            is_first_obj = False

    bpy.ops.object.transform_apply(location = reset_location, rotation = reset_rotation, scale = reset_scale)

    deselect_all(context)
    context.view_layer.objects.active = None

    if reset_scale and reset_scale != 1.0:
        for act in bpy.data.actions:
            correct_scale_fixed_action(act, scale)
    return


def correct_scale_fixed_action(action: bpy.types.Action, scale_factor: int|float) -> None:
    for fcurve in action.fcurves:
        if fcurve.data_path.endswith('location'):
            for kfp in fcurve.keyframe_points:
                kfp.co[1] *= scale_factor

    return


def create_empty(name: str, location: List[int], coll_name: str) -> bpy.types.Object:
    empty_obj = bpy.data.objects.new( "empty", None, )
    empty_obj.name = name
    empty_obj.empty_display_size = 1 
    bpy.data.collections[coll_name].objects.link(empty_obj)
    empty_obj.location = location
    return empty_obj