import bpy
import os, sys
from typing import List, Optional
from inspect import stack
from logging import getLogger

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.editor.material'
module_logger = getLogger(module_logger_name)

SHADERS = (
    'UNLIT',
    'STANDARD',
)

BLEND_METHODS = (
    'OPAQUE',
    'BLEND',
    'CLIP'
)

IMAGE_EXTENSIONS = (
    'JPG',
    'JPEG',
    'PNG',
    'BMP',
    'TIFF',
    'TGA',
)

class Material:
    def __init__(self, mat: bpy.types.Material) -> None:
        self._logger_name = f'{root_logger_name}.{self.__module__}'
        self._logger = getLogger(self._logger_name)

        self.material: bpy.types.Material = mat
        self.shader: str = 'UNLIT'

        self.texture_dir: str = ''
        self.basecolor_tex: str = ''
        self.basecolor_tex_path: str = ''
        self.normal_tex: str = ''
        self.normal_tex_path: str = ''
        self.roughness_tex: str = ''
        self.roughness_tex_path: str = ''
        self.emission_tex: str = ''
        self.emission_tex_path: str = ''
        
        self.metallic_param: float = 0.0
        self.roughness_param: float = 1.0
        self.emission_color: List[float] = [0.0, 0.0, 0.0, 1.0]
        self.blend_method: str = 'OPAQUE'
        self.multiply_color = None

    def set_shader(self, shader: str) -> None:
        sd = shader.upper()
        if sd in SHADERS:
            self.shader = sd
        else:
            self._logger.warning(f'Unexpected shader name. blend method must be {[x for x in SHADERS]} | shader: {shader}')
        return
    
    def _set_basecolor_tex_path(self, path: str) -> None:
        # 画像ファイル拡張子で検出した方がいい
        if not os.path.exists(path):
            self._logger.warning(f'Base color texture path does not exist. | path: {path}')
            return
        self.basecolor_tex_path = path
        return
    
    def _set_normal_tex_path(self, path: str) -> None:
        if not os.path.exists(path):
            self._logger.warning(f'Normal texture path does not exist. | path: {path}')
            return
        self.normal_tex_path = path
        return
    
    def _set_roughness_tex_path(self, path: str) -> None:
        if not os.path.exists(path):
            self._logger.warning(f'Roughness texture path does not exist. | path: {path}')
            return
        self.roughness_tex_path = path
        return
    
    def _set_emission_tex_path(self, path: str) -> None:
        if not os.path.exists(path):
            self._logger.warning(f'Emission texture path does not exist. | path: {path}')
            return
        self.emission_tex_path = path
        return
    
    def set_blend_method(self, blend_method: str) -> None:
        bm = blend_method.upper()
        if bm in BLEND_METHODS:
            self.blend_method = bm
        else:
            self._logger.warning(f'Unexpected blend method. blend method must be {[x for x in BLEND_METHODS]} | blend_method: {blend_method}')
        return

    def _create_unlit_material(self) -> None:
        # set blend method
        self.material.blend_method = self.blend_method

        self.material.use_nodes = True
        node_tree = self.material.node_tree

        # remove all nodes
        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        # create unlit nodes
        trs_node = node_tree.nodes.new(type='ShaderNodeBsdfTransparent')
        trs_node.location = 0, -400
        mix_node = node_tree.nodes.new(type='ShaderNodeMixShader')
        mix_node.location = 350, 0
        mat_out_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        mat_out_node.location = 600, 0
        node_tree.links.new(trs_node.outputs[0], mix_node.inputs[1])
        node_tree.links.new(mix_node.outputs[0], mat_out_node.inputs['Surface'])

        if self.basecolor_tex_path:
            # set base color tex node
            _create_image_node(node_tree, self.basecolor_tex_path, mix_node.inputs[2], mix_node.inputs[0])
        else:
            # set gray
            self._logger.warning(f'No base color texture. Set gray color.')
            color_node = node_tree.nodes.new(type='ShaderNodeRGB')
            node_tree.links.new(color_node.outputs[0], mix_node.inputs[2])
        
        return

    def _create_standard_material(self) -> None:
        # set blend method
        self.material.blend_method = self.blend_method
            
        self.material.use_nodes = True
        node_tree = self.material.node_tree

        # remove all nodes
        for node in node_tree.nodes:
            node_tree.nodes.remove(node)
        
        # create stadard shader nodes
        shader_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        shader_node.location = 400, 0
        mat_out_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        mat_out_node.location = 700, 0
        self.material.node_tree.links.new(shader_node.outputs[0], mat_out_node.inputs['Surface'])

        # set shader params
        shader_node.inputs['Metallic'].default_value = self.metallic_param
        shader_node.inputs['Roughness'].default_value = self.roughness_param
        
        # set base color
        if self.basecolor_tex_path:
            if self.blend_method == 'OPAQUE':
                _create_image_node(node_tree= node_tree, image_path= self.basecolor_tex_path, color_input= shader_node.inputs['Base Color'], multiply_color= self.multiply_color)
            else:
                _create_image_node(node_tree= node_tree, image_path= self.basecolor_tex_path, color_input= shader_node.inputs['Base Color'], alpha_input= shader_node.inputs['Alpha'], multiply_color= self.multiply_color)

        # set normal
        if self.normal_tex_path:
            _create_image_node(node_tree, self.normal_tex_path, shader_node.inputs['Normal'], None, True)

        # set roughness
        if self.roughness_tex_path:
            _create_image_node(node_tree, self.roughness_tex_path, shader_node.inputs['Roughness'])

        # set emission
        if self.emission_tex_path:
            _create_image_node(node_tree, self.emission_tex_path, shader_node.inputs['Emission'])
        else:
            shader_node.inputs['Emission'].default_value = self.emission_color

        return

    def setting(self, setting: dict) -> None:
        shader = setting.get("shader")
        basecolor_tex = setting.get("basecolor_tex")
        normal_tex = setting.get("normal_tex")
        roughness_tex = setting.get("roughness_tex")
        emission_tex = setting.get("emission_tex")
        metallic_param = setting.get("metallic_param")
        roughness_param = setting.get("roughness_param")
        emission_color = setting.get("emission_color")
        blend_method = setting.get("blend_method")
        multiply_color = setting.get("multiply_color")
        
        if isinstance(shader, str):
            self.set_shader(shader)

        if isinstance(basecolor_tex, str) and basecolor_tex != "":
            basecolor_tex_path = os.path.join(self.texture_dir, basecolor_tex)
            self._set_basecolor_tex_path(basecolor_tex_path)

        if isinstance(normal_tex, str) and normal_tex != "":
            normal_tex_path = os.path.join(self.texture_dir, normal_tex)
            self._set_normal_tex_path(normal_tex_path)

        if isinstance(roughness_tex, str) and roughness_tex != "":
            roughness_tex_path = os.path.join(self.texture_dir, roughness_tex)
            self._set_roughness_tex_path(roughness_tex_path)

        if isinstance(emission_tex, str) and emission_tex != "":
            emission_tex_path = os.path.join(self.texture_dir, emission_tex)
            self._set_emission_tex_path(emission_tex_path)

        if isinstance(metallic_param, int|float):
            self.metallic_param = float(metallic_param)

        if isinstance(roughness_param, int|float):
            self.roughness_param = float(roughness_param)

        if isinstance(emission_color, list):
            if len(emission_color) == 4:
                self.emission_color = emission_color

        if isinstance(blend_method, str):
            self.set_blend_method(blend_method)

        if isinstance(multiply_color, list):
            if len(multiply_color) == 4 and all([isinstance(x, float) for x in multiply_color]):
                self.multiply_color = multiply_color

        return

    def create(self) -> None:
        if self.shader == 'UNLIT':
            self._create_unlit_material()
            msg = f'UNLIT material created. | {self.material.name}'
        elif self.shader == 'STANDARD':
            self._create_standard_material()
            msg = f'STANDARD material created. | {self.material.name}'

        self._logger.info(msg)
        return


def _create_image_node(
    node_tree: bpy.types.ShaderNodeTree, 
    image_path: str, 
    color_input: bpy.types.NodeSocket,
    alpha_input: Optional[bpy.types.NodeSocket] = None,
    is_normal: bool = False,
    multiply_color: Optional[List[int]] =  None,
) -> None:
    module_logger.debug(sys._getframe().f_code.co_name)
    # create image node
    img_node = node_tree.nodes.new(type='ShaderNodeTexImage')
    img_node.location = 0, 0
    node_tree.nodes.active = img_node
    loadimage = bpy.data.images.load(filepath = image_path)
    img_node.image = loadimage

    if multiply_color:
        mix_rgb_node = node_tree.nodes.new(type='ShaderNodeMixRGB')
        mix_rgb_node.blend_type = 'MULTIPLY'
        mix_rgb_node.inputs['Fac'].default_value = 1
        mix_rgb_node.inputs['Color2'].default_value = multiply_color

    if is_normal:
        # normal map
        normal_map_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
        normal_map_node.location = 0, -600
        normal_map_node.uv_map = "UVMap" # get uvmap
        node_tree.links.new(img_node.outputs['Color'], normal_map_node.inputs['Color'])
        node_tree.links.new(normal_map_node.outputs['Normal'], color_input)
    else:
        # other
        if multiply_color:
            node_tree.links.new(img_node.outputs['Color'], mix_rgb_node.inputs['Color1'])
            node_tree.links.new(mix_rgb_node.outputs['Color'], color_input)
        else:
            node_tree.links.new(img_node.outputs['Color'], color_input)

        if alpha_input:
            node_tree.links.new(img_node.outputs['Alpha'], alpha_input)
    
    return

def remove_all_materials(mesh: bpy.types.Object) -> None:
    mesh.data.materials.clear()
    return

def create_material(mesh: bpy.types.Object, name: str) -> None:
    mesh.data.materials.append(name)
    return