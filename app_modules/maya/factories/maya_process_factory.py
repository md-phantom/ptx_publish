# copyright PhantomFX 2024
from abc import ABC, abstractmethod
import logging
import json
from pathlib import Path
import importlib.util

import pymel.core as pm

logging.basicConfig(level=logging.WARNING)


class MayaProcessBase(ABC):
    """
    * Abstract class to define a Maya Process Node
    """
    def __init__(self, *args, **kwargs) -> None:
        super(*args, **kwargs).__init__()

        # Property to store the output we get out of this process
        # Should ideally be a PyNode
        self.__out_node: pm.PyNode = None

        # Property to store the current state of the process
        # -1: The process hasn't started
        #  0: The process failed
        #  1: The process completed with warnings
        #  2: The process succeeded
        self.__process_state: int = -1

    @property
    def out_node(self):
        return self.__out_node
    
    @out_node.setter
    def out_node(self, node):
        self.__out_node = pm.PyNode(node)

    @property
    def process_state(self):
        return self.__process_state
    
    @process_state.setter
    def process_state(self, val: int):
        if val not in range(-1, 3):
            logging.error("Supplied value is not in the range -1 to 2. Please supply a value in this range only.")

        self.__process_state = val

    @abstractmethod
    def process(self):
        """
        * Abstract method to run the process node
        """
        pass


class MayaProcessFactory:
    """
    * The "Factory" class to return an initialized object of the particular type of process
    """
    def __init__(self) -> None:
        self._processes = dict()
        self._mod_spec = None
        with open(f"{Path(__file__).parent}/maya_processes.conf") as file:
            self._processes = json.load(file)

    def register_process(self, proc):
        """
        * Finds the module spec specified by the proc.
        """ 
        if proc not in self._processes.keys():
            raise ValueError("Given application isn't registered with the system")
                
        self._mod_spec = importlib.util.find_spec(".".join(['ptx_publish', 'app_modules', 'maya', 'interchange', self._processes[proc]]))

    def create(self, *args, **kwargs):
        """
        * Creates the object which will be called in the client method to invoke the process
        """
        if self._mod_spec == None:
            raise ValueError("Invalid module specified")
        
        mod = self._mod_spec.loader.load_module()
        NodeBuilder = mod.ProcessNodeBuilder()
        return NodeBuilder(*args, **kwargs)