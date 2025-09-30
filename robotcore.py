from spark import SparkMax
from canmanager import *
import gpiozero
import time
import fakes
gpiozero.Device.pin_factory = gpiozero.pins.pigpio.PiGPIOFactory
class TShirtBot:
    def __init__(self):
        self.can_manager = get_can_manager()
        self.rotate_barrel = SparkMax(6)
        self.tilter = SparkMax(5)
        self.front_left = SparkMax(15)
        self.back_left = SparkMax(12)
        self.front_right = SparkMax(11)
        self.back_right = SparkMax(10)
        #self.test_spark = SparkMax(16)
        self.enabled = False
        self.last_ping = 0
        self.is_killed = False
        self.time_end_shoot = 0
        self.shooting = True
        self.requested_left = 0
        self.requested_right = 0
        self.time_end_shoot = 0
        self.relay = gpiozero.LED(27) if fakes.is_raspberrypi() else fakes.FakeRelay()

    def kill_thread(self):
        self.can_manager.stop_bus()
        self.is_killed = True

    def refresh_ping(self):
        self.last_ping = time.time()

    def forward(self):
        self.front_left.set_duty_cycle(.1)
        self.front_right.set_duty_cycle(-.1)
        self.back_left.set_duty_cycle(.1)
        self.back_right.set_duty_cycle(-.1)

    def backward(self):
        self.front_left.set_duty_cycle(-.1)
        self.front_right.set_duty_cycle(.1)
        self.back_left.set_duty_cycle(-.1)
        self.back_right.set_duty_cycle(.1)

    def turn_left(self):
        self.front_left.set_duty_cycle(-.1)
        self.front_right.set_duty_cycle(-.1)
        self.back_left.set_duty_cycle(-.1)
        self.back_right.set_duty_cycle(-.1)

    def turn_right(self):
        self.front_left.set_duty_cycle(.1)
        self.front_right.set_duty_cycle(.1)
        self.back_left.set_duty_cycle(.1)
        self.back_right.set_duty_cycle(.1)
    def set_shooting(self, shooting):
        self.shooting = shooting
    def pulse_shoot(self, sec):
        self.time_end_shoot = time.time() + sec
        #self.test_spark.set_duty_cycle(sec)
    def drive(self, forward: float, counterclockwise: float):
        right = forward - counterclockwise
        left = forward + counterclockwise
        if max(abs(right), abs(left)) > 1: # normalize if trying to go over 100%
            norm_factor = 1 / max(abs(right), abs(left))
            right *= norm_factor
            left *= norm_factor
        
        # print("r", right, ", l", left)
        self.requested_left = left
        self.requested_right = right

    def disable_drivetrain(self):
        self.front_left.set_duty_cycle(0)
        self.front_right.set_duty_cycle(0)
        self.back_left.set_duty_cycle(0)
        self.back_right.set_duty_cycle(0)

    def tilt_up(self):
        self.tilter.set_duty_cycle(-0.1)
    def tilt_down(self):
        self.tilter.set_duty_cycle(0.1)
    def rotate(self):
        self.rotate_barrel.set_duty_cycle(.1)
    def stop_turret(self):
        self.rotate_barrel.set_duty_cycle(0)
        self.tilter.set_duty_cycle(0)
    def hold(self):
        self.tilter.set_duty_cycle(.05)

    def set_enabled(self, enabled):
        print("Enabled: ", enabled)
        self.enabled = enabled
        self.can_manager.set_heartbeat(enabled)
        if not enabled:
            self.drive(0, 0)
            self.set_shooting(False)
        
    def get_enabled(self):
        return self.enabled
    def get_status_info(self):
        """Return whatever should be sent to the frontend every 0.75 sec"""
        return [self.get_enabled()]
    def tick(self):
        now = time.time()
        if now - self.last_ping > 1 and self.enabled:
            self.set_enabled(False)
        if self.enabled:
            self.front_left.set_duty_cycle(self.requested_left)
            self.back_left.set_duty_cycle(self.requested_left)

            self.front_right.set_duty_cycle(-self.requested_right)
            self.back_right.set_duty_cycle(-self.requested_right)

            if self.shooting:
                pass
        if now <= self.time_end_shoot:
        #print("on")
            self.relay.on()
        else:
            #print("off")

            self.relay.off()
        time.sleep(0.02)
    
    def main_loop(self):
        self.can_manager.start_thread()
        while not self.is_killed:
            self.tick()
        
