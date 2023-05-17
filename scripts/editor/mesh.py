import bpy
import bmesh
import os
from typing import Optional
from inspect import stack
from logging import getLogger

from editor import deselect_all, clean

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.editor.mesh'
module_logger = getLogger(module_logger_name)

COLORS =  (
    (1,0,0),
    (0,0,1),
    (1,0.843137255,0),
    (0,0.501960784,0),
    (0,0.749019608,1),
    (0.933333333,0.509803922,0.933333333),
    (0.956862745,0.643137255,0.376470588),
    (0.941176471,0.501960784,0.501960784),
    (1,0.270588235,0),
    (1,0.549019608,0),
    (0.933333333,0.909803922,0.419607843),
    (0.501960784,0.501960784,0),
    (0.48627451,0.988235294,0),
    (0.560784314,0.737254902,0.560784314),
    (0.4,1,0.666666667),
    (0.498039216,1,0.831372549),
    (0.68627451,0.933333333,0.933333333),
    (0.254901961,0.411764706,0.882352941),
    (0.541176471,0.168627451,0.88627451),
    (1,0.078431373,0.576470588),
    (1,0.71372549,0.756862745),
    (0,0,0),
    (1,1,1)
)


def _is_mesh_obj(obj: bpy.types.Object) -> bool:
    return bool(obj.type == 'MESH')


def get_mesh_obj_by_name(context: bpy.types.Context, mesh_obj_name: str) -> Optional[bpy.types.Object]:
    obj = context.scene.objects.get(mesh_obj_name)

    if not obj:
        return None
    
    if not _is_mesh_obj(obj):
        return None

    return obj


def has_blendshape(mesh: bpy.types.Object) -> bool:
    if not _is_mesh_obj(mesh):
        module_logger.error(f'Object type must be "MESH". | object: {mesh}, type: {mesh.type}')
        return False

    if not mesh.data.shape_keys:
        return False
    
    return True


def _select_all_verts(edit_mesh: any) -> None:
    edit_mesh.select_mode = {'VERT'}
    for vert in edit_mesh.verts:
        vert.select_set(True)
    return

def _deselect_all_verts(edit_mesh: any) -> None:
    for vert in edit_mesh.verts:
        vert.select_set(False)
    return


def select_mesh_object(context: bpy.types.Context, mesh: bpy.types.Object) -> None:
    if not _is_mesh_obj(mesh):
        module_logger.error(f'Object type must be "MESH". | object: {mesh}, type: {mesh.type}')
        return
    deselect_all(context)
    mesh.select_set(True)
    context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    return


def join_all_meshes(context: bpy.types.Context, data: bpy.types.BlendData, joined_name: str = 'Mesh') -> bpy.types.Object:
    is_first_obj = True
    for ob in context.scene.objects:
        if ob.type != 'MESH':
            ob.select_set(False)
            continue
        ob.select_set(True)

        if is_first_obj:
            context.view_layer.objects.active = ob
            bpy.ops.object.mode_set(mode = "OBJECT")
            is_first_obj = False

    bpy.ops.object.join()

    joined_mesh = context.view_layer.objects.active
    joined_mesh.name = joined_name
    joined_mesh.data.name = joined_name

    clean(data)
    deselect_all(context)

    return joined_mesh


def remove_doubles(context: bpy.types.Context, mesh: bpy.types.Object, threshold: float = 1e-05) -> None:
    select_mesh_object(context, mesh)

    bpy.ops.object.mode_set(mode='EDIT')
    edit_mesh = bmesh.from_edit_mesh(mesh.data)
    _select_all_verts(edit_mesh)
    bpy.ops.mesh.remove_doubles(threshold=threshold, use_unselected=False, use_sharp_edge_from_normals=False)
    _deselect_all_verts(edit_mesh)
    bpy.ops.object.mode_set(mode='OBJECT')

    deselect_all(context)
    return 


def recalculate_normals(context: bpy.types.Context, mesh: bpy.types.Object, smooth_angle: float=3.14159) -> None:
    select_mesh_object(context, mesh)
    
    # shade_smooth() work at selected objects only
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    context.object.data.use_auto_smooth = True
    context.object.data.auto_smooth_angle = smooth_angle
    bpy.ops.mesh.customdata_custom_splitnormals_add()

    deselect_all(context)
    return


def separate_mesh_by_materials(context: bpy.types.Context, mesh: bpy.types.Object) -> None:
    select_mesh_object(context, mesh)
    bpy.ops.mesh.separate(type='MATERIAL')
    deselect_all(context)
    return 


def set_vertexcol_by_materials(context: bpy.types.Context, mesh: bpy.types.Object) -> None:
    separate_mesh_by_materials(context, mesh)

    num = 0
    for ob in context.scene.objects:
        if ob.type != 'MESH':
            continue
        select_mesh_object(context, ob)
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        context.object.data.use_paint_mask = False
        color = COLORS[num]
        bpy.data.brushes["Draw"].color = (color)
        bpy.ops.paint.vertex_color_set()
        bpy.ops.object.mode_set(mode='OBJECT')

        num += 1
        if num > len(COLORS):
            num = 0
    
    deselect_all(context)
    return


def limit_vertex_weight_total(context: bpy.types.Context, mesh: bpy.types.Object, limit: int = 4) -> None:
    select_mesh_object(context, mesh)

    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL')
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=limit)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    deselect_all(context)
    return


def reset_material(context: bpy.types.Context, data: bpy.types.BlendData, mesh: bpy.types.Object, name: str) -> None:
    select_mesh_object(context, mesh)
    mesh.data.materials.clear()
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    newmat = data.materials.new(name)
    mesh.data.materials.append(newmat)
    return


def rescale(context: bpy.types.Context, mesh: bpy.types.Object, scale_factor: float) -> None:
    select_mesh_object(context, mesh)
    mesh.scale.x *= scale_factor
    mesh.scale.y *= scale_factor
    mesh.scale.z *= scale_factor
    deselect_all(context)
    return