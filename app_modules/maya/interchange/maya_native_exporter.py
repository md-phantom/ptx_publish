import pymel.core as pm
from ..factories.maya_process_factory import MayaExportProcessBase

import logging
from pathlib import Path


class MayaNativeExporter(MayaExportProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__maya_file_type = kwargs.get('maya_file_type') if 'maya_file_type' in kwargs.keys() else 'ma'
        self.__force = kwargs.get('force') if 'force' in kwargs.keys() else True
        self.__preserve_refs = kwargs.get('preserver_references') if 'preserver_references' in kwargs.keys() else False
        self.__selection_only = kwargs.get('selection_only') if 'selection_only' in kwargs.keys() else False

    def process(self):
        if not self.root_node:
            self.process_state = 0
            logging.error("Root node not specified. Please select a root node to cache.")

        if self.export_path == "":
            self.process_state = 1
            logging.warning("Export path wasn't specified. Using the current file's location as the export path.")
            f_path = Path(pm.sceneName())
            self.export_path = f'{f_path.parent}/{f_path.stem}.{self.__maya_file_type}'

        if self.__selection_only:
            pm.exportSelected(self.export_path, force=self.__force, preserveReferences=self.__preserve_refs, type=self.__maya_file_type)
        else:
            pm.exportAll(self.export_path, force=self.__force, preserveReferences=self.__preserve_refs, type=self.__maya_file_type)
        self.process_state = 2


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaNativeExporter:
        if not self._instance:
            self._instance = MayaNativeExporter(*args, **kwds)
        return self._instance