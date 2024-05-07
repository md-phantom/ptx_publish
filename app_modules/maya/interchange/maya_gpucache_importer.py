import pymel.core as pm
from ..factories.maya_process_factory import MayaProcessBase
from ..utils import alembic_utils as au

import logging
from pathlib import Path


class MayaGpuCacheImporter(MayaProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gpu_cache_node = kwargs.get('root_node') if 'root_node' in kwargs.keys() else None

    def process(self):
        if not self.root_node:
            self.process_state = 0
            logging.error("Root node not specified. Please select a root node to cache.")

        au.gpu_cache_to_geom(self.gpu_cache_node)
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