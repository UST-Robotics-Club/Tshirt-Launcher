import os
import can
import struct
import time
import threading

HEARTBEAT_ID = 0x2052C80
HEARTBEAT_SIZE = 8
HEARTBEAT_DATA = [255] * HEARTBEAT_SIZE
CAN_EFF_FLAG = 0x80000000

class CanManager:
    def __init__(self):
        self.devices = []
        os.system('sudo ip link set can0 type can bitrate 1000000')  # 1 Mbps
        os.system('sudo ifconfig can0 up')
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')

    def add_device(self, device):
        self.devices.append(device)
        device.set_bus(self.bus)
    def send_heartbeat(self):
        can_id = HEARTBEAT_ID | CAN_EFF_FLAG
        msg = can.Message(arbitration_id=can_id, data=HEARTBEAT_DATA, is_extended_id=True)
        try:
            self.bus.send(msg)
            #print(f"Sent heartbeat frame: ID=0x{can_id:X}")
        except can.CanError as e:
            pass
            #print(f"Heartbeat send failed: {e}")

    def main_loop(self):
        os.system('sudo ip link set can0 type can bitrate 1000000')  # 1 Mbps
        os.system('sudo ifconfig can0 up')
        try:
            while True:
                self.send_heartbeat()
                time.sleep(0.02)
        finally:
            os.system('sudo ifconfig can0 down')
            
    def start_thread(self):
        t = threading.Thread(target = self.main_loop)
        t.start()
        self.thread = t

        
