import pymel.core as pm
from ..factories.maya_process_factory import MayaProcessBase
from ..utils import alembic_utils as au

import logging
from pathlib import Path


class MayaAlembicExporter(MayaProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root_node = kwargs.get('root_node') if 'root_node' in kwargs.keys() else None
        self.export_path = kwargs.get('export_path') if 'export_path' in kwargs.keys() else ''
        self.frame_range = kwargs.get('frame_range') if 'frame_range' in kwargs.keys() else [1, 1]

    def process(self):
        if not self.root_node:
            self.process_state = 0
            logging.error("Root node not specified. Please select a root node to cache.")

        if self.export_path == "":
            self.process_state = 1
            logging.warning("Export path wasn't specified. Using the current file's location as the export path.")
            f_path = Path(pm.sceneName())
            self.export_path = f'{f_path.parent.as_posix()}/{f_path.stem}.abc'

        abc_cmd = au.generate_abc_command(self.root_node, self.export_path, self.frame_range[0], self.frame_range[1])
        au.export_abc(abc_cmd)
        self.process_state = 2


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaAlembicExporter:
        if not self._instance:
            self._instance = MayaAlembicExporter(*args, **kwds)
        return self._instance