# copyright PhantomFX 2024
from abc import ABC, abstractmethod
import logging
import json
from pxr import Usd, Sdf, UsdAbc

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