# copyright PhantomFX 2024
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.WARNING)

@dataclass
class AssetInfo:
    """
    * Consider this to be a C/C++ type struct to store asset attributes
    * Can be overridden on a per process level to include more info as required
    """
    asset_name: str
    asset_type: str
    asset_process: str
    asset_version: str


class Publish(ABC):
    """
    * Abstract class to be used as a base class to publish a scene from a DCC software
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        # Variable to store the asset information for this publish. 
        # This has to be of type AssetInfo or a sub-type of AssetInfo
        self.asset: AssetInfo

    @abstractmethod
    def publish(self):
        """
        * Method where the core publish logic goes; this needs to be implemented anywhere
        * this class is implemented.
        """
        pass


class PtxPublishFactory:
    """
    * The "Factory" class to return an initialized object of the particular type of publish
    """
    def __init__(self) -> None:
        self._apps = dict()

    def register_app(self, app, pub_type, pub_method):
        """
        * Registers the application as the key, and the publish object as the app.
        * Maintains a dictionary of the apps and the list of associated publish methods
        """
        if app not in self._apps.keys():
            self._apps[app] = dict()
        self._apps[app][pub_type] = pub_method

    def create(self, app, pub_type, *args, **kwargs):
        """
        * Creates the object which will be called in the client method to invoke the publish
        """
        p_app = self._apps.get(app).get(pub_type)
        if not p_app:
            raise ValueError(pub_type)
        return p_app(*args, **kwargs)

