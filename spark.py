

import can
import struct

# Constants
CONTROL_SIZE = 8
HEARTBEAT_SIZE = 8
STATUS_SIZE = 2
CAN_EFF_FLAG = 0x80000000

# Enums
class ControlMode:
    Duty_Cycle_Set     = 0x2050080
    Speed_Set          = 0x2050480
    Smart_Velocity_Set = 0x20504C0
    Position_Set       = 0x2050C80
    Voltage_Set        = 0x2051080
    Current_Set        = 0x20510C0
    Smart_Motion_Set   = 0x2051480

class StatusFrameID:
    status_0 = 0x2051800
    status_1 = 0x2051840
    status_2 = 0x2051880
    status_3 = 0x20518C0
    status_4 = 0x2051900

def create_data(data, data_size, total_size):
    """Packs raw data into a byte array padded to total_size"""
    frame = bytearray(total_size)
    raw = struct.pack('<f', data)[:data_size]  # Pack float as little-endian
    frame[:len(raw)] = raw
    return frame

class Spark:
    def __init__(self, can_id):
        self.can_id = can_id
    
    def set_manager(self, manager):
        self.manager = manager

    def set_percent(self, percent):
        self.send_control_frame(ControlMode.Duty_Cycle_Set, percent)

    def send_control_frame(self, mode, setpoint):
        can_id = (mode + self.can_id) | CAN_EFF_FLAG
        data = create_data(setpoint, 4, CONTROL_SIZE)
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
        try:
            self.manager.queue_message(msg)
            #print(f"Sent control frame: ID=0x{can_id:X}, data={list(data)}")
        except can.CanError as e:
            pass
    def set_status_frame_period(self, frame_id, period):
        can_id = (frame_id + self.can_id) | CAN_EFF_FLAG
        data = struct.pack('<H', period) + bytes(STATUS_SIZE - 2)
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
        try:
            self.manager.queue_message(msg)
            #print(f"Set status frame period: ID=0x{can_id:X}, period={period}")
        except can.CanError as e:
            pass
            #print(f"Status frame period send failed: {e}")

    