import pymel.core as pm
from ..factories.maya_process_factory import MayaImportProxyProcessBase

import logging


class MayaNativeImporter(MayaImportProxyProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__import_path = kwargs.get('import_path') if 'import_path' in kwargs.keys() else ''

    def process(self):
        if self.__import_path == '':
            logging.error("Import path not specified.")
            self.process_state = 0
            return
        
        pm.importFile(self.__import_path, loadReferenceDepth="none")
        
        self.process_state = 2


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaNativeImporter:
        if not self._instance:
            self._instance = MayaNativeImporter(*args, **kwds)
        return self._instance