import pymel.core as pm
from ...core.ptx_publish_factory import Activate, AssetInfo
from .factories import maya_process_factory as mpf
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
        self._process = kwargs.get('use_process') if 'use_process' in kwargs.keys() else 'abc'

    def make_active(self):
        # Get the selected node. If nothing is selected, just grab the first assembky
        # which is not in the __ignore_assemblies__ list        
        cache_node:pm.PyNode = pm.ls(sl=True)[0] if len(pm.ls(sl=True)) > 0 else None
        if cache_node == None:
            all_assemblies = [node for node in pm.ls(assemblies=True) if node not in self.__ignore_assemblies__]
            cache_node = all_assemblies[0] if len(all_assemblies) > 0 else None

        # If the cache node is still invalid, return with an error
        if cache_node == None:
            self.publish_state = 0
            logging.error("Unable to find any GPU Cache node")
            return
        
        logging.info(f"CacheNode: {cache_node}")

        # Create the process factory
        prc_factory = mpf.MayaProcessFactory()
        
        # Register the geometry import process, create the node and run it
        # to convert the proxy to native geometry
        imp_mod = prc_factory.register_process("importers", self._process)
        importer = prc_factory.create(imp_mod, proxy_node=cache_node)
        importer.process()

        self.publish_state = importer.process_state


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