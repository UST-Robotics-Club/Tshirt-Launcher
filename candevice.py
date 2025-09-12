
from abc import ABC
import time

import canmanager

class DecodedCanPacket:
    full_can_id: int
    device_id: int
    api_index: int
    api_class: int
    manuf_code: int
    device_type: int
    data: bytearray
    def __str__(self):
        return f"full 0x{self.full_can_id: X} dev {self.device_id} api_idx {hex(self.api_index)} api_class {hex(self.api_class)} manuf_code {hex(self.manuf_code)} device_type {hex(self.device_type)} data {str(self.data)}"

class CanDevice(ABC):

    def __init__(self, can_id: int):
        self.last_time_recieved = 0
        self.can_id = can_id
        canmanager.get_can_manager().add_device(self)

    def get_last_time_recieved(self):
        return self.last_time_recieved
    
    def get_can_id(self) -> int:
        return self.can_id
    
    def set_manager(self, manager: "canmanager.CanManager"):
        self.manager = manager

    def handle_packet(self, msg: DecodedCanPacket):
        """Should override this is subclass but still call super"""
        self.last_time_recieved = time.time()
