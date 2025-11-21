

import can
import struct
import time
from canmanager import CanDevice, DecodedCanPacket

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

class SparkMax(CanDevice):
    def __init__(self, can_id):
        super().__init__(can_id)
        self.encoder_position = 0
        self.encoder_offset = 0
        self.max_voltage = 12
        self.status = {}

    def handle_packet(self, msg: DecodedCanPacket):
        super().handle_packet(msg)
        self.last_time_recieved = time.time()
        #if(self.can_id==6): print(str(msg))
        if msg.api_class == 0x2e:
            if msg.api_index == 2:
                self.encoder_position = struct.unpack("<f", msg.data[4:8])[0]
                #print(self.encoder_position)
                # try:
                    
                #     for d in self.status[2]:
                #        print(hex(d)[2:], end="_")
                # except:
                #     pass
        self.status[msg.api_index] = msg.data
    def get_encoder_position(self):
        """Get the encoder position, taking into account wherever it was last reset. Measured in rotations.
            If this is always returning 0, maybe the SparkMax isn't sending status frames. Check in the REV client
            for the Advanced option to force sending status frame 2.
        """
        return self.encoder_position + self.encoder_offset
    def reset_encoder_position(self):
        """Make this position be reported as 0. Only does it on this software side, not by sending a command to the Spark """
        self.encoder_offset = -self.encoder_position
        
    def set_duty_cycle(self, percent):
        """Percent should be between -1 and 1"""
        self.send_control_frame(ControlMode.Duty_Cycle_Set, percent)

    def set_proportion_volts(self, proportion):
        """Set the output of the spark in volts, as a proportion of the configured max voltage (default 12v)"""
        self.send_control_frame(ControlMode.Voltage_Set, self.max_voltage * proportion)

    def set_max_voltage(self, volts):
        """Sets the reference voltage that will be used in set_proportion_volts"""
        self.max_voltage = volts

    def set_position(self, position):
        """Position is expressed in rotations"""
        self.send_control_frame(ControlMode.Position_Set, position)

    def send_control_frame(self, mode, setpoint):
        can_id = (mode + self.can_id) | CAN_EFF_FLAG
        data = create_data(setpoint, 4, CONTROL_SIZE)
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
        try:
            self.manager.queue_message(msg)
            #print(f"Sent control frame: ID=0x{can_id:X}, data={list(data)}")
        except can.CanError as e:
            pass
    def blink_led(self):
        """doesn't work"""
        can_id = (0x2051D80 + self.can_id) | CAN_EFF_FLAG
        msg = can.Message(arbitration_id=can_id, is_extended_id=True)
        try:
            self.manager.queue_message(msg)
            print(f"Sent blink frame: ID=0x{can_id:X}")
        except can.CanError as e:
            pass
    def clear_faults(self):
        """Does work. Clears sticky faults"""
        can_id = (0x2051B80 + self.can_id) | CAN_EFF_FLAG
        msg = can.Message(arbitration_id=can_id, is_extended_id=True)
        try:
            self.manager.queue_message(msg)
            print(f"Sent clear frame: ID=0x{can_id:X}")
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

    
