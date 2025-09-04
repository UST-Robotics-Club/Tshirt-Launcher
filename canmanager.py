from abc import ABC, abstractmethod
import os, io
import can
import struct
import time
import threading
from queue import Queue
HEARTBEAT_ID = 0x2052C80
HEARTBEAT_SIZE = 8

HEARTBEAT_DATA = [255] * HEARTBEAT_SIZE
CAN_EFF_FLAG = 0x80000000

class DecodedCanPacket:
    device_id: int
    api_index: int
    api_class: int
    manuf_code: int
    device_type: int
    def __str__(self):
        return f"dev {self.device_id} api_idx {hex(self.api_index)} api_class {hex(self.api_class)} manuf_code {hex(self.manuf_code)} device_type {hex(self.device_type)}"

class CanDevice(ABC):
    @abstractmethod
    def get_can_id(self) -> int:
        pass

    @abstractmethod
    def handle_packet(self, msg: DecodedCanPacket):
        pass

class CanManager:
    def __init__(self):
        self.devices: dict[int, CanDevice] = {}
        self.bus = None
        self.is_killed = False
        self.write_queue: Queue[can.Message] = Queue()
    def add_device(self, device: CanDevice):
        self.devices[device.get_can_id()] = device
        device.set_manager(self)

    def queue_message(self, message: can.Message):
        self.write_queue.put(message)

    def start_heartbeat(self):
        can_id = HEARTBEAT_ID | CAN_EFF_FLAG
        msg = can.Message(arbitration_id=can_id, data=HEARTBEAT_DATA, is_extended_id=True)
        try:
            self.heartbeat = self.bus.send_periodic(msg, 0.02)
            print(f"Sent heartbeat frame: ID=0x{can_id:X}")
        except can.CanError as e:
            print(f"Heartbeat send failed: {e}")

    def read_loop(self):
        try:
            last = 0
            while not self.is_killed:
                msg = self.bus.recv()
                decoded = DecodedCanPacket()
                decoded.device_id =   (0b00000000000000000000000111111 & msg.arbitration_id)
                decoded.api_index =   (0b00000000000000000001111000000 & msg.arbitration_id) >> 6
                decoded.api_class =   (0b00000000000001111110000000000 & msg.arbitration_id) >> 10
                decoded.manuf_code =  (0b00000111111110000000000000000 & msg.arbitration_id) >> 16
                decoded.device_type =  (0b11111000000000000000000000000 & msg.arbitration_id) >> 24
                if decoded.device_id in self.devices:
                    self.devices[decoded.device_id].handle_packet(decoded)
                if time.time() - last > 1:
                    #print(str(decoded))
                    #print("full", hex(msg.arbitration_id), bin(msg.arbitration_id))
                    last = time.time()
                #time.sleep(1)
        except Exception as e:
            print("Read err: ", str(e))
    def write_loop(self):
        try:
            while not self.is_killed:
                msg = self.write_queue.get()
                try:
                    self.bus.send(msg)
                except can.CanError as e:
                    print(e)
        except Exception as e:
            print("WRITE ERRR!!!", str(e))
    def start_thread(self):
        os.system('sudo ifconfig can0 down')
        os.system('sudo ip link set can0 type can bitrate 1000000')  # 1 Mbps
        os.system('sudo ifconfig can0 up')
        self.bus = can.interface.Bus(channel='can0', interface='socketcan', bitrate=1000000)
        self.start_heartbeat()
        self.t1 = threading.Thread(target = self.write_loop)
        self.t1.start()
        self.t2 = threading.Thread(target = self.read_loop)
        self.t2.start()
    def set_heartbeat(self, enabled):
        try:
            self.heartbeat.stop()
        except can.exceptions.CanError:
            pass
        if enabled:
            self.start_heartbeat()
    def stop_bus(self):
        self.bus.stop_all_periodic_tasks()
        self.is_killed = True
        #os.system('sudo ifconfig can0 down')

class FakeCanManager(CanManager):
    def __init__(self):
        self.devices = {}
        self.bus = None
        self.write_queue: Queue[can.Message] = Queue()

    def set_heartbeat(self, enabled):
        pass

    def start_thread(self):
        pass

    def stop_bus(self):
        self.is_killed = True

    def queue_message(self, message: can.Message):
        pass
        #print(bin(message.arbitration_id), bin(int.from_bytes(message.data, 'big')))


def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

def get_can_manager():
    """Returns either a real or mock CanManager depending on if the code is actually running on a Pi"""
    if is_raspberrypi():
        return CanManager()
    else:
        return FakeCanManager()