import bpy
import os, sys
from inspect import stack
from logging import getLogger

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.exporter.model'
module_logger = getLogger(module_logger_name)

from utils import validate_path


EXTENSIONS = (
    'fbx',
    'glb',
    'gltf',
    # 'obj',
    'vrm'
)

def export_model(directory: str, file_name: str, extension: str) -> None:
    extension = extension.lower()
    if extension not in EXTENSIONS:
        module_logger.error(f'File extension not supported. | extension: {extension}')
        sys.exit()

    path_valid = validate_path(directory, file_name, extension)

    if path_valid.get("error"):
        module_logger.error(path_valid["error"])
        sys.exit()

    file_path = path_valid.get("path")

    if not path_valid.get("warn"):
        module_logger.debug(f'Overwrite file. | path: {file_path}')

    module_logger.debug(f'{extension.upper()} export start.')

    if extension == 'vrm':
        bpy.ops.export_scene.vrm(
            filepath = file_path, 
            export_invisibles = False, 
            export_only_selections = False, 
            enable_advanced_preferences = False, 
            export_fb_ngon_encoding = False,        
        )

    elif extension == 'glb':
        bpy.ops.export_scene.gltf(
            filepath = file_path, 
            export_format = 'GLB', 
            export_draco_mesh_compression_enable = False, 
            export_tangents = False, 
            export_materials = 'EXPORT', 
            export_yup = True, 
            export_animations = True
        )

    elif extension == 'gltf':
        bpy.ops.export_scene.gltf(
            filepath = file_path, 
            export_format = 'GLTF_EMBEDDED', 
            export_draco_mesh_compression_enable = False, 
            export_tangents = False, 
            export_materials = 'EXPORT', 
            export_yup = True, 
            export_animations = True
        )

    elif extension == 'fbx':
        bpy.ops.export_scene.fbx(
            filepath = file_path, 
            use_active_collection = False, 
            global_scale = 1.0, 
            apply_unit_scale = True, 
            apply_scale_options = 'FBX_SCALE_NONE', 
            use_space_transform = True, 
            bake_space_transform = True, # Apply Transform option, default false
            use_triangles = True,
            add_leaf_bones = False,
            primary_bone_axis = 'Y',
            secondary_bone_axis = 'X',
            path_mode = 'COPY', # Emmed texture
            embed_textures = True,  # Emmed texture
        )

    module_logger.debug(f'{extension.upper()} export completed.')

    return