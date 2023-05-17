import os
from typing import Dict

def get_filename_without_ext(file_name: str) -> str:
    return os.path.splitext(file_name)[0]

def get_ext(file_name: str) -> str:
    return os.path.splitext(file_name)[1][1:]


def validate_path(directory: str, file_name: str, file_extension: str) -> Dict[str, str]:
    validate = dict()
    if not isinstance(directory, str) or not isinstance(file_name, str):
        validate.update([
            ("error", f'Unexpected directory or file name. Both must be string. | directory: {directory}, file: {file_name}'),
        ])
        return validate

    if not os.path.exists(directory):
        validate.update([
            ("error", f'Directory does not exist. | directory: {directory}')
        ])

    if not file_name.endswith(file_extension):
        file_name = f'{file_name}.{file_extension}'
    
    file_path = os.path.join(directory, file_name)

    if not os.path.exists(file_path):
        validate.update([
            ("warn", f'Path does not exist. | path: {file_path}'),
        ])

    validate.update([
        ("path", file_path),
    ])

    return validate