import pymel.core as pm
from ..factories.maya_process_factory import MayaImportProxyProcessBase
from ..utils import usd_utils as uu

import logging


class MayaUsdImporter(MayaImportProxyProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def process(self):
        if self.proxy_node == None:
            self.process_state = 0
            logging.error("No USD stage was specified.")

        stage_node = None
        if self.proxy_node.nodeType() == "transform":
            if len(self.proxy_node.listRelatives(allDescendents=True, typ='mayaUsdProxyShape', fullPath=True)) > 0:
                stage_node = self.proxy_node.listRelatives(allDescendents=True, typ='mayaUsdProxyShape', fullPath=True)[0]
        elif self.proxy_node.nodeType() == "mayaUsdProxyShape":
            stage_node = self.proxy_node

        if not stage_node:
            self.process_state = 0
            logging.error("No valid Maya USD Proxy Shape Node found in selection.")

        uu.nativize_stage(stage_node)
        
        self.process_state = 2


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaUsdImporter:
        if not self._instance:
            self._instance = MayaUsdImporter(*args, **kwds)
        return self._instance