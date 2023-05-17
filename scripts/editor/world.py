import bpy
import os
from typing import Set, List, Dict, Optional, Tuple
from inspect import stack
from logging import getLogger

root_logger_name = os.path.splitext(os.path.basename(stack()[-2].filename))[0]
module_logger_name = f'{root_logger_name}.editor.world'
module_logger = getLogger(module_logger_name)

class World:
    def __init__(self, name: str) -> None:
        self._logger_name = f'{root_logger_name}.{self.__module__}'
        self._logger = getLogger(self._logger_name)

        self.world = bpy.data.worlds.new(name)
        bpy.context.scene.world = self.world

    def solid_color(self, color: Tuple[int|float]) -> bpy.types.World:
        # check color
        if not len(color) == 4 or not all([isinstance(x, int|float) for x in color]):
            module_logger.warning(f'Color must be Tupple[int|float] | color: {color}')
            color = (1, 1, 1, 1)

        _construct_solid_color_background_node(self.world, color)

        return self.world

    def solid_color_hdri(self, color: Tuple[int|float], hdri_filepath: str) -> bpy.types.World:
        # check color
        if not len(color) == 4 or not all([isinstance(x, int|float) for x in color]):
            module_logger.warning(f'Color must be Tupple[int|float] | color: {color}')
            color = (1, 1, 1, 1)

        if not os.path.exists(hdri_filepath):
            return

        _construct_solid_color_background_node(self.world, color, hdri_filepath)

        return self.world

def _construct_solid_color_background_node(world: bpy.types.World, rgba: Tuple[int|float], hdri_filepath: str = None) -> None:
    world.use_nodes = True
    node_tree = world.node_tree

    # remove all nodes
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)
    # create node
    rgb = node_tree.nodes.new(type='ShaderNodeRGB')
    light_path = node_tree.nodes.new(type='ShaderNodeLightPath')
    mix = node_tree.nodes.new(type='ShaderNodeMixRGB')
    world_out = node_tree.nodes.new(type='ShaderNodeOutputWorld')
    background = node_tree.nodes.new(type='ShaderNodeBackground')
    # location
    rgb.location = -200, -300
    light_path.location = -200, 300
    mix.location = 0, 0
    world_out.location = 400, 0
    background.location = 200, 0
    # create link
    node_tree.links.new(rgb.outputs[0], mix.inputs[2])
    node_tree.links.new(light_path.outputs[0], mix.inputs[0])
    node_tree.links.new(mix.outputs[0], background.inputs[0])
    node_tree.links.new(background.outputs[0], world_out.inputs[0])
    
    # set background color
    rgb.outputs[0].default_value = rgba

    # set hdri
    if hdri_filepath:
        return

    return