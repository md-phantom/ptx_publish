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

    @abstractmethod
    def process(self):
        """
        * Abstract method to run the process node
        """
        pass


class MayaExportProcessBase(MayaProcessBase):
    """
    * Abstract class to handle Maya Exporters
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__export_path:str = ''
        self.__root_node = None
        self.__frame_range = []

        self.export_path = kwargs.get('export_path') if 'export_path' in kwargs.keys() else ''
        self.root_node = kwargs.get('root_node') if 'root_node' in kwargs.keys() else None
        self.frame_range = kwargs.get('frame_range') if 'frame_range' in kwargs.keys() else [1, 1]

    @property
    def export_path(self):
        return self.__export_path
    
    @export_path.setter
    def export_path(self, val:str):
        self.__export_path = Path(val).as_posix()

    @property
    def root_node(self):
        return self.__root_node
    
    @root_node.setter
    def root_node(self, node):
        self.__root_node = node

    @property
    def frame_range(self):
        return self.__frame_range
    
    @frame_range.setter
    def frame_range(self, range:list):
        self.__frame_range = list(range)


class MayaProxyProcessBase(MayaProcessBase):
    """
    * Abstract class to handle proxies created in the scene. Adds an additional method
    * to reroute proxy paths once the files have been sent to the storage server
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__proxy_path:str = ""

        # Property to store the output we get out of this process
        # Should ideally be a PyNode
        self.__out_node: pm.PyNode = None

        self.proxy_path = kwargs.get('proxy_path') if 'proxy_path' in kwargs.keys() else ''

    @property
    def proxy_path(self):
        return self.__proxy_path
    
    @proxy_path.setter
    def proxy_path(self, val:str):
        self.__proxy_path = Path(val).as_posix()

    @property
    def out_node(self):
        return self.__out_node
    
    @out_node.setter
    def out_node(self, node):
        self.__out_node = pm.PyNode(node)
    
    @abstractmethod
    def reroute_proxy(self, new_path:str):
        pass


class MayaImportProxyProcessBase(MayaProcessBase):
    """
    * Abstract class to handle nativizing of proxy geometries in the Maya scene.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__proxy_node: pm.PyNode = None

        self.proxy_node = kwargs.get('proxy_node') if 'proxy_node' in kwargs.keys() else None

    @property
    def proxy_node(self):
        return self.__proxy_node
    
    @proxy_node.setter
    def proxy_node(self, node:pm.PyNode):
        self.__proxy_node = node


class MayaProcessFactory:
    """
    * The "Factory" class to return an initialized object of the particular type of process
    """
    def __init__(self) -> None:
        self._processes = dict()
        with open(f"{Path(__file__).parent}/maya_processes.conf") as file:
            self._processes = json.load(file)

    def register_process(self, proc_type, proc):
        """
        * Finds the module spec specified by the proc.
        """ 
        if proc_type not in self._processes.keys():
            raise ValueError("Given process type isn't registered with the system")
        
        if proc not in self._processes[proc_type].keys():
            raise ValueError("Given process isn't registered with the system")
                
        return importlib.util.find_spec(".".join(['ptx_publish', 'app_modules', 'maya', 'interchange', self._processes[proc_type][proc]]))

    def create(self, mod_spec, *args, **kwargs):
        """
        * Creates the object which will be called in the client method to invoke the process
        """
        if mod_spec == None:
            raise ValueError("Invalid module specified")
        
        mod = mod_spec.loader.load_module()
        NodeBuilder = mod.ProcessNodeBuilder()
        return NodeBuilder(*args, **kwargs)