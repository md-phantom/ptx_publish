# copyright PhantomFX 2024
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any
import logging
import os

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
    lock_owner: str = ""


class Publish(ABC):
    """
    * Abstract class to be used as a base class to publish a scene from a DCC software
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        # Property to store the asset information for this publish. 
        # This has to be of type AssetInfo or a sub-type of AssetInfo
        self.asset: AssetInfo
        
        # Property to store the process related information we may want to 
        # write out to a database or a file as required
        self.__publish_info__: Dict = {}

        # Property to store the current state of the process
        # -1: The process hasn't started
        #  0: The process failed
        #  1: The process completed with warnings
        #  2: The process succeeded
        self.__publish_state__: int = -1

        # Property to store the processed out file
        self.__out_file__: str = ""

    @property
    def out_file(self):
        return self.__out_file__
    
    @out_file.setter
    def out_file(self, val):
        self.__out_file__ = val

    @property
    def publish_state(self):
        return self.__publish_state__
    
    @publish_state.setter
    def publish_state(self, val: int):
        if val not in range(-1, 3):
            logging.error("Supplied value is not in the range -1 to 2. Please supply a value in this range only.")

        self.__publish_state__ = val

    @property
    def publish_info(self):
        return self.__publish_info__
    
    @publish_info.setter
    def publish_info(self, key: str, val: Any):
        self.__publish_info__[key] = val

    @abstractmethod
    def publish(self):
        """
        * Method where the core publish logic goes; this needs to be implemented anywhere
        * this class is implemented.
        """
        pass


class Activate(Publish):
    """
    * Abstract class implementation for using in the Active/Passive workflow. Derives from the Publish class.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        # Property to store the activated info
        self.__lock_info__: str = ""

    @property
    def lock_info(self):
        return self.__lock_info__
    
    @lock_info.setter
    def lock_info(self, val: str):
        self.__lock_info__ = val

    def is_asset_locked(self):
        return (self.asset.lock_owner != "")

    def publish(self):
        """
        * Empty implementation; we don't really need to re-implement this in child classes
        """
        self.make_active()
        
    @abstractmethod
    def make_active(self):
        """
        * Abstract method to implement when we want to activate an asset.
        """
        pass

    def generate_lock_info(self):
        """
        * Generate the asset lock info here. Store it in the 
        """
        self.lock_info = os.getenv("USERNAME").upper()


class Passive(Publish):
    """
    * Abstract class implementation for using in the Active/Passive workflow. Derives from the Publish class.
    """
    def publish(self):
        """
        * Empty implementation; we don't really need to re-implement this in child classes
        """
        self.make_passive()

    @abstractmethod
    def make_passive(self):
        """
        * Abstract method to implement when we want to make an asset passive in a scene.
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


if __name__ == "__main__":
    class ExamplePublish(Publish):
        def publish(self):
            print("Example Publish")

    P = ExamplePublish()
    P.publish_info[1] = {2: "val2", 3: "val3"}
    print(P.publish_info[1][2])