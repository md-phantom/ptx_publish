import pymel.core as pm
from ..factories.maya_process_factory import MayaProcessBase
from ..utils import usd_utils as uu

import logging
from pathlib import Path


class MayaUsdExporter(MayaProcessBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root_node = kwargs.get('root_node') if 'root_node' in kwargs.keys() else None
        self.export_path = kwargs.get('export_path') if 'export_path' in kwargs.keys() else ''
        self.append = kwargs.get('append') if 'append' in kwargs.keys() else False
        self.convert_materials_to = kwargs.get('convertMaterialsTo') if 'convertMaterialsTo' in kwargs.keys() else 'UsdPreviewSurface'
        self.default_mesh_scheme = kwargs.get('defaultMeshScheme') if 'defaultMeshScheme' in kwargs.keys() else 'catmullClark'
        self.default_usd_format = kwargs.get('defaultUSDFormat') if 'defaultUSDFormat' in kwargs.keys() else 'usda'
        self.frame_range = kwargs.get('frameRange') if 'frameRange' in kwargs.keys() else [1, 1]
        self.selection = kwargs.get('selection') if 'selection' in kwargs.keys() else False 

    def process(self):
        if self.root_node:
            # If a root node is specified, then select it and turn on
            # the selection flag
            root = pm.PyNode(self.root_node)
            pm.select(root)
            self.selection = True
            logging.info("Selecting root node for export.")

        if self.export_path == "":
            self.process_state = 1
            logging.warning("Export path wasn't specified. Using the current file's location as the export path.")
            f_path = Path(pm.sceneName())
            self.export_path = f'{f_path.parent}/{f_path.stem}.usd'

        uu.export_usd(file=self.export_path, append=self.append, convertMaterialsTo=self.convert_materials_to, defaultMeshScheme=self.default_mesh_scheme,
                      defaultUSDFormat=self.default_usd_format, frameRange=self.frame_range, selection=self.selection)
        
        self.process_state = 2


class ProcessNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Alembic Export Class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> MayaUsdExporter:
        if not self._instance:
            self._instance = MayaUsdExporter(*args, **kwds)
        return self._instance