from ...core.ptx_publish_factory import Publish, AssetInfo
from dataclasses import dataclass
from typing import List


@dataclass
class MdlAssetInfo(AssetInfo):
    """
    * Overriding AssetInfo to include the name of the root node, and store the list of 
    * geometries under the root node that will be exported out.
    """
    root_node: str
    geom_list: List[str]


class PtxMdlPublish(Publish):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.asset = MdlAssetInfo(*args)

    def publish(self):
        print("Publishing from Blender")


class PtxMdlPublishBuilder:
    """
    * Build an instance of the PtxMdlPublish class and return it via the __call__ method
    """
    def __init__(self) -> None:
        self._instance = None

    def __call__(self, *args, **kwds) -> PtxMdlPublish:
        if not self._instance:
            self._instance = PtxMdlPublish(*args, **kwds)
        return self._instance