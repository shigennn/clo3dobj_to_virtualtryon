import bpy
import os, sys
from typing import Optional
from inspect import stack
from logging import getLogger

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.importer.model'
module_logger = getLogger(module_logger_name)

from utils import validate_path, get_ext, get_filename_without_ext


EXTENSIONS = (
    'fbx',
    'glb',
    'gltf',
    'obj',
    'vrm'
)

def import_model(directory: str, file_name: str, extension: Optional[str] = None) -> None:
    if extension:
        extension = extension.lower()
    else:
        extension = get_ext(file_name)
        if not extension:
            module_logger.error(f'File extension does not exist. | file: {file_name}')
            sys.exit()

    if extension not in EXTENSIONS:
        module_logger.error(f'File extension not supported. | extension: {extension}')
        sys.exit()

    path_valid = validate_path(directory, file_name, extension)

    if path_valid.get("error"):
        module_logger.error(path_valid["error"])
        sys.exit()

    if path_valid.get("warn"):
        module_logger.error(path_valid["warn"])
        sys.exit()
    
    file_path = path_valid.get("path")


    module_logger.debug(f'{extension.upper()} import start.')

    if extension == 'fbx':
        try:
            bpy.ops.import_scene.fbx(
                filepath = file_path, 
                anim_offset = 0, 
                ignore_leaf_bones = False, 
                force_connect_children = False,
                axis_forward = '-Z', 
                axis_up = 'Y'
            )
        except RuntimeError:
            module_logger.error(f'ASCII FBX files are not supported. Please convert to BINARY. | {file_path}')
            sys.exit()

    elif extension == 'glb' or extension == 'gltf':
        bpy.ops.import_scene.gltf(
            filepath = file_path, 
            convert_lighting_mode = 'SPEC', 
            filter_glob = '*.glb;*.gltf', 
            files = None, 
            loglevel = 0, 
            import_pack_images = True, 
            merge_vertices = False, 
            import_shading = 'NORMALS', 
            bone_heuristic = 'TEMPERANCE', 
            guess_original_bind_pose = True
        )

    elif extension == 'obj':
        bpy.ops.import_scene.obj(
            filepath = file_path, 
            use_edges = True, 
            use_smooth_groups = True, 
            use_split_objects = True, 
            use_split_groups = False, 
            use_groups_as_vgroups = False, 
            use_image_search = True, 
            split_mode = 'OFF', # keep vertex order
            global_clamp_size = 0.0, 
            axis_forward = '-Z', 
            axis_up = 'Y'
        )

    elif extension == 'vrm':
        bpy.ops.import_scene.vrm(
            filepath = file_path, 
            set_shading_type_to_material_on_import = True, 
            set_view_transform_to_standard_on_import = True, 
            set_armature_display_to_wire = True, 
            set_armature_display_to_show_in_front = True
        )

    module_logger.debug(f'{extension.upper()} import completed.')

    return