from spark import Spark
from canmanager import *
import gpiozero
import time
#gpiozero.Device.pin_factory = gpiozero.pins.pigpio.PiGPIOFactory
class TShirtBot:
    def __init__(self):
        self.can_manager = get_can_manager()
        self.rotate_barrel = Spark(5)
        self.tilter = Spark(6)
        self.front_left = Spark(10)
        self.back_left = Spark(11)
        self.front_right = Spark(12)
        self.back_right = Spark(13)
        self.can_manager.add_device(self.rotate_barrel)
        self.can_manager.add_device(self.tilter)
        self.can_manager.add_device(self.front_left)
        self.can_manager.add_device(self.front_right)
        self.can_manager.add_device(self.back_left)
        self.can_manager.add_device(self.back_right)
        self.enabled = False
        self.last_ping = 0
        self.is_killed = False
        self.time_end_shoot = 0

    def kill_thread(self):
        self.can_manager.stop_bus()
        self.is_killed = True

    def refresh_ping(self):
        self.last_ping = time.time()


    def forward(self):
        self.front_left.set_percent(.1)
        self.front_right.set_percent(-.1)
        self.back_left.set_percent(.1)
        print("I am going forwards")
        self.back_right.set_percent(-.1)

    def backward(self):
        self.front_left.set_percent(-.1)
        self.front_right.set_percent(.1)
        self.back_left.set_percent(-.1)
        self.back_right.set_percent(.1)

    def turn_left(self):
        self.front_left.set_percent(-.1)
        self.front_right.set_percent(-.1)
        self.back_left.set_percent(-.1)
        self.back_right.set_percent(-.1)

    def turn_right(self):
        self.front_left.set_percent(.1)
        self.front_right.set_percent(.1)
        self.back_left.set_percent(.1)
        self.back_right.set_percent(.1)
    def disable_drivetrain(self):
        self.front_left.set_percent(0)
        self.front_right.set_percent(0)
        self.back_left.set_percent(0)
        self.back_right.set_percent(0)

    def tilt_up(self):
        self.tilter.set_percent(.1)
    def tilt_down(self):
        self.tilter.set_percent(-.1)
    def rotate(self):
        self.rotate_barrel.set_percent(.1)
    def stop_turret(self):
        self.rotate_barrel.set_percent(0)
        self.tilter.set_percent(0)

    def set_enabled(self, enabled):
        print("Enabled: ", enabled)
        self.enabled = enabled
        self.can_manager.set_heartbeat(enabled)
        
    def get_enabled(self):
        return self.enabled
    
    def tick(self):
        now = time.time()
        if now - self.last_ping > 1 and self.enabled:
            self.set_enabled(False)

        time.sleep(0.02)
    
    def main_loop(self):
        self.can_manager.start_thread()
        while not self.is_killed:
            self.tick()
            
        
