import pymel.core as pm
from ..factories.maya_process_factory import MayaImportProxyProcessBase
from ..utils import alembic_utils as au

import logging
from pathlib import Path


class MayaGpuCacheImporter(MayaImportProxyProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def process(self):
        if not self.proxy_node:
            self.process_state = 0
            logging.error("Proxy node not specified.")

        cache_node = None
        if self.proxy_node.nodeType() == "transform":
            if len(self.proxy_node.listRelatives(allDescendents=True, typ='gpuCache', fullPath=True)) > 0:
                cache_node = self.proxy_node.listRelatives(allDescendents=True, typ='gpuCache', fullPath=True)[0]
        elif self.proxy_node.nodeType() == "gpuCache":
            cache_node = self.proxy_node

        if not cache_node:
            self.process_state = 0
            logging.error("No valid GPU Cache found in selection.")
        
        au.gpu_cache_to_geom(cache_node)
        self.process_state = 2


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaGpuCacheImporter:
        if not self._instance:
            self._instance = MayaGpuCacheImporter(*args, **kwds)
        return self._instance