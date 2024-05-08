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
        self._process = kwargs.get('use_process') if 'use_process' in kwargs.keys() else 'abc'

    def make_passive(self):
        # The root is the first top node which is not in the default top level nodes
        root = [node for node in pm.ls(assemblies=True) if node not in self.__ignore_assemblies__][0]
        
        prc_factory = mpf.MayaProcessFactory()
        prc_factory.register_process("exporters", self._process)

        exporter = prc_factory.create(root_node=root)
        exporter.process()

        self.publish_state = exporter.process_state

    def reroute_proxy(self, new_path: str):
        pass


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