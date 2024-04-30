#import pymel.core as pmc
from ...core.ptx_publish_factory import Publish, AssetInfo
from dataclasses import dataclass
from typing import Any, List


@dataclass
class ShaderAttributes:
    """
    * Shader Attribute data structure
    """
    attr_name: str
    attr_val: Any


@dataclass
class ShaderInfo:
    """
    * Shader information data structure
    """
    shader_name: str
    shader_attr_list: List[ShaderAttributes]
    shader_assignment: List[str]


@dataclass
class LukAssetInfo(AssetInfo):
    """
    * Overriding AssetInfo to store the map of shader assignments in this file
    """
    shader_assignment: List[ShaderInfo]


class PtxLukPublish(Publish):
    """
    * Handle Looks Publishing from Maya
    """
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.asset = LukAssetInfo(*args)

    def publish(self):
        print("Publishing luks from Maya")


class PtxLukPublishBuilder:
    """
    * Factory for Creating an instance of the Maya Looks Publish class.
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PtxLukPublish:
        if not self._instance:
            self._instance = PtxLukPublish(*args, **kwds)
        return self._instance
