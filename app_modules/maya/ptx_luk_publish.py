#import pymel.core as pmc
from ...core.ptx_publish_factory import Publish, AssetInfo
from dataclasses import dataclass
from typing import Any, List


class PtxLukPublish(Publish):
    """
    * Handle Looks Publishing from Maya
    """
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.asset = AssetInfo(*args)

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
