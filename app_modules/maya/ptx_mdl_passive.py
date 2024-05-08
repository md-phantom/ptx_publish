import pymel.core as pm
from ...core.ptx_publish_factory import Activate, AssetInfo, Passive
from .factories import maya_process_factory as mpf
from .utils import alembic_utils as au
from dataclasses import dataclass
from typing import List
import logging
import os
from pathlib import Path


@dataclass
class MdlAssetInfo():
    """
    * Overriding AssetInfo to include the name of the root node, and store the list of 
    * geometries under the root node that will be exported out.
    """
    root_node: str
    geom_list: List[str]


class PtxMdlPassive(Passive):
    """
    * Handle making the model passive in Maya
    """
    __ignore_assemblies__ = ['persp', 'top', 'front', 'side']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.asset = AssetInfo(*args)
        self.export_path:str = kwargs.get('export_path') if 'export_path' in kwargs.keys() else ''
        self.frame_range = kwargs.get('frame_range') if 'frame_range' in kwargs.keys() else [1, 1]
        self._process = kwargs.get('use_process') if 'use_process' in kwargs.keys() else 'abc'
        self._export_default_alembic = kwargs.get('export_default_alembic') if 'export_default_alembic' in kwargs.keys() else False

        self.__exporter = None
        self.__proxy = None
        self.__fabc_exporter = None

    def make_passive(self):
        # The root is the first top node which is not in the default top level nodes
        root = [node for node in pm.ls(assemblies=True) if node not in self.__ignore_assemblies__][0]
        
        # Create the process factory
        prc_factory = mpf.MayaProcessFactory()

        # Register the export process, create the node and export 
        exp_mod = prc_factory.register_process("exporters", self._process)
        self.__exporter = prc_factory.create(exp_mod, root_node=root, export_path=self.export_path, frame_range=self.frame_range)
        self.__exporter.process()

        # Raise an error if the process state is 0
        if self.__exporter.process_state == 0:
            self.publish_state = 0
            logging.error("Publish Failed")

        # Export an alembic file as a default if we ask for it
        # make sure the default process isn't an alembic export
        if self._export_default_alembic and self._process != "abc":
            fabc_exp_mod = prc_factory.register_process("exporters", "abc")
            self.__fabc_exporter = prc_factory.create(fabc_exp_mod, export_path=self.export_path, frame_range=self.frame_range)
            self.__fabc_exporter.process()

        # Set the export path to the export path generated by the exporter
        self.export_path = self.__exporter.export_path

        # Register the proxy process, create the node and run it
        prx_mod = prc_factory.register_process("proxies", self._process)
        self.__proxy = prc_factory.create(prx_mod, proxy_path=self.export_path, use_process=self._process)
        self.__proxy.process()

        if self.__proxy.process_state > 0:
            # Delete the root node if the process state is greater than 0
            pm.delete(root)

        # Set the publish state to the minimum of the exporter and proxy process states
        self.publish_state = min(self.__exporter.process_state, self.__proxy.process_state)

    def reroute_proxy(self, new_path: str):
        self.__proxy.reroute_proxy(new_path)

    def get_force_exported_alembic_path(self)->str:
        if not self.__fabc_exporter:
            return ""
        
        return self.__fabc_exporter.export_path


class PtxNodeBuilder:
    """
    * Factory for Creating an instance of the Maya Model Activate class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PtxMdlPassive:
        if not self._instance:
            self._instance = PtxMdlPassive(*args, **kwds)
        return self._instance