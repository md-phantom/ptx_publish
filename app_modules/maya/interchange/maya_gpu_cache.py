import pymel.core as pm
from ..factories.maya_process_factory import MayaProxyProcessBase
from ..utils import alembic_utils as au

import logging
from pathlib import Path


class MayaGpuCache(MayaProxyProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cache_path = kwargs.get('cache_path') if 'cache_path' in kwargs.keys() else ''

    def process(self):
        if self.cache_path == "":
            self.process_state = 0
            logging.error("The alembic path wasn't specified")

        self.out_node = au.import_gpu_cache(self.cache_path)
        self.process_state = 2

    def rerout_proxy(self, new_path: str):
        if new_path == "":
            logging.warning("No new path specified.")
            return
        
        self.out_node.setAttr("cacheFileName", new_path)


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaGpuCache:
        if not self._instance:
            self._instance = MayaGpuCache(*args, **kwds)
        return self._instance