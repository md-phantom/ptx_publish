import pymel.core as pm
from ..factories.maya_process_factory import MayaProcessBase
from ..utils import usd_utils as uu

import logging
from pathlib import Path


class MayaUsdStage(MayaProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.usd_path = kwargs.get('usd_path') if 'usd_path' in kwargs.keys() else ''

    def process(self):
        if self.usd_path == "":
            self.process_state = 0
            logging.error("Export path wasn't specified. Using the current file's location as the export path.")

        self.out_node = uu.create_usd_stage(self.usd_path)        
        self.process_state = 2


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaUsdStage:
        if not self._instance:
            self._instance = MayaUsdStage(*args, **kwds)
        return self._instance