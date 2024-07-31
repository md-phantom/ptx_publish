# copyright PhantomFX 2024
from abc import ABC, abstractmethod
import importlib.util
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.WARNING)


class PhantomBaseUsdProcess(ABC):
    """
    * Abstract class to open, write and manipulate USD files
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        # Property to store the current state of the process
        # -1: The process hasn't started
        #  0: The process failed
        #  1: The process completed with warnings
        #  2: The process succeeded
        self.__process_state: int = -1

    @property
    def process_state(self):
        return self.__process_state
    
    @process_state.setter
    def process_state(self, val: int):
        if val not in range(-1, 3):
            logging.error("Supplied value is not in the range -1 to 2. Please supply a value in this range only.")

        self.__process_state = val


class PhantomUsdFactory:
    """
    * The "Factory" class to return an initialized object of the particular type of UsdType
    """
    def __init__(self) -> None:
        self._usd = dict()
        with open(f"{Path(__file__).parent}/phantom_usd_defs.conf") as file:
            self._usd = json.load(file)

    def register_usd_type(self, usd_type, prim):
        """
        * Finds the module spec specified by the proc.
        """ 
        if usd_type not in self._usd.keys():
            raise ValueError("Given USD Type type isn't registered with the system")
        
        if prim not in self._usd[usd_type].keys():
            raise ValueError("Given USD prim isn't registered with the system")
                
        return importlib.util.find_spec(".".join(['ptx_publish', 'app_modules', 'usd', usd_type, self._usd[usd_type][prim]]))

    def create(self, mod_spec, *args, **kwargs):
        """
        * Creates the object which will be called in the client method to invoke the process
        """
        if mod_spec == None:
            raise ValueError("Invalid module specified")
        
        mod = mod_spec.loader.load_module()
        NodeBuilder = mod.PhantomUsdNodeBuilder()
        return NodeBuilder(*args, **kwargs)
    

if __name__ == "__main__":
    usdf = PhantomUsdFactory()
    mat_mod_spec = usdf.register_usd_type("shaders", "aiStandardSurface")
    mat = usdf.create(mat_mod_spec, "MtlX", [])
    print(mat)