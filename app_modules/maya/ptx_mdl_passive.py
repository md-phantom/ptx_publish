import pymel.core as pm
from ...core.ptx_publish_factory import Activate, AssetInfo, Passive
from .utils import alembic_utils as au
from dataclasses import dataclass
from typing import List
import logging
import os
from pathlib import Path


@dataclass
class MdlAssetInfo():
    """
    * Overriding AssetInfo to include the name of the root node, and store the list of 
    * geometries under the root node that will be exported out.
    """
    root_node: str
    geom_list: List[str]


class PtxMdlPassive(Passive):
    """
    * Handle making the model passive in Maya
    """
    __ignore_assemblies__ = ['persp', 'top', 'front', 'side']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.asset = AssetInfo(*args)
        self.export_path:str = ''

    def make_passive(self):
        # The root is the first top node which is not in the default top level nodes
        root_node = [node for node in pm.ls(assemblies=True) if node not in self.__ignore_assemblies__][0]
        geom_list = [each_mesh for each_mesh in root_node.listRelatives(allDescendents=True, typ='mesh', fullPath=True)]
        if self.asset.lock_owner != os.getenv('USERNAME').upper():
            self.publish_state = 0
            logging.error("Locknames on file don't match.")

        f_path = Path(pm.sceneName())
        self.export_path = f'{f_path.parent}/{f_path.stem}.abc'
        abc_cmd = au.generate_abc_command(root_node, self.export_path, 1, 1)
        au.export_abc(abc_cmd)

    def convert_scene_gpu_cache(self, cache_path):
        # Remove the old geometries
        root_node = [node for node in pm.ls(assemblies=True) if node not in self.__ignore_assemblies__][0]
        pm.delete(root_node)

        # Import the GPU Cache
        au.import_gpu_cache(cache_path)


class PtxNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Model Activate class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PtxMdlPassive:
        if not self._instance:
            self._instance = PtxMdlPassive(*args, **kwds)
        return self._instance