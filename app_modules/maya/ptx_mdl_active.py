import pymel.core as pm
from ...core.ptx_publish_factory import Activate, AssetInfo, Passive
from .utils import alembic_utils as au

import logging


class PtxMdlActivate(Activate):
    """
    * Handle making the model active in Maya
    """
    __ignore_assemblies__ = ['persp', 'top', 'front', 'side']

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.asset = AssetInfo(*args)

    def make_active(self):
        if self.is_asset_locked():
            self.publish_state = 0
            logging.error("Asset is already locked. Aborting")
            return
        
        gpu_cache_node:pm.PyNode = None
        for node in pm.ls(assemblies=True):
            if node not in self.__ignore_assemblies__:
                gpu_cache_node = node.listRelatives(allDescendents=True, typ='gpuCache', fullPath=True)[0] if len(node.listRelatives(allDescendents=True, typ='gpuCache', fullPath=True)) > 0 else None

        logging.info(f"GPUCacheNode: {gpu_cache_node}")

        if gpu_cache_node == None:
            self.publish_state = 1
            logging.warning("Unable to find any GPU Cache node")
            return

        # Convert the gpu_cache to normal geometry
        au.gpu_cache_to_geom(gpu_cache_node)
        # Write out the activated info with the new lock owner
        self.generate_lock_info()

        self.publish_state = 2


class PtxNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Model Activate class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PtxMdlActivate:
        if not self._instance:
            self._instance = PtxMdlActivate(*args, **kwds)
        return self._instance