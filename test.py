#!/usr/bin/env python3

import os
import can
import struct
import time

os.system('sudo ip link set can0 type can bitrate 1000000')  # 1 Mbps
os.system('sudo ifconfig can0 up')

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

HEARTBEAT_ID = 0x2052C80
HEARTBEAT_DATA = [255] * HEARTBEAT_SIZE

def create_data(data, data_size, total_size):
    """Packs raw data into a byte array padded to total_size"""
    frame = bytearray(total_size)
    raw = struct.pack('<f', data)[:data_size]  # Pack float as little-endian
    frame[:len(raw)] = raw
    return frame

def send_control_frame(bus, device_id, mode, setpoint):
    can_id = (mode + device_id) | CAN_EFF_FLAG
    data = create_data(setpoint, 4, CONTROL_SIZE)
    msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
    try:
        bus.send(msg)
        print(f"Sent control frame: ID=0x{can_id:X}, data={list(data)}")
    except can.CanError as e:
        print(f"Control frame send failed: {e}")

def send_heartbeat(bus):
    can_id = HEARTBEAT_ID | CAN_EFF_FLAG
    msg = can.Message(arbitration_id=can_id, data=HEARTBEAT_DATA, is_extended_id=True)
    try:
        bus.send(msg)
        print(f"Sent heartbeat frame: ID=0x{can_id:X}")
    except can.CanError as e:
        print(f"Heartbeat send failed: {e}")

def set_status_frame_period(bus, device_id, frame_id, period):
    can_id = (frame_id + device_id) | CAN_EFF_FLAG
    data = struct.pack('<H', period) + bytes(STATUS_SIZE - 2)
    msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
    try:
        bus.send(msg)
        print(f"Set status frame period: ID=0x{can_id:X}, period={period}")
    except can.CanError as e:
        print(f"Status frame period send failed: {e}")

def main():
    bus = can.interface.Bus(channel='can0', bustype='socketcan')
    num_to_go = 0
    power = 0
    while True:
        send_heartbeat(bus)
        if num_to_go > 0:
          num_to_go -= 1
        else:
          power = 0
        send_control_frame(bus, device_id=5, mode=ControlMode.Duty_Cycle_Set, setpoint=power)
        if num_to_go <= 0:
          num_to_go = float(input("Time: ")) / 0.02
          power = float(input("Power: "))
        time.sleep(0.02)


try:
    main()
except KeyboardInterrupt:
    print("Exiting.")
finally:
    os.system('sudo ifconfig can0 down')
