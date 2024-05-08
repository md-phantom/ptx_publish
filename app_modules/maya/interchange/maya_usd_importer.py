import pymel.core as pm
from ..factories.maya_process_factory import MayaProcessBase
from ..utils import usd_utils as uu

import logging
from pathlib import Path


class MayaUsdImporter(MayaProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.usd_stage = kwargs.get('usd_stage_node') if 'usd_stage_node' in kwargs.keys() else None

    def process(self):
        if self.usd_stage == None:
            self.process_state = 0
            logging.error("No USD stage was specified.")

        stage_node = None
        if self.usd_stage.nodeType() == "transform":
            if len(self.usd_stage.listRelatives(allDescendents=True, typ='mayaUsdProxyShape', fullPath=True)) > 0:
                stage_node = self.usd_stage.listRelatives(allDescendents=True, typ='mayaUsdProxyShape', fullPath=True)[0]
        elif self.usd_stage.nodeType() == "mayaUsdProxyShape":
            stage_node = self.usd_stage

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