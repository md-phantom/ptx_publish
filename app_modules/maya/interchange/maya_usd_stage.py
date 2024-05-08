import pymel.core as pm
from ..factories.maya_process_factory import MayaProxyProcessBase
from ..utils import usd_utils as uu

import logging


class MayaUsdStage(MayaProxyProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def process(self):
        if self.proxy_path == "":
            self.process_state = 0
            logging.error("The Proxy Path wasn't specified.")

        self.out_node = uu.create_usd_stage(self.proxy_path)        
        self.process_state = 2

    def reroute_proxy(self, new_path: str):
        self.out_node.setAttr("filePath", new_path)
        self.proxy_path = new_path


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya USD Stage creation class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaUsdStage:
        if not self._instance:
            self._instance = MayaUsdStage(*args, **kwds)
        return self._instance