import pymel.core as pm
from ...core.ptx_publish_factory import Publish
from .factories import maya_process_factory as mpf

import logging


class PtxExportWorkScene(Publish):
    """
    * Handle making the model passive in Maya
    """
    __ignore_assemblies__ = ['persp', 'top', 'front', 'side']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.export_path:str = kwargs.get('export_path') if 'export_path' in kwargs.keys() else ''
        self.frame_range = kwargs.get('frame_range') if 'frame_range' in kwargs.keys() else [1, 1]
        self._process = kwargs.get('use_process') if 'use_process' in kwargs.keys() else 'mayaAscii'
        self._nodes_to_select = kwargs.get('nodes_to_select') if 'nodes_to_select' in kwargs.keys() else [node for node in pm.ls(assemblies=True) if node not in self.__ignore_assemblies__]

        self.__exporter = None

    def publish(self):        
        # Create the process factory
        prc_factory = mpf.MayaProcessFactory()
        # Register the export process, create the node and export 
        exp_mod = prc_factory.register_process("exporters", "mae")

        self.__exporter = prc_factory.create(exp_mod, export_path=self.export_path, force=True, maya_file_type=self._process, selection_only=(len(self._nodes_to_select)==0))
        self.__exporter.process()

        # Raise an error if the process state is 0
        if self.__exporter.process_state == 0:
            self.publish_state = 0
            logging.error("Publish Failed")

        # Set the export path to the export path generated by the exporter
        self.export_path = self.__exporter.export_path

        self.publish_state = self.__exporter.process_state

    def reroute_proxy(self, new_path: str):
        pass


class PtxNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Model Activate class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PtxExportWorkScene:
        if not self._instance:
            self._instance = PtxExportWorkScene(*args, **kwds)
        return self._instance