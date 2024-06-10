import pymel.core as pm
from ...core.ptx_publish_factory import AssetInfo, Passive
from .factories import maya_process_factory as mpf

import logging


class PtxCreateProxy(Passive):
    """
    * Handle making the model passive in Maya
    """
    __ignore_assemblies__ = ['persp', 'top', 'front', 'side']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.export_path:str = kwargs.get('export_path') if 'export_path' in kwargs.keys() else ''
        self._process = kwargs.get('use_process') if 'use_process' in kwargs.keys() else 'abc'
        self.orig_nodes = kwargs.get('orig_nodes') if 'orig_nodes' in kwargs.keys() else []

        self.__proxy = None

    def make_passive(self):        
        # Create the process factory
        prc_factory = mpf.MayaProcessFactory()

        # Register the proxy process, create the node and run it
        prx_mod = prc_factory.register_process("proxies", self._process)
        self.__proxy = prc_factory.create(prx_mod, proxy_path=self.export_path, use_process=self._process)
        self.__proxy.process()

        if self.__proxy.process_state > 0:
            # Delete the root node if the process state is greater than 0
            pm.delete(self.orig_nodes)

        # Set the publish state to the minimum of the exporter and proxy process states
        self.publish_state = self.__proxy.process_state

    def reroute_proxy(self, new_path: str):
        return super().reroute_proxy(new_path)


class PtxNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Model Activate class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PtxCreateProxy:
        if not self._instance:
            self._instance = PtxCreateProxy(*args, **kwds)
        return self._instance