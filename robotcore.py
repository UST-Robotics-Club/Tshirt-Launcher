from spark import Spark
from canmanager import *
import gpiozero
import time
#gpiozero.Device.pin_factory = gpiozero.pins.pigpio.PiGPIOFactory
class TShirtBot:
    def __init__(self):
        self.can_manager = get_can_manager()
        self.spark_one = Spark(5)
        self.spark_two = Spark(6)
        self.can_manager.add_device(self.spark_one)
        self.can_manager.add_device(self.spark_two)
        self.enabled = False
        self.last_ping = 0
        self.is_killed = False
        self.time_end_shoot = 0
        self.relay = gpiozero.LED(27)

    def kill_thread(self):
        self.can_manager.stop_bus()
        self.is_killed = True

    def refresh_ping(self):
        self.last_ping = time.time()
  
    def set_both(self, one, two):
        self.spark_one.set_percent(one)
        self.spark_two.set_percent(two)
    
    def pulse_shoot(self, sec):
        self.time_end_shoot = time.time() + sec
    def set_one(self, power):
        self.spark_one.set_percent(power)

    def set_two(self, power):
        self.spark_two.set_percent(power)
    
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
            
        
